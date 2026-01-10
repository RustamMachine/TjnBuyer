import unittest
from unittest.mock import patch
from core.inventory_manager import InventoryItem, ItemStatus
from logic.matchmaker import Matchmaker

# MOCK DATA
MOCK_EXCLUSIVE_GROUPS = {
    "Amulets": ["GemLevels"]
}

MOCK_TAG_MAP = {
    "Amulets": {
        "GemSpell": "GemLevels",
        "GemMelee": "GemLevels",
        "Spirit": "Resources"
    },
    "Rings": {
        # Все эти теги считаются разными и неконфликтующими в тесте
        "ColdAttack": "ElementalDamage",
        "FireAttack": "ElementalDamage",
        "LightningAttack": "ElementalDamage",
        "ChaosRes": "Resistances",
        "Life": "Stats",
        "Mana": "Stats",
        "Speed": "SpeedGroup",
        "Rarity": "Misc",
        "CastRate": "SpeedGroup"
    }
}

class TestMatchmaker(unittest.TestCase):
    def setUp(self):
        self.matchmaker = Matchmaker()

    def create_item(self, slot, cls, tags):
        return InventoryItem(slot, cls, tags)

    @patch("logic.matchmaker.MUTUALLY_EXCLUSIVE_GROUPS", MOCK_EXCLUSIVE_GROUPS)
    @patch("logic.matchmaker.TAG_TO_GROUP_MAP", MOCK_TAG_MAP)
    def test_simple_match(self):
        """Spirit + GemSpell = OK (Разные группы)"""
        i1 = self.create_item(0, "Amulets", ["Spirit"])
        i2 = self.create_item(1, "Amulets", ["GemSpell"])
        
        pairs = self.matchmaker.create_crafting_queue([i1, i2])
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0][0][1], ["Spirit"])

    @patch("logic.matchmaker.MUTUALLY_EXCLUSIVE_GROUPS", MOCK_EXCLUSIVE_GROUPS)
    @patch("logic.matchmaker.TAG_TO_GROUP_MAP", MOCK_TAG_MAP)
    def test_exclusive_conflict(self):
        """GemSpell + GemMelee = Conflict (Одна группа GemLevels)"""
        i1 = self.create_item(0, "Amulets", ["GemSpell"])
        i2 = self.create_item(1, "Amulets", ["GemMelee"])
        
        pairs = self.matchmaker.create_crafting_queue([i1, i2])
        self.assertEqual(len(pairs), 0)

    @patch("logic.matchmaker.MUTUALLY_EXCLUSIVE_GROUPS", MOCK_EXCLUSIVE_GROUPS)
    @patch("logic.matchmaker.TAG_TO_GROUP_MAP", MOCK_TAG_MAP)
    def test_ignore_finished_items(self):
        """Предмет с 2 тегами (FINISHED) должен игнорироваться"""
        i_finished = self.create_item(0, "Amulets", ["Spirit", "GemSpell"])
        i_base = self.create_item(1, "Amulets", ["Spirit"])
        
        self.assertEqual(i_finished.status, ItemStatus.FINISHED)
        
        pairs = self.matchmaker.create_crafting_queue([i_finished, i_base])
        self.assertEqual(len(pairs), 0)

    @patch("logic.matchmaker.MUTUALLY_EXCLUSIVE_GROUPS", MOCK_EXCLUSIVE_GROUPS)
    @patch("logic.matchmaker.TAG_TO_GROUP_MAP", MOCK_TAG_MAP)
    def test_nine_candidates_stress_test(self):
        """
        9 кандидатов (Rings). 
        Все теги разные.
        Должно получиться 4 пары, и 1 предмет останется без пары.
        """
        # Создаем 9 предметов с уникальными тегами
        tags_list = [
            "ColdAttack", "FireAttack", "LightningAttack", 
            "ChaosRes", "Life", "Mana", 
            "Speed", "Rarity", "CastRate"
        ]
        
        inventory = []
        for i, tag in enumerate(tags_list):
            item = self.create_item(i, "Rings", [tag])
            inventory.append(item)
            
        pairs = self.matchmaker.create_crafting_queue(inventory)
        
        # 9 предметов -> 4 пары (8 занято), 1 остался
        self.assertEqual(len(pairs), 4)
        
        # Проверим, что все предметы в парах уникальны
        used_items = set()
        for p in pairs:
            item_a = p[0][0]
            item_b = p[1][0]
            used_items.add(item_a)
            used_items.add(item_b)
            
        self.assertEqual(len(used_items), 8)
        print(f"\n[TEST INFO] Used {len(used_items)}/9 items. Pairs: {len(pairs)}")

if __name__ == "__main__":
    unittest.main()