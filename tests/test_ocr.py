import unittest
import os
import cv2
import shutil
from perception.ocr_engine import OCREngine
import config.config as config

REAL_TEST_CASES = [
    {
        "file": "amulets/melee_magic_vs_spirit.png",
        "item_a_search": "Melee Skills",
        "item_b_search": "Spirit"
    },
    {
        "file": "amulets/melee_vs_spirit_magic.png",
        "item_a_search": "Melee Skills",
        "item_b_search": "Spirit"
    },
    # --- НОВЫЙ КЕЙС ---
    {
        "file": "amulets/spirit_minion1_vs_minion.png",
        # Слева ищем ТОЛЬКО Spirit (хотя там есть и Minion T3, мы его игнорируем)
        "item_a_search": "Spirit", 
        # Справа ищем Minion (Т1)
        "item_b_search": "Minion Skills"
    },
    # ------------------
    {
        "file": "rings/cold_vs_lightning_phys.png",
        "item_a_search": "Cold damage",
        "item_b_search": "Lightning damage"
    }
]

class TestOCR(unittest.TestCase):
    def setUp(self):
        self.ocr = OCREngine()
        self.debug_dir = os.path.join("tests", "debug_ocr")
        if os.path.exists(self.debug_dir):
            shutil.rmtree(self.debug_dir)
        os.makedirs(self.debug_dir)

    def test_global_coordinates(self):
        print(f"\n=== GLOBAL COORDINATES TEST (Saved to {self.debug_dir}) ===")
        
        for case in REAL_TEST_CASES:
            rel_path = os.path.join("tests", "fixtures", "screenshots", case["file"])
            if not os.path.exists(rel_path):
                continue
                
            full_img = cv2.imread(rel_path)
            # Копия для рисования результата
            debug_full_img = full_img.copy()
            
            filename = os.path.basename(case["file"]).replace(".png", "")

            # --- ITEM A (LEFT) ---
            # 1. Вырезаем
            roi_a = config.RECOMB_ITEM_A_ROI
            crop_a = self.ocr.crop_image(full_img, roi_a)
            
            # 2. Ищем с учетом смещения (передаем roi_a[0], roi_a[1])
            # offset=(Left, Top)
            coords_a = self.ocr.find_text_coordinates(
                crop_a, 
                case["item_a_search"], 
                offset=(roi_a[0], roi_a[1])
            )
            
            if coords_a:
                gx, gy = coords_a
                # Рисуем КРЕСТИК на полном скрине
                # Это доказывает, что координаты глобальные
                cv2.drawMarker(debug_full_img, (gx, gy), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=3)
                print(f"[{filename}] Left Global: ({gx}, {gy}) -> OK")
            else:
                print(f"[{filename}] Left: NOT FOUND")

            # --- ITEM B (RIGHT) ---
            roi_b = config.RECOMB_ITEM_B_ROI
            crop_b = self.ocr.crop_image(full_img, roi_b)
            
            coords_b = self.ocr.find_text_coordinates(
                crop_b, 
                case["item_b_search"], 
                offset=(roi_b[0], roi_b[1])
            )
            
            if coords_b:
                gx, gy = coords_b
                cv2.drawMarker(debug_full_img, (gx, gy), (0, 255, 0), markerType=cv2.MARKER_CROSS, markerSize=20, thickness=3)
                print(f"[{filename}] Right Global: ({gx}, {gy}) -> OK")
            else:
                print(f"[{filename}] Right: NOT FOUND")

            # Сохраняем полный скриншот с пометками
            cv2.imwrite(os.path.join(self.debug_dir, f"{filename}_GLOBAL_RESULT.png"), debug_full_img)

if __name__ == "__main__":
    unittest.main()