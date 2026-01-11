from typing import List, Tuple, Set, Dict
from core.inventory_manager import InventoryItem, ItemStatus
from config.mods_config import MUTUALLY_EXCLUSIVE_GROUPS, TAG_TO_GROUP_MAP
import config.config as config
from colorama import Fore, Style, init

init(autoreset=True)

CraftingParticipant = Tuple[InventoryItem, List[str]]
CraftingPair = Tuple[CraftingParticipant, CraftingParticipant]

class Matchmaker:
    def create_crafting_queue(self, inventory: List[InventoryItem]) -> List[CraftingPair]:
        """
        Logic:
        1. Takes CRAFT_BASE items (single mod items).
        2. Pairs them if:
           - Tags are COMPLETELY DIFFERENT (sets are disjoint).
           - Tags are NOT in the same Mutually Exclusive Group.
        """
        if config.DETAILED_LOGGING:
            print(f"\n{Fore.CYAN}=== MATCHMAKER ==={Style.RESET_ALL}")
        
        pairs: List[CraftingPair] = []
        
        # Берем только CRAFT_BASE (предметы с 1 модом)
        candidates = [item for item in inventory if item.status == ItemStatus.CRAFT_BASE]
        
        if config.DETAILED_LOGGING:
            print(f"Candidates (CRAFT_BASE): {len(candidates)}")

        # Группируем по классу (Amulet, Ring и т.д.)
        grouped_items = {}
        for item in candidates:
            if item.item_class not in grouped_items:
                grouped_items[item.item_class] = []
            grouped_items[item.item_class].append(item)
            
        # Создаем пары
        for item_class, items in grouped_items.items():
            if config.DETAILED_LOGGING:
                print(f"Class: {Fore.BLUE}{item_class}{Style.RESET_ALL} ({len(items)})")
            
            exclusive_groups = MUTUALLY_EXCLUSIVE_GROUPS.get(item_class, [])
            tag_map = TAG_TO_GROUP_MAP.get(item_class, {})
            
            used_indices: Set[int] = set()
            
            for i in range(len(items)):
                if i in used_indices:
                    continue
                    
                item_a = items[i]
                tags_a = set(item_a.tags)
                
                if config.DETAILED_LOGGING:
                    print(f"   Slot {item_a.slot_index} [{', '.join(tags_a)}] looking for partner...")
                
                best_match_idx = -1
                
                for j in range(i + 1, len(items)):
                    if j in used_indices:
                        continue
                        
                    item_b = items[j]
                    tags_b = set(item_b.tags)
                    
                    # 1. ПРОВЕРКА НА ПЕРЕСЕЧЕНИЕ (НОВОЕ)
                    # Если есть хоть один общий тег (например Spirit и Spirit) - пропускаем.
                    # Мы хотим крафтить {A} + {B} -> {A, B}.
                    # А не {A} + {A} -> {A}.
                    if not tags_a.isdisjoint(tags_b):
                        # if config.DETAILED_LOGGING:
                        #     print(f"      -> Skip Slot {item_b.slot_index}: Overlapping tags")
                        continue

                    # 2. Проверка на группы исключений (Exclusive Groups)
                    # Например, нельзя скрестить Mana и Life, если они в одной группе.
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
                        if config.DETAILED_LOGGING:
                            print(f"      -> Skip Slot {item_b.slot_index}: Exclusive Group Conflict")
                        continue

                    # УСПЕХ
                    if config.DETAILED_LOGGING:
                        print(f"      -> {Fore.GREEN}MATCH{Style.RESET_ALL} with Slot {item_b.slot_index} [{', '.join(tags_b)}]")
                    
                    best_match_idx = j
                    break
                
                if best_match_idx != -1:
                    item_b = items[best_match_idx]
                    part_a = (item_a, item_a.tags)
                    part_b = (item_b, item_b.tags)
                    pairs.append((part_a, part_b))
                    used_indices.add(i)
                    used_indices.add(best_match_idx)
                else:
                    if config.DETAILED_LOGGING:
                        print(f"      -> No valid partner found.")

        print(f"Pairs created: {len(pairs)}")
        return pairs