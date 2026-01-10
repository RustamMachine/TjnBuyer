import re
from typing import Optional
from core.inventory_manager import InventoryItem, InventoryManager
from config.mods_config import WANTED_MODS_BY_CLASS

class ItemScanner:
    def __init__(self, manager: InventoryManager):
        self.manager = manager

    def _parse_text_poe2(self, raw_text: str, slot_index: int) -> Optional[InventoryItem]:
        # 1. Определяем класс предмета
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        item_class = None
        
        for line in lines:
            if line.startswith("Item Class:"):
                item_class = line.split(":")[1].strip()
                break
        
        # Если класс не в конфиге - это мусор
        if not item_class or item_class not in WANTED_MODS_BY_CLASS:
            return None # Или вернуть InventoryItem со статусом TRASH

        # 2. Ищем Т1 моды согласно конфигу
        found_tags = []
        rules = WANTED_MODS_BY_CLASS[item_class]

        for i, line in enumerate(lines):
            # Парсим только Tier 1
            if "(Tier: 1)" in line and line.startswith("{") and line.endswith("}"):
                if i + 1 < len(lines):
                    mod_text = lines[i + 1]
                    
                    # Бежим по группам правил (Damage, Resources и т.д.)
                    for group_name, mappings in rules.items():
                        for substring, tag in mappings.items():
                            if substring in mod_text:
                                found_tags.append(tag)
                                # Нашли совпадение для этой строки - идем к следующей строке текста
                                break 

        # Убираем дубликаты (на всякий случай)
        found_tags = list(set(found_tags))

        # Создаем предмет. InventoryItem сам выставит статус (TRASH/CRAFT_BASE/FINISHED)
        return InventoryItem(slot_index, item_class, found_tags)

    # Метод для вызова из бота (пример)
    def scan_slot_text(self, text: str, slot_index: int):
        item = self._parse_text_poe2(text, slot_index)
        if item:
            self.manager.update_slot(slot_index, item)
        else:
            # Если item None, значит класс не подошел или еще что-то
            # Можно создать пустой/мусорный итем
            self.manager.update_slot(slot_index, InventoryItem(slot_index, "Unknown", []))