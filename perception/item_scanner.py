from core.inventory_manager import InventoryItem, InventoryManager

class ItemScanner:
    def __init__(self, manager: InventoryManager):
        self.manager = manager

    def _parse_text_poe2(self, raw_text: str, slot_index: int):
        # STUB IMPLEMENTATION - Will fail tests but allow them to run
        return None
