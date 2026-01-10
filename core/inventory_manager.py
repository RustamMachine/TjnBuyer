from typing import List, Optional
from enum import Enum

class ItemStatus(Enum):
    EMPTY = "EMPTY"        # Пустой слот
    TRASH = "TRASH"        # Нет ценных модов
    CRAFT_BASE = "CRAFT_BASE" # 1 ценный мод (идеально для крафта)
    FINISHED = "FINISHED"  # 2+ ценных мода (готовый предмет, не трогать)
    LOCKED = "LOCKED"      # Используется прямо сейчас

class InventoryItem:
    def __init__(self, slot_index: int, item_class: str, tags: List[str]):
        self.slot_index = slot_index
        self.item_class = item_class
        self.tags = tags
        self.status = self._determine_status()

    def _determine_status(self) -> ItemStatus:
        if not self.tags:
            return ItemStatus.TRASH
        
        # Если 2 и более тегов — считаем предмет готовым (или полу-готовым).
        # Матчмейкер обычно ищет CRAFT_BASE, чтобы сделать FINISHED.
        if len(self.tags) >= 2:
            return ItemStatus.FINISHED
            
        return ItemStatus.CRAFT_BASE

    def __repr__(self):
        return f"Item(slot={self.slot_index}, cls={self.item_class}, tags={self.tags}, status={self.status.value})"

class InventoryManager:
    def __init__(self):
        self.items = {} 

    def update_slot(self, index: int, item_obj: Optional[InventoryItem]):
        self.items[index] = item_obj
        
    def get_crafting_candidates(self) -> List[InventoryItem]:
        """Возвращает только предметы, готовые к скрещиванию"""
        return [
            item for item in self.items.values() 
            if item and item.status == ItemStatus.CRAFT_BASE
        ]