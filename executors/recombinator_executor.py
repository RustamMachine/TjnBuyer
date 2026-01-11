import time
import os
import random
import mss
import cv2
import ctypes
import numpy as np
import config.config as config
import config.mods_config as mods_config
from colorama import Fore, Style

# Импорты подсистем
# Убрал move_smooth из импорта, используем smooth_move
from core.inventory_manager import InventoryManager, ItemStatus
from core.input_handler import human_click, copy_item_data, release_all_modifiers, smooth_move
from perception.item_scanner import ItemScanner
from perception.ocr_engine import OCREngine
from perception.shopping_vision import get_occupied_inventory_slots
from logic.matchmaker import Matchmaker

class RecombinatorExecutor:
    def __init__(self):
        self.manager = InventoryManager()
        self.scanner = ItemScanner(self.manager)
        self.matchmaker = Matchmaker()
        self.ocr = OCREngine()
        
        user32 = ctypes.windll.user32
        self.screen_width = user32.GetSystemMetrics(0)
        self.screen_height = user32.GetSystemMetrics(1)
        
    def _move_to_safe_zone(self):
        """
        Быстрый и плавный увод мыши ЗА край экрана.
        """
        target_x = self.screen_width - 1
        target_y = self.screen_height // 2 + random.randint(-100, 100)
        
        # Используем smooth_move
        smooth_move(target_x, target_y, speed_mult=5.0)
        time.sleep(0.15) 

    def scan_player_inventory(self):
        """
        Оптимизированное сканирование инвентаря.
        """
        print(f"{Fore.YELLOW}[EXECUTOR] Vision Scan (Check empty slots)...{Style.RESET_ALL}")
        
        occupied_indices = get_occupied_inventory_slots()
        
        if not occupied_indices:
            print(f"{Fore.YELLOW}[EXECUTOR] Inventory appears empty (Vision).{Style.RESET_ALL}")
            return

        print(f"{Fore.YELLOW}[EXECUTOR] Detailed Scan of {len(occupied_indices)} items...{Style.RESET_ALL}")
        
        release_all_modifiers()

        for i in occupied_indices:
            item = self.manager.get_item(i)
            if item and item.status == ItemStatus.LOCKED:
                continue

            coords = config.PLAYER_INVENTORY_GRID[i]
            
            # Используем smooth_move
            smooth_move(coords[0], coords[1])
            time.sleep(0.04)
            raw_text = copy_item_data()
            self.scanner.scan_slot_text(raw_text, i)
            
        release_all_modifiers()

        print("[EXECUTOR] Scan complete. Moving mouse to safe zone.")
        self._move_to_safe_zone()

    def execute_cycle(self):
        """
        Главный метод цикла крафта.
        """
        self.scan_player_inventory()
        
        candidates = self.manager.get_crafting_candidates()
        queue = self.matchmaker.create_crafting_queue(candidates)
        
        if not queue:
            print(f"{Fore.RED}[EXECUTOR] No valid pairs found.{Style.RESET_ALL}")
            return False

        print(f"{Fore.GREEN}[EXECUTOR] Processing {len(queue)} pairs...{Style.RESET_ALL}")
        
        for pair in queue:
            self._process_pair(pair)
            
        return True

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
        
        # 1. Загрузка в рекомбинатор
        human_click(config.PLAYER_INVENTORY_GRID[item_a.slot_index], key_modifier="ctrl")
        time.sleep(0.15)
        human_click(config.PLAYER_INVENTORY_GRID[item_b.slot_index], key_modifier="ctrl")
        
        # 2. Отводим мышь
        time.sleep(0.1)
        self._move_to_safe_zone()
        time.sleep(0.3) 
        
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
        
        if len(combine_coords) == 4:
            cx = (combine_coords[0] + combine_coords[2]) // 2
            cy = (combine_coords[1] + combine_coords[3]) // 2
            target_click = (cx, cy)
        elif len(combine_coords) == 2:
            target_click = combine_coords
        else:
            print(f"{Fore.RED}[ERROR] Invalid Combine Coords format!{Style.RESET_ALL}")
            return

        human_click(target_click)
        
        print("[EXECUTOR] Waiting for animation (6s)...")
        time.sleep(6.0) 
        
        self._check_result_and_cleanup(item_a.slot_index, item_b.slot_index)

    def _check_result_and_cleanup(self, slot_a_idx, slot_b_idx):
        """
        Проверяет результат крафта.
        """
        self.manager.remove_item(slot_a_idx)
        self.manager.remove_item(slot_b_idx)

        self._move_to_safe_zone()

        with mss.mss() as sct:
            screen = np.array(sct.grab(sct.monitors[1]))
            screen = cv2.cvtColor(screen, cv2.COLOR_BGRA2BGR)
        
        fail_crop = self.ocr.crop_image(screen, config.RECOMB_FAIL_MSG_ROI)
        coords_fail = self.ocr.find_text_coordinates(
            fail_crop, "Failed", 
            offset=(config.RECOMB_FAIL_MSG_ROI[0], config.RECOMB_FAIL_MSG_ROI[1])
        )
        
        if coords_fail:
            print(f"{Fore.MAGENTA}[RESULT] BROKEN! (Found 'Failed' text){Style.RESET_ALL}")
            return

        cx, cy = config.RECOMB_OUTPUT_SLOT
        half = 10
        result_slot_crop = screen[cy-half:cy+half, cx-half:cx+half]
        
        avg_brightness = np.mean(result_slot_crop)

        if avg_brightness > config.RECOMB_RESULT_BRIGHTNESS_THRESHOLD:
            print(f"{Fore.GREEN}[RESULT] SUCCESS! Taking item.{Style.RESET_ALL}")
            human_click(config.RECOMB_OUTPUT_SLOT, key_modifier="ctrl")
            time.sleep(0.3)
        else:
            print(f"{Fore.MAGENTA}[RESULT] BROKEN! (Slot empty, low brightness){Style.RESET_ALL}")

    def _select_mods(self, full_screenshot, roi, wanted_tags, item_class):
        crop = self.ocr.crop_image(full_screenshot, roi)
        
        for tag in wanted_tags:
            target_text = self._get_text_for_tag(item_class, tag)
            if not target_text: continue
            
            coords = self.ocr.find_text_coordinates(crop, target_text, offset=(roi[0], roi[1]))
            
            if coords:
                gx, gy = coords
                print(f"   -> Found '{tag}'. Clicking ({gx}, {gy})")
                human_click((gx, gy))
                time.sleep(0.1)
            else:
                print(f"{Fore.RED}   -> Missed '{tag}' ('{target_text}'){Style.RESET_ALL}")

    def _get_text_for_tag(self, item_class, tag):
        class_config = mods_config.WANTED_MODS_BY_CLASS.get(item_class, {})
        for group, mappings in class_config.items():
            for text_key, tag_val in mappings.items():
                if tag_val == tag:
                    return text_key
        return None