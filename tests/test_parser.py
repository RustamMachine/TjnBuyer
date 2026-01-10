import unittest
from core.inventory_manager import InventoryManager
from perception.item_scanner import ItemScanner
from tests.fixtures_data import TEST_CASES

class TestItemParser(unittest.TestCase):
    def setUp(self):
        # Нам нужен экземпляр сканера, чтобы вызвать метод.
        # InventoryManager тут нужен только как заглушка для init.
        self.dummy_manager = InventoryManager() 
        self.scanner = ItemScanner(self.dummy_manager)

    def test_parser_logic(self):
        """Табличный тест: проверяет все кейсы из fixtures_data.py"""
        
        print(f"\n--- Запуск тестов парсера ({len(TEST_CASES)} кейсов) ---")

        for case in TEST_CASES:
            with self.subTest(msg=f"Case: {case['id']} - {case['description']}"):
                
                # 1. Действие (Action)
                # Передаем текст и фейковый индекс слота (0)
                result_item = self.scanner._parse_text_poe2(case["raw_text"], 0)

                # 2. Проверка (Assertion)
                
                # Сценарий: Предмет должен быть мусором (None)
                if case["should_be_none"]:
                    self.assertIsNone(
                        result_item, 
                        f"Ожидался None (мусор), но вернулся объект: {result_item}"
                    )
                
                # Сценарий: Предмет валидный
                else:
                    self.assertIsNotNone(
                        result_item, 
                        f"Ожидался предмет, но вернулся None (Case: {case['id']})"
                    )
                    
                    # Проверяем Класс (Rings/Amulets)
                    self.assertEqual(
                        result_item.item_class, 
                        case["expected_class"],
                        f"Неверный класс предмета в кейсе {case['id']}"
                    )

                    # Проверяем Теги (Самое важное!)
                    # Используем assertCountEqual, чтобы порядок тегов не имел значения
                    self.assertCountEqual(
                        result_item.tags, 
                        case["expected_tags"],
                        f"Набор тегов не совпал в кейсе {case['id']}"
                    )
                    
                    print(f"   [OK] {case['id']}")

if __name__ == "__main__":
    unittest.main()
