from enum import Enum
import threading

class ItemStatus(str, Enum):
    UNKNOWN = "unknown"
    TRASH = "trash"
    CRAFT_BASE = "craft_base" # 1 тег - заготовка
    FINISHED = "finished"     # 2+ тега - результат
    LOCKED = "locked"
    OCR_ERROR = "ocr_error"

class InventoryItem:
    def __init__(self, slot_index, item_class, tags):
        self.slot_index = slot_index
        self.item_class = item_class
        self.tags = tags  # Список строк
        
        # Автоматическое определение статуса
        if not tags:
            self.status = ItemStatus.TRASH
        elif len(tags) >= 2:
            # Если нашли 2 и более нужных модов - считаем предмет готовым/ценным
            self.status = ItemStatus.FINISHED
        else:
            # Если 1 мод - это база для крафта
            self.status = ItemStatus.CRAFT_BASE

    def __repr__(self):
        return f"Slot{self.slot_index}({self.item_class}, {self.tags}, {self.status})"

class InventoryManager:
    def __init__(self):
        self.slots = {}  # index -> InventoryItem
        self.lock = threading.Lock()

    def update_slot(self, index, item):
        with self.lock:
            self.slots[index] = item

    def get_item(self, index):
        with self.lock:
            return self.slots.get(index)

    def get_crafting_candidates(self):
        """Возвращает список предметов, готовых к крафту."""
        with self.lock:
            return [
                item for item in self.slots.values() 
                if item.status == ItemStatus.CRAFT_BASE
            ]

    def lock_item(self, index):
        with self.lock:
            if index in self.slots:
                self.slots[index].status = ItemStatus.LOCKED

    def unlock_item(self, index):
        """
        Разблокирует предмет.
        ВАЖНО: Возвращает статус на основе количества тегов, 
        чтобы случайно не сделать FINISHED предмет снова CRAFT_BASE при ошибке.
        """
        with self.lock:
            if index in self.slots:
                item = self.slots[index]
                if len(item.tags) >= 2:
                    item.status = ItemStatus.FINISHED
                else:
                    item.status = ItemStatus.CRAFT_BASE
    
    def mark_as_error(self, index):
        with self.lock:
            if index in self.slots:
                self.slots[index].status = ItemStatus.OCR_ERROR

    def remove_item(self, index):
        with self.lock:
            if index in self.slots:
                del self.slots[index]