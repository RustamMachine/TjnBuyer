import time
import os
import sys
import random
import mss
import cv2
import ctypes
import numpy as np
import logging
from contextlib import contextmanager
from colorama import Fore, Style

import config.config as config
import config.mods_config as mods_config

# Импорты подсистем
from core.inventory_manager import InventoryManager, ItemStatus
from core.input_handler import human_click, copy_item_data, release_all_modifiers, smooth_move
from perception.item_scanner import ItemScanner
from perception.ocr_engine import OCREngine
from perception.shopping_vision import get_occupied_inventory_slots
from logic.matchmaker import Matchmaker

# Константы
SCAN_DELAY = 0.04
CRAFT_ANIMATION_DURATION = 6.0
MOUSE_SETTLE_TIME = 0.15
SAFE_ZONE_MOVE_SPEED = 5.0
POST_CRAFT_WAIT = 0.3
MOD_SELECTION_DELAY = 0.1
RESULT_SLOT_SAMPLE_SIZE = 10

# Настройка логирования
logger = logging.getLogger(__name__)


class RecombinatorExecutor:
    def __init__(self):
        self.manager = InventoryManager()
        self.scanner = ItemScanner(self.manager)
        self.matchmaker = Matchmaker()
        self.ocr = OCREngine()
        
        user32 = ctypes.windll.user32
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)
        
        self._validate_config()
        
    def _validate_config(self):
        required_attrs = [
            'PLAYER_INVENTORY_GRID',
            'RECOMB_ITEM_A_ROI',
            'RECOMB_ITEM_B_ROI',
            'RECOMB_BTN_COMBINE_COORDS',
            'RECOMB_OUTPUT_SLOT',
            'RECOMB_INPUT_SLOT_A',
            'RECOMB_INPUT_SLOT_B',
            'RECOMB_FAIL_MSG_ROI',
            'RECOMB_RESULT_BRIGHTNESS_THRESHOLD'
        ]
        for attr in required_attrs:
            if not hasattr(config, attr):
                raise ValueError(f"Missing required config attribute: {attr}")
    
    @contextmanager
    def safe_mouse_position(self):
        try:
            yield
        finally:
            self._move_to_safe_zone()
        
    def _move_to_safe_zone(self):
        target_x = self.screen_width - 1
        target_y = self.screen_height // 2 + random.randint(-100, 100)
        smooth_move(target_x, target_y, speed_mult=SAFE_ZONE_MOVE_SPEED)
        time.sleep(MOUSE_SETTLE_TIME)

    def scan_player_inventory(self):
        print(f"{Fore.YELLOW}[EXECUTOR] Vision Scan (Check empty slots)...{Style.RESET_ALL}")
        
        try:
            occupied_indices = get_occupied_inventory_slots()
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to get occupied slots: {e}{Style.RESET_ALL}")
            logger.exception("Vision scan failed")
            return False
        
        if not occupied_indices:
            print(f"{Fore.YELLOW}[EXECUTOR] Inventory appears empty (Vision).{Style.RESET_ALL}")
            return True

        print(f"{Fore.YELLOW}[EXECUTOR] Detailed Scan of {len(occupied_indices)} items...{Style.RESET_ALL}")
        release_all_modifiers()

        for i in occupied_indices:
            if i < 0 or i >= len(config.PLAYER_INVENTORY_GRID):
                continue

            item = self.manager.get_item(i)
            if item and (item.status == ItemStatus.LOCKED or item.status == ItemStatus.OCR_ERROR):
                continue

            coords = config.PLAYER_INVENTORY_GRID[i]
            try:
                smooth_move(coords[0], coords[1])
                time.sleep(SCAN_DELAY)
                raw_text = copy_item_data()
                self.scanner.scan_slot_text(raw_text, i)
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Scan failed for slot {i}: {e}{Style.RESET_ALL}")
                continue
            
        release_all_modifiers()
        print("[EXECUTOR] Scan complete. Moving mouse to safe zone.")
        self._move_to_safe_zone()
        return True

    def execute_cycle(self):
        try:
            # 1. СКАНИРОВАНИЕ
            # Проводим сканирование только ОДИН раз перед началом обработки всей очереди
            scan_success = self.scan_player_inventory()
            if not scan_success:
                print(f"{Fore.RED}[EXECUTOR] Scan failed. Retrying next cycle...{Style.RESET_ALL}")
                return False
            
            # 2. СОЗДАНИЕ ОЧЕРЕДИ
            candidates = self.manager.get_crafting_candidates()
            queue = self.matchmaker.create_crafting_queue(candidates)
            
            # Если пар нет — закрываемся (работа выполнена)
            if not queue:
                print(f"{Fore.RED}[EXECUTOR] No valid pairs found.{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}=========================================={Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}[SYSTEM] Job Finished! Shutting down...{Style.RESET_ALL}")
                print(f"{Fore.MAGENTA}=========================================={Style.RESET_ALL}")
                sys.exit(0)

            print(f"{Fore.GREEN}[EXECUTOR] Processing {len(queue)} pairs...{Style.RESET_ALL}")
            
            # 3. ОБРАБОТКА ОЧЕРЕДИ
            # Проходим по ВСЕМ парам, найденным матчмейкером
            for pair in queue:
                try:
                    self._process_pair(pair)
                except Exception as e:
                    print(f"{Fore.RED}[ERROR] Failed to process pair: {e}{Style.RESET_ALL}")
                    logger.exception("Pair processing failed")
                    # Если пара упала с ошибкой, идем к следующей, не прерывая весь цикл
                    continue
            
            # 4. ЗАВЕРШЕНИЕ ЦИКЛА
            # ВАЖНО: return True стоит ЗДЕСЬ (вне цикла for),
            # чтобы сообщить main.py, что мы закончили работать со списком и готовы к новому сканированию.
            return True

        except SystemExit:
            raise
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Execute cycle failed: {e}{Style.RESET_ALL}")
            logger.exception("Execute cycle crashed")
            return False

    def _process_pair(self, pair):
        part_a, part_b = pair
        item_a, tags_a = part_a
        item_b, tags_b = part_b
        
        print(f"\n{Fore.CYAN}>>> Crafting Pair: Slot {item_a.slot_index} + Slot {item_b.slot_index}{Style.RESET_ALL}")
        
        self.manager.lock_item(item_a.slot_index)
        self.manager.lock_item(item_b.slot_index)
        
        try:
            # 1. Загрузка
            human_click(config.PLAYER_INVENTORY_GRID[item_a.slot_index], key_modifier="ctrl")
            time.sleep(MOUSE_SETTLE_TIME)
            human_click(config.PLAYER_INVENTORY_GRID[item_b.slot_index], key_modifier="ctrl")
            
            time.sleep(0.1)
            time.sleep(POST_CRAFT_WAIT)
            
            # 2. Скриншот
            with mss.mss() as sct:
                screenshot = np.array(sct.grab(sct.monitors[1]))
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

            # 3. Выбор модов
            success_a = self._select_mods(screenshot, config.RECOMB_ITEM_A_ROI, tags_a, item_a.item_class)
            if not success_a:
                print(f"{Fore.RED}[ABORT] Failed to find mods for Item A. Aborting craft.{Style.RESET_ALL}")
                self._abort_craft_process(item_a.slot_index, item_b.slot_index)
                return

            success_b = self._select_mods(screenshot, config.RECOMB_ITEM_B_ROI, tags_b, item_b.item_class)
            if not success_b:
                print(f"{Fore.RED}[ABORT] Failed to find mods for Item B. Aborting craft.{Style.RESET_ALL}")
                self._abort_craft_process(item_a.slot_index, item_b.slot_index)
                return
            
            # 4. Combine
            print("[EXECUTOR] Clicking Combine...")
            
            combine_coords = config.RECOMB_BTN_COMBINE_COORDS
            if len(combine_coords) == 4:
                target_click = ((combine_coords[0] + combine_coords[2]) // 2, (combine_coords[1] + combine_coords[3]) // 2)
            else:
                target_click = tuple(combine_coords)
            
            human_click(target_click)
            print(f"[EXECUTOR] Waiting for animation ({CRAFT_ANIMATION_DURATION}s)...")
            time.sleep(CRAFT_ANIMATION_DURATION)
            
            self._check_result_and_cleanup(item_a.slot_index, item_b.slot_index)
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Process pair failed: {e}{Style.RESET_ALL}")
            self.manager.unlock_item(item_a.slot_index)
            self.manager.unlock_item(item_b.slot_index)
            raise

    def _abort_craft_process(self, slot_a_idx, slot_b_idx):
        print(f"{Fore.YELLOW}[EXECUTOR] Retrieving items from Recombinator...{Style.RESET_ALL}")
        human_click(config.RECOMB_INPUT_SLOT_A, key_modifier="ctrl")
        time.sleep(0.2)
        human_click(config.RECOMB_INPUT_SLOT_B, key_modifier="ctrl")
        time.sleep(0.2)
        self.manager.mark_as_error(slot_a_idx)
        self.manager.mark_as_error(slot_b_idx)
        print(f"{Fore.MAGENTA}[MANAGER] Items marked as OCR_ERROR.{Style.RESET_ALL}")

    def _check_result_and_cleanup(self, slot_a_idx, slot_b_idx):
        should_remove_items = False

        try:
            with mss.mss() as sct:
                screen = np.array(sct.grab(sct.monitors[1]))
                screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Screenshot failed: {e}{Style.RESET_ALL}")
            return
        
        try:
            fail_crop = self.ocr.crop_image(screen, config.RECOMB_FAIL_MSG_ROI)
            coords_fail = self.ocr.find_text_coordinates(
                fail_crop, "Failed", 
                offset=(config.RECOMB_FAIL_MSG_ROI[0], config.RECOMB_FAIL_MSG_ROI[1])
            )
            if coords_fail:
                print(f"{Fore.MAGENTA}[RESULT] BROKEN! (Found 'Failed' text){Style.RESET_ALL}")
                should_remove_items = True
        except Exception:
            pass

        if not should_remove_items:
            try:
                cx, cy = config.RECOMB_OUTPUT_SLOT
                half = RESULT_SLOT_SAMPLE_SIZE
                if cy-half >= 0 and cy+half < screen.shape[0] and cx-half >= 0 and cx+half < screen.shape[1]:
                    result_slot_crop = screen[cy-half:cy+half, cx-half:cx+half]
                    gray_crop = cv2.cvtColor(result_slot_crop, cv2.COLOR_BGR2GRAY)
                    avg_brightness = np.mean(gray_crop)

                    if avg_brightness > config.RECOMB_RESULT_BRIGHTNESS_THRESHOLD:
                        print(f"{Fore.GREEN}[RESULT] SUCCESS! (brightness: {avg_brightness:.1f}){Style.RESET_ALL}")
                        human_click(config.RECOMB_OUTPUT_SLOT, key_modifier="ctrl")
                        time.sleep(POST_CRAFT_WAIT)
                        should_remove_items = True
                    else:
                        print(f"{Fore.MAGENTA}[RESULT] BROKEN! (Empty, brightness: {avg_brightness:.1f}){Style.RESET_ALL}")
                        should_remove_items = True
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Brightness check: {e}{Style.RESET_ALL}")

        if should_remove_items:
            self.manager.remove_item(slot_a_idx)
            self.manager.remove_item(slot_b_idx)

    def _select_mods(self, full_screenshot, roi, wanted_tags, item_class):
        try:
            crop = self.ocr.crop_image(full_screenshot, roi)
        except Exception:
            return False
        
        all_found = True
        
        for tag in wanted_tags:
            # ТЕПЕРЬ ПОЛУЧАЕМ СПИСОК ВОЗМОЖНЫХ СТРОК (например, ["47 to Spirit", "48 to Spirit"])
            text_variants = self._get_text_list_for_tag(item_class, tag)
            
            if not text_variants:
                if config.DETAILED_LOGGING:
                    print(f"   [OCR] No text mapping found for tag '{tag}'")
                continue

            tag_found = False
            
            # Пробуем каждый вариант текста, пока не найдем
            for target_text in text_variants:
                if config.DETAILED_LOGGING:
                    print(f"   [OCR] Looking for '{target_text}' (Tag: {tag})")
                
                try:
                    coords = self.ocr.find_text_coordinates(
                        crop, 
                        target_text, 
                        offset=(roi[0], roi[1])
                    )
                    
                    if coords:
                        gx, gy = coords
                        print(f"   -> Found '{tag}' via '{target_text}'. Clicking ({gx}, {gy})")
                        human_click((gx, gy))
                        time.sleep(MOD_SELECTION_DELAY)
                        tag_found = True
                        break # Выходим из внутреннего цикла, переходим к следующему тегу
                except Exception as e:
                    print(f"{Fore.RED}[ERROR] OCR check failed: {e}{Style.RESET_ALL}")
            
            if not tag_found:
                print(f"{Fore.RED}   -> Missed '{tag}' (Tried {len(text_variants)} variants){Style.RESET_ALL}")
                all_found = False
                break 
        
        return all_found

    def _get_text_list_for_tag(self, item_class, tag):
        """
        Возвращает СПИСОК всех строк, которые соответствуют данному тегу.
        Нужно для случаев, когда один тег (Spirit) может быть описан разными строками (47 to Spirit, 48 to Spirit...).
        """
        variants = []
        class_config = mods_config.WANTED_MODS_BY_CLASS.get(item_class, {})
        for group, mappings in class_config.items():
            for text_key, tag_val in mappings.items():
                if tag_val == tag:
                    variants.append(text_key)
        return variants