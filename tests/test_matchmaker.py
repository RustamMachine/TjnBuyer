import unittest
from core.inventory_manager import InventoryItem, ItemStatus
from logic.matchmaker import Matchmaker

class TestMatchmaker(unittest.TestCase):
    def setUp(self):
        self.matchmaker = Matchmaker()

    def create_mock_item(self, slot, item_class, tags):
        """Helper to create InventoryItem with specific state"""
        item = InventoryItem(slot_index=slot, item_class=item_class, tags=tags)
        return item

    def test_match_simple_pair(self):
        """
        Input: List [Item_A (Spirit), Item_B (GemSpell)]
        Assert: Result has 1 pair: (Item_A, Item_B)
        """
        item_a = self.create_mock_item(0, "Amulets", ["Spirit"])
        item_b = self.create_mock_item(1, "Amulets", ["GemSpell"])
        
        inventory = [item_a, item_b]
        
        pairs = self.matchmaker.create_crafting_queue(inventory)
        
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0], (item_a, item_b))

    def test_match_ignore_junk(self):
        """
        Input: List [Item_A (Spirit), Item_C (Junk/Empty)]
        Assert: Result is Empty (Item C has no value, so A has no partner)
        """
        item_a = self.create_mock_item(0, "Amulets", ["Spirit"])
        item_c = self.create_mock_item(1, "Amulets", []) # No tags = Trash
        
        inventory = [item_a, item_c]
        
        pairs = self.matchmaker.create_crafting_queue(inventory)
        
        self.assertEqual(len(pairs), 0)

    def test_match_distinct_classes(self):
        """
        Input: List [Item_A (Amulet), Item_D (Ring)]
        Assert: Result is Empty (Cannot pair Amulet with Ring)
        """
        item_a = self.create_mock_item(0, "Amulets", ["Spirit"])
        item_d = self.create_mock_item(1, "Rings", ["ColdAttack"])
        
        inventory = [item_a, item_d]
        
        pairs = self.matchmaker.create_crafting_queue(inventory)
        
        self.assertEqual(len(pairs), 0)

    def test_match_rings(self):
        """
        Input: List [Item_D (Cold), Item_E (Fire)]
        Assert: Result has 1 pair (Item_D, Item_E)
        """
        item_d = self.create_mock_item(0, "Rings", ["ColdAttack"])
        item_e = self.create_mock_item(1, "Rings", ["FireAttack"])
        
        inventory = [item_d, item_e]
        
        pairs = self.matchmaker.create_crafting_queue(inventory)
        
        self.assertEqual(len(pairs), 1)
        # Порядок в паре не важен, но проверим состав
        self.assertIn(item_d, pairs[0])
        self.assertIn(item_e, pairs[0])

    def test_ignore_finished_items(self):
        """
        Input: Item_F (Ring, 2 tags -> FINISHED) + Item_G (Ring, 1 tag)
        Assert: Empty queue. Finished items should not be inputs.
        """
        item_f = self.create_mock_item(0, "Rings", ["Life", "ColdAttack"]) # 2 tags -> FINISHED
        item_g = self.create_mock_item(1, "Rings", ["FireAttack"])
        
        inventory = [item_f, item_g]
        
        pairs = self.matchmaker.create_crafting_queue(inventory)
        
        self.assertEqual(len(pairs), 0)

    def test_complex_inventory(self):
        """
        Input: 4 rings. A(Cold), B(Fire), C(Lightning), D(Chaos)
        Expect: 2 pairs. (A,B) and (C,D) or similar combinations.
        """
        r1 = self.create_mock_item(0, "Rings", ["ColdAttack"])
        r2 = self.create_mock_item(1, "Rings", ["FireAttack"])
        r3 = self.create_mock_item(2, "Rings", ["LightningAttack"])
        r4 = self.create_mock_item(3, "Rings", ["ChaosRes"])
        
        inventory = [r1, r2, r3, r4]
        
        pairs = self.matchmaker.create_crafting_queue(inventory)
        
        self.assertEqual(len(pairs), 2)
        
        # Check that all items are used exactly once
        used_items = []
        for p in pairs:
            used_items.extend(p)
        
        self.assertCountEqual(used_items, inventory)

if __name__ == "__main__":
    unittest.main()
