from typing import List, Optional
from enum import Enum

class ItemStatus(Enum):
    EMPTY = "EMPTY"
    TRASH = "TRASH"
    CRAFT_BASE = "CRAFT_BASE"
    FINISHED = "FINISHED"
    LOCKED = "LOCKED"

class InventoryItem:
    def __init__(self, slot_index: int, item_class: str, tags: List[str]):
        self.slot_index = slot_index
        self.item_class = item_class
        self.tags = tags
        self.status = self._determine_status()

    def _determine_status(self) -> ItemStatus:
        if not self.tags:
            return ItemStatus.TRASH
        if len(self.tags) >= 2:
            return ItemStatus.FINISHED
        return ItemStatus.CRAFT_BASE

    def __repr__(self):
        return f"InventoryItem(slot={self.slot_index}, class={self.item_class}, tags={self.tags}, status={self.status})"

class InventoryManager:
    def __init__(self):
        self.items = {} # Placeholder

    def update_slot(self, index, item_obj):
        self.items[index] = item_obj
