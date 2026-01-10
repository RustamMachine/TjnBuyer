import re
from core.inventory_manager import InventoryItem, InventoryManager
from config.mods_config import WANTED_MODS_BY_CLASS

class ItemScanner:
    def __init__(self, manager: InventoryManager):
        self.manager = manager

    def _parse_text_poe2(self, raw_text: str, slot_index: int) -> InventoryItem:
        print(f"\n--- [DEBUG] Анализ предмета в слоте {slot_index} ---")
        lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        
        # 1. Определяем класс предмета
        item_class = None
        for line in lines:
            if line.startswith("Item Class:"):
                item_class = line.split(":")[1].strip()
                print(f"   [DEBUG] Найден класс: '{item_class}'")
                break
        
        if not item_class or item_class not in WANTED_MODS_BY_CLASS:
            print(f"   [DEBUG] Класс '{item_class}' нас не интересует -> SKIP")
            return None

        # 2. Ищем Т1 моды
        found_tags = []
        rules = WANTED_MODS_BY_CLASS[item_class]

        for i, line in enumerate(lines):
            # Ищем строку с Tier: 1
            if "(Tier: 1)" in line and line.startswith("{") and line.endswith("}"):
                print(f"   [DEBUG] Нашел Т1 аффикс в строке: {line}")
                
                # Проверяем следующую строку на наличие полезных свойств
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    print(f"      -> Смотрю описание мода: '{next_line}'")
                    
                    # Проверяем правила из конфига
                    for pattern, tag in rules.items():
                        if isinstance(tag, dict):
                            # Вложенный поиск (например, для урона)
                            for sub_pattern, sub_tag in tag.items():
                                if sub_pattern in next_line:
                                    print(f"         !!! СОВПАДЕНИЕ: '{sub_pattern}' -> Тег: {sub_tag}")
                                    found_tags.append(sub_tag)
                        else:
                            # Простой поиск подстроки
                            if pattern in next_line:
                                print(f"         !!! СОВПАДЕНИЕ: '{pattern}' -> Тег: {tag}")
                                found_tags.append(tag)

        # Убираем дубликаты
        found_tags = list(set(found_tags))
        print(f"   [DEBUG] Итоговые теги: {found_tags}")

        if not found_tags:
            print("   [DEBUG] Полезных тегов нет -> TRASH")
            return None

        print("   [DEBUG] Предмет принят!")
        return InventoryItem(slot_index, item_class, found_tags)


