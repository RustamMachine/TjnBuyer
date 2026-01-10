from typing import List, Tuple, Set
from core.inventory_manager import InventoryItem, ItemStatus

class Matchmaker:
    def create_crafting_queue(self, inventory: List[InventoryItem]) -> List[Tuple[InventoryItem, InventoryItem]]:
        """
        Creates a list of pairs for recombination.
        Logic:
        1. Filter for CRAFT_BASE items (status check).
        2. Group by Item Class.
        3. Pair items with DIFFERENT tags within the same class.
        """
        pairs = []
        
        # 1. Filter valid candidates
        candidates = [item for item in inventory if item.status == ItemStatus.CRAFT_BASE]
        
        # 2. Group by Class
        grouped_items = {}
        for item in candidates:
            if item.item_class not in grouped_items:
                grouped_items[item.item_class] = []
            grouped_items[item.item_class].append(item)
            
        # 3. Create Pairs
        for item_class, items in grouped_items.items():
            used_indices: Set[int] = set()
            
            # Simple greedy pairing
            for i in range(len(items)):
                if i in used_indices:
                    continue
                    
                item_a = items[i]
                best_match_idx = -1
                
                # Look for a partner j > i
                for j in range(i + 1, len(items)):
                    if j in used_indices:
                        continue
                        
                    item_b = items[j]
                    
                    # Core Logic: Tags must be different to create a merged item
                    # (e.g. Life + Mana -> Life & Mana)
                    # We check if the intersection is smaller than the union of tags (meaning they aren't identical)
                    # Ideally, we want NO overlap for maximum efficiency, but for now just "different sets" is enough context
                    # strict rule from mm.md: "Find two items... that have different valuable tags"
                    
                    # Let's verify strict difference:
                    set_a = set(item_a.tags)
                    set_b = set(item_b.tags)
                    
                    if set_a != set_b and not set_a.intersection(set_b):
                         # Perfect match: totally different tags (e.g. Life vs Fire)
                        best_match_idx = j
                        break
                    
                    # Fallback logic: If we can't find a perfect disjoint match, 
                    # should we pair partially overlapping ones? 
                    # For this MVP, let's stick to the test cases implies distinct tags (Cold vs Fire).
                    # If we have {Life, Cold} and {Life, Fire}, that's also good.
                    if set_a != set_b:
                        best_match_idx = j
                        # Don't break yet, prefer disjoint if possible? 
                        # For simplicity/MVP: take first valid different-tag partner.
                        break
                
                if best_match_idx != -1:
                    item_b = items[best_match_idx]
                    pairs.append((item_a, item_b))
                    used_indices.add(i)
                    used_indices.add(best_match_idx)
                    
        return pairs