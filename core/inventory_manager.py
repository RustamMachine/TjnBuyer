from typing import List, Optional, Dict
from enum import Enum

class ItemStatus(Enum):
    EMPTY = "EMPTY"        # Слот пуст
    TRASH = "TRASH"        # Предмет есть, но он мусор
    CRAFT_BASE = "CRAFT_BASE" # 1 ценный мод (кандидат)
    FINISHED = "FINISHED"  # 2+ ценных мода (готовый)
    LOCKED = "LOCKED"      # В процессе использования прямо сейчас

class InventoryItem:
    def __init__(self, slot_index: int, item_class: str, tags: List[str]):
        self.slot_index = slot_index
        self.item_class = item_class
        self.tags = tags
        self.status = self._determine_status()

    def _determine_status(self) -> ItemStatus:
        if not self.tags:
            return ItemStatus.TRASH
        
        # Если 2 и более тегов — считаем предмет готовым.
        if len(self.tags) >= 2:
            return ItemStatus.FINISHED
            
        return ItemStatus.CRAFT_BASE

    def __repr__(self):
        return f"Item(slot={self.slot_index}, cls={self.item_class}, tags={self.tags}, status={self.status.value})"

class InventoryManager:
    def __init__(self):
        # Храним состояние всех 60 слотов (0-59). Изначально None.
        self.items: Dict[int, Optional[InventoryItem]] = {i: None for i in range(60)}

    def update_slot(self, index: int, item_obj: Optional[InventoryItem]):
        """Обновляет информацию о предмете в слоте."""
        if 0 <= index < 60:
            self.items[index] = item_obj

    def remove_item(self, index: int):
        """Очищает слот (например, предмет забрали в рекомбинатор)."""
        if 0 <= index < 60:
            self.items[index] = None

    def get_item(self, index: int) -> Optional[InventoryItem]:
        return self.items.get(index)
        
    def get_crafting_candidates(self) -> List[InventoryItem]:
        """Возвращает список предметов, доступных для крафта (Base)."""
        return [
            item for item in self.items.values() 
            if item and item.status == ItemStatus.CRAFT_BASE
        ]

    def get_next_empty_slot(self) -> int:
        """Ищет первый свободный слот (для выгрузки результата). Возвращает -1, если всё занято."""
        for i in range(60):
            if self.items[i] is None:
                return i
        return -1

    def lock_item(self, index: int):
        """Помечает предмет как используемый (чтобы не взять его дважды)."""
        item = self.items.get(index)
        if item:
            item.status = ItemStatus.LOCKED

    def unlock_item(self, index: int):
        """Снимает блокировку (если крафт не состоялся)."""
        item = self.items.get(index)
        if item and item.status == ItemStatus.LOCKED:
            # Пересчитываем статус заново
            item.status = item._determine_status()