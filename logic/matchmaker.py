from typing import List, Tuple, Set, Dict
from core.inventory_manager import InventoryItem, ItemStatus
from config.mods_config import MUTUALLY_EXCLUSIVE_GROUPS, TAG_TO_GROUP_MAP
from colorama import Fore, Style, init

init(autoreset=True)

# Типы данных для читаемости
# (Предмет, Список тегов для выбора в рекомбинаторе)
CraftingParticipant = Tuple[InventoryItem, List[str]]
CraftingPair = Tuple[CraftingParticipant, CraftingParticipant]

class Matchmaker:
    def create_crafting_queue(self, inventory: List[InventoryItem]) -> List[CraftingPair]:
        """
        Logic:
        1. Takes CRAFT_BASE items.
        2. Pairs them if:
           - Tags are different (set intersection check).
           - Tags are NOT in the same Mutually Exclusive Group.
        """
        print(f"\n{Fore.CYAN}=== MATCHMAKER (Logic Only) ==={Style.RESET_ALL}")
        
        pairs: List[CraftingPair] = []
        
        # 1. Filter Candidates (Only CRAFT_BASE)
        # Мы доверяем сканеру: если статус BASE, значит там есть 1+ валидный тег.
        candidates = [item for item in inventory if item.status == ItemStatus.CRAFT_BASE]
        
        print(f"Candidates: {len(candidates)}")

        # 2. Group by Class
        grouped_items = {}
        for item in candidates:
            if item.item_class not in grouped_items:
                grouped_items[item.item_class] = []
            grouped_items[item.item_class].append(item)
            
        # 3. Create Pairs
        for item_class, items in grouped_items.items():
            print(f"\nClass: {Fore.BLUE}{item_class}{Style.RESET_ALL} ({len(items)})")
            
            # Получаем настройки конфликтов для этого класса
            exclusive_groups = MUTUALLY_EXCLUSIVE_GROUPS.get(item_class, [])
            tag_map = TAG_TO_GROUP_MAP.get(item_class, {})
            
            used_indices: Set[int] = set()
            
            for i in range(len(items)):
                if i in used_indices:
                    continue
                    
                item_a = items[i]
                tags_a = set(item_a.tags)
                
                print(f"   A (Slot {item_a.slot_index}): {list(tags_a)}")
                best_match_idx = -1
                
                for j in range(i + 1, len(items)):
                    if j in used_indices:
                        continue
                        
                    item_b = items[j]
                    tags_b = set(item_b.tags)
                    
                    # --- ПРОВЕРКА 1: Разнообразие ---
                    # Если теги одинаковые (например Spirit + Spirit), скрещивать бессмысленно (обычно)
                    if tags_a == tags_b:
                        continue

                    # --- ПРОВЕРКА 2: Конфликты (Exclusive Groups) ---
                    # Нельзя скрещивать, если теги принадлежат одной запрещенной группе
                    has_conflict = False
                    for t_a in tags_a:
                        for t_b in tags_b:
                            g_a = tag_map.get(t_a)
                            g_b = tag_map.get(t_b)
                            if g_a and g_b and g_a == g_b and g_a in exclusive_groups:
                                has_conflict = True
                                break
                        if has_conflict: 
                            break
                            
                    if has_conflict:
                        print(f"      -> Skip B (Slot {item_b.slot_index}): Exclusive Group Conflict")
                        continue

                    # --- УСПЕХ ---
                    # Если мы здесь, пара валидна.
                    # В этой версии берем первого подходящего (Greedy strategy)
                    print(f"      -> {Fore.GREEN}MATCH{Style.RESET_ALL} with B (Slot {item_b.slot_index}): {list(tags_b)}")
                    best_match_idx = j
                    break
                
                if best_match_idx != -1:
                    item_b = items[best_match_idx]
                    
                    # Формируем результат с явным указанием тегов для кликера
                    part_a = (item_a, item_a.tags)
                    part_b = (item_b, item_b.tags)
                    
                    pairs.append((part_a, part_b))
                    used_indices.add(i)
                    used_indices.add(best_match_idx)
                else:
                    print(f"      -> No partner.")

        print(f"Pairs created: {len(pairs)}")
        return pairs