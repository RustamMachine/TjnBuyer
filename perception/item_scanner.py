import re
from typing import Optional
from core.inventory_manager import InventoryItem, InventoryManager
from config.mods_config import WANTED_MODS_BY_CLASS
import config.config as config
from colorama import Fore, Style

class ItemScanner:
    def __init__(self, manager: InventoryManager):
        self.manager = manager

    def _parse_text_poe2(self, raw_text: str, slot_index: int) -> Optional[InventoryItem]:
        # 1. Проверка на пустой буфер обмена
        if not raw_text or not raw_text.strip():
            if config.DETAILED_LOGGING:
                print(f"{Fore.RED}[SCANNER] Slot {slot_index}: Empty text! (Copy failed?){Style.RESET_ALL}")
            return None

        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        item_class = None
        
        # 2. Определяем класс предмета
        for line in lines:
            if line.startswith("Item Class:"):
                item_class = line.split(":")[1].strip()
                break
        
        # Если класс не найден или не интересен
        if not item_class:
            return None

        if item_class not in WANTED_MODS_BY_CLASS:
            if config.DETAILED_LOGGING:
                print(f"[SCANNER] Slot {slot_index}: Class '{item_class}' ignored.")
            return None

        # 3. Проверка наличия Tier-информации (Advanced Mod Descriptions)
        has_tier_info = any("(Tier:" in line for line in lines)
        if not has_tier_info:
            if config.DETAILED_LOGGING:
                print(f"{Fore.RED}[SCANNER] Slot {slot_index} ({item_class}): NO TIER INFO! Enable 'Advanced Mod Descriptions' in PoE Options!{Style.RESET_ALL}")
            return InventoryItem(slot_index, item_class, [])

        # 4. Ищем Т1 моды согласно конфигу
        found_tags = []
        rules = WANTED_MODS_BY_CLASS[item_class]

        if config.DETAILED_LOGGING:
            print(f"--- Scanning Slot {slot_index} ({item_class}) ---")

        for i, line in enumerate(lines):
            # Парсим только Tier 1
            if "(Tier: 1)" in line and line.startswith("{") and line.endswith("}"):
                if i + 1 < len(lines):
                    mod_text = lines[i + 1]
                    
                    if config.DETAILED_LOGGING:
                        print(f"   Line T1: '{mod_text}'")
                    
                    # Бежим по группам правил
                    for group_name, mappings in rules.items():
                        for substring, tag in mappings.items():
                            if substring in mod_text:
                                found_tags.append(tag)
                                if config.DETAILED_LOGGING:
                                    print(f"     {Fore.GREEN}-> MATCH: '{substring}' => Tag: {tag}{Style.RESET_ALL}")
                                break 

        found_tags = list(set(found_tags))

        if config.DETAILED_LOGGING and found_tags:
            print(f"{Fore.CYAN}[SCANNER] Slot {slot_index} Result: {found_tags}{Style.RESET_ALL}")

        # Создаем предмет. InventoryItem сам выставит статус (TRASH/CRAFT_BASE/FINISHED)
        return InventoryItem(slot_index, item_class, found_tags)

    def scan_slot_text(self, text: str, slot_index: int):
        item = self._parse_text_poe2(text, slot_index)
        if item:
            self.manager.update_slot(slot_index, item)
        else:
            self.manager.update_slot(slot_index, InventoryItem(slot_index, "Unknown", []))