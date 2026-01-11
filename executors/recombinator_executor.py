import time
import os
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
        """Валидация критических параметров конфигурации"""
        required_attrs = [
            'PLAYER_INVENTORY_GRID',
            'RECOMB_ITEM_A_ROI',
            'RECOMB_ITEM_B_ROI',
            'RECOMB_BTN_COMBINE_COORDS',
            'RECOMB_OUTPUT_SLOT',
            'RECOMB_FAIL_MSG_ROI',
            'RECOMB_RESULT_BRIGHTNESS_THRESHOLD'
        ]
        
        for attr in required_attrs:
            if not hasattr(config, attr):
                raise ValueError(f"Missing required config attribute: {attr}")
    
    @contextmanager
    def safe_mouse_position(self):
        """Гарантирует возврат мыши в безопасную зону после операций"""
        try:
            yield
        finally:
            self._move_to_safe_zone()
        
    def _move_to_safe_zone(self):
        """
        Быстрый и плавный увод мыши ЗА край экрана.
        """
        target_x = self.screen_width - 1
        target_y = self.screen_height // 2 + random.randint(-100, 100)
        
        smooth_move(target_x, target_y, speed_mult=SAFE_ZONE_MOVE_SPEED)
        time.sleep(MOUSE_SETTLE_TIME)

    def scan_player_inventory(self):
        """
        Оптимизированное сканирование инвентаря.
        """
        print(f"{Fore.YELLOW}[EXECUTOR] Vision Scan (Check empty slots)...{Style.RESET_ALL}")
        
        try:
            occupied_indices = get_occupied_inventory_slots()
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to get occupied slots: {e}{Style.RESET_ALL}")
            logger.exception("Vision scan failed")
            return
        
        if not occupied_indices:
            print(f"{Fore.YELLOW}[EXECUTOR] Inventory appears empty (Vision).{Style.RESET_ALL}")
            return

        print(f"{Fore.YELLOW}[EXECUTOR] Detailed Scan of {len(occupied_indices)} items...{Style.RESET_ALL}")
        
        release_all_modifiers()

        for i in occupied_indices:
            # ФИКС: Проверяем существование координат для слота
            if i not in config.PLAYER_INVENTORY_GRID:
                print(f"{Fore.RED}[ERROR] Invalid slot index: {i} (not in grid){Style.RESET_ALL}")
                logger.error(f"Slot {i} not found in PLAYER_INVENTORY_GRID")
                continue
            
            item = self.manager.get_item(i)
            
            # ФИКС: Пропускаем locked И несуществующие предметы
            if not item or item.status == ItemStatus.LOCKED:
                continue

            coords = config.PLAYER_INVENTORY_GRID[i]
            
            try:
                smooth_move(coords[0], coords[1])
                time.sleep(SCAN_DELAY)
                raw_text = copy_item_data()
                self.scanner.scan_slot_text(raw_text, i)
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Scan failed for slot {i}: {e}{Style.RESET_ALL}")
                logger.exception(f"Failed to scan slot {i}")
                continue
            
        release_all_modifiers()

        print("[EXECUTOR] Scan complete. Moving mouse to safe zone.")
        self._move_to_safe_zone()

    def execute_cycle(self):
        """
        Главный метод цикла крафта.
        """
        try:
            self.scan_player_inventory()
            
            candidates = self.manager.get_crafting_candidates()
            queue = self.matchmaker.create_crafting_queue(candidates)
            
            if not queue:
                print(f"{Fore.RED}[EXECUTOR] No valid pairs found.{Style.RESET_ALL}")
                return False

            print(f"{Fore.GREEN}[EXECUTOR] Processing {len(queue)} pairs...{Style.RESET_ALL}")
            
            for pair in queue:
                try:
                    self._process_pair(pair)
                except Exception as e:
                    print(f"{Fore.RED}[ERROR] Failed to process pair: {e}{Style.RESET_ALL}")
                    logger.exception("Pair processing failed")
                    continue
                
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Execute cycle failed: {e}{Style.RESET_ALL}")
            logger.exception("Execute cycle crashed")
            return False

    def _process_pair(self, pair):
        """
        Полный цикл обработки одной пары предметов.
        """
        part_a, part_b = pair
        item_a, tags_a = part_a
        item_b, tags_b = part_b
        
        print(f"\n{Fore.CYAN}>>> Crafting Pair: Slot {item_a.slot_index} + Slot {item_b.slot_index}{Style.RESET_ALL}")
        
        self.manager.lock_item(item_a.slot_index)
        self.manager.lock_item(item_b.slot_index)
        
        try:
            # 1. Загрузка в рекомбинатор
            human_click(config.PLAYER_INVENTORY_GRID[item_a.slot_index], key_modifier="ctrl")
            time.sleep(MOUSE_SETTLE_TIME)
            human_click(config.PLAYER_INVENTORY_GRID[item_b.slot_index], key_modifier="ctrl")
            
            # 2. Отводим мышь
            time.sleep(0.1)
            self._move_to_safe_zone()
            time.sleep(POST_CRAFT_WAIT)
            
            # 3. Скриншот
            with mss.mss() as sct:
                screenshot = np.array(sct.grab(sct.monitors[1]))
                screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

            # 4. Выбор модов
            self._select_mods(screenshot, config.RECOMB_ITEM_A_ROI, tags_a, item_a.item_class)
            self._select_mods(screenshot, config.RECOMB_ITEM_B_ROI, tags_b, item_b.item_class)
            
            # 5. Combine
            print("[EXECUTOR] Clicking Combine...")
            
            combine_coords = config.RECOMB_BTN_COMBINE_COORDS
            
            # ФИКС: Более безопасное извлечение координат
            try:
                if len(combine_coords) == 4:
                    target_click = (
                        (combine_coords[0] + combine_coords[2]) // 2,
                        (combine_coords[1] + combine_coords[3]) // 2
                    )
                elif len(combine_coords) == 2:
                    target_click = tuple(combine_coords)
                else:
                    raise ValueError(f"Invalid RECOMB_BTN_COMBINE_COORDS format: {combine_coords}")
                    
                human_click(target_click)
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Combine click failed: {e}{Style.RESET_ALL}")
                logger.exception("Failed to click combine button")
                return
            
            print(f"[EXECUTOR] Waiting for animation ({CRAFT_ANIMATION_DURATION}s)...")
            time.sleep(CRAFT_ANIMATION_DURATION)
            
            self._check_result_and_cleanup(item_a.slot_index, item_b.slot_index)
            
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Process pair failed: {e}{Style.RESET_ALL}")
            logger.exception("Pair processing error")
            # Разблокируем предметы в случае ошибки
            self.manager.unlock_item(item_a.slot_index)
            self.manager.unlock_item(item_b.slot_index)
            raise

    def _check_result_and_cleanup(self, slot_a_idx, slot_b_idx):
        """
        Проверяет результат крафта. ФИКС: Сначала проверяем, потом удаляем.
        """
        self._move_to_safe_zone()

        try:
            with mss.mss() as sct:
                screen = np.array(sct.grab(sct.monitors[1]))
                screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Screenshot failed: {e}{Style.RESET_ALL}")
            logger.exception("Failed to capture result screen")
            # ФИКС: Удаляем предметы даже если скриншот не удался
            self.manager.remove_item(slot_a_idx)
            self.manager.remove_item(slot_b_idx)
            return
        
        # Проверка на "Failed" сообщение
        try:
            fail_crop = self.ocr.crop_image(screen, config.RECOMB_FAIL_MSG_ROI)
            coords_fail = self.ocr.find_text_coordinates(
                fail_crop, "Failed", 
                offset=(config.RECOMB_FAIL_MSG_ROI[0], config.RECOMB_FAIL_MSG_ROI[1])
            )
            
            if coords_fail:
                print(f"{Fore.MAGENTA}[RESULT] BROKEN! (Found 'Failed' text){Style.RESET_ALL}")
                # ФИКС: Удаляем только после проверки
                self.manager.remove_item(slot_a_idx)
                self.manager.remove_item(slot_b_idx)
                return
        except Exception as e:
            print(f"{Fore.YELLOW}[WARNING] Failed text detection error: {e}{Style.RESET_ALL}")
            logger.warning(f"Failed to check for 'Failed' message: {e}")

        # Проверка яркости слота результата
        try:
            cx, cy = config.RECOMB_OUTPUT_SLOT
            half = RESULT_SLOT_SAMPLE_SIZE
            result_slot_crop = screen[cy-half:cy+half, cx-half:cx+half]
            
            # ФИКС: Конвертируем в grayscale для корректной проверки яркости
            gray_crop = cv2.cvtColor(result_slot_crop, cv2.COLOR_BGR2GRAY)
            avg_brightness = np.mean(gray_crop)

            if avg_brightness > config.RECOMB_RESULT_BRIGHTNESS_THRESHOLD:
                print(f"{Fore.GREEN}[RESULT] SUCCESS! Taking item (brightness: {avg_brightness:.1f}).{Style.RESET_ALL}")
                human_click(config.RECOMB_OUTPUT_SLOT, key_modifier="ctrl")
                time.sleep(POST_CRAFT_WAIT)
            else:
                print(f"{Fore.MAGENTA}[RESULT] BROKEN! (Slot empty, brightness: {avg_brightness:.1f}){Style.RESET_ALL}")
                
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Brightness check failed: {e}{Style.RESET_ALL}")
            logger.exception("Failed to check result brightness")
        
        # ФИКС: Удаляем предметы в конце, после всех проверок
        self.manager.remove_item(slot_a_idx)
        self.manager.remove_item(slot_b_idx)

    def _select_mods(self, full_screenshot, roi, wanted_tags, item_class):
        """
        Выбор нужных модификаторов на скриншоте.
        """
        try:
            crop = self.ocr.crop_image(full_screenshot, roi)
        except Exception as e:
            print(f"{Fore.RED}[ERROR] Failed to crop ROI: {e}{Style.RESET_ALL}")
            logger.exception(f"ROI crop failed for {roi}")
            return
        
        for tag in wanted_tags:
            target_text = self._get_text_for_tag(item_class, tag)
            if not target_text:
                print(f"{Fore.YELLOW}[WARNING] No text mapping for tag '{tag}'{Style.RESET_ALL}")
                continue
            
            try:
                coords = self.ocr.find_text_coordinates(
                    crop, 
                    target_text, 
                    offset=(roi[0], roi[1])
                )
                
                if coords:
                    gx, gy = coords
                    print(f"   -> Found '{tag}'. Clicking ({gx}, {gy})")
                    human_click((gx, gy))
                    time.sleep(MOD_SELECTION_DELAY)
                else:
                    print(f"{Fore.RED}   -> Missed '{tag}' ('{target_text}'){Style.RESET_ALL}")
                    
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Failed to select mod '{tag}': {e}{Style.RESET_ALL}")
                logger.exception(f"Mod selection failed for {tag}")

    def _get_text_for_tag(self, item_class, tag):
        """
        Получает текст для поиска по тегу и классу предмета.
        """
        class_config = mods_config.WANTED_MODS_BY_CLASS.get(item_class, {})
        for group, mappings in class_config.items():
            for text_key, tag_val in mappings.items():
                if tag_val == tag:
                    return text_key
        return None