import cv2
import numpy as np
import pytesseract
from typing import Tuple, Optional, List, Dict

# Укажите путь к Tesseract, если он не в PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class OCREngine:
    def crop_image(self, image: np.array, roi_coords: Tuple[int, int, int, int]) -> np.array:
        """
        Вырезает часть изображения.
        :param roi_coords: (Left, Top, Right, Bottom)
        """
        x1, y1, x2, y2 = roi_coords
        h, w = image.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        return image[y1:y2, x1:x2]

    def preprocess_image(self, image: np.array) -> np.array:
        """
        Подготовка изображения: Max Channel -> Upscale -> Normalize -> Threshold
        """
        if len(image.shape) == 3:
            gray = np.max(image, axis=2)
        else:
            gray = image

        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        _, thresh = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)
        thresh = cv2.bitwise_not(thresh)
        
        return thresh

    def find_text_coordinates(
        self, 
        image: np.array, 
        target_text: str, 
        offset: Tuple[int, int] = (0, 0)
    ) -> Optional[Tuple[int, int]]:
        """
        Ищет текст и возвращает АБСОЛЮТНЫЕ координаты центра (Screen X, Screen Y).
        
        :param image: Вырезанное изображение (Crop).
        :param target_text: Текст для поиска.
        :param offset: (Global_X, Global_Y) - координаты верхнего левого угла кропа.
                       Нужно передать (ROI_Left, ROI_Top), чтобы получить координаты экрана.
        :return: (Global_Screen_X, Global_Screen_Y)
        """
        preprocessed = self.preprocess_image(image)
        
        data = pytesseract.image_to_data(preprocessed, output_type=pytesseract.Output.DICT, config='--psm 6')
        
        n_boxes = len(data['text'])
        target_words = target_text.lower().split()
        if not target_words:
            return None
        
        first_target_word = target_words[0]

        for i in range(n_boxes):
            word_found = data['text'][i].lower().strip()
            if not word_found:
                continue
            
            if first_target_word in word_found:
                # Координаты внутри увеличенного (x2) изображения
                x, y, w, h = data['left'][i], data['top'][i], data['width'][i], data['height'][i]
                
                # Возвращаем к масштабу 1:1
                orig_x = int(x / 2)
                orig_y = int(y / 2)
                orig_w = int(w / 2)
                orig_h = int(h / 2)
                
                # Центр относительно кропа
                center_crop_x = orig_x + orig_w // 2
                center_crop_y = orig_y + orig_h // 2
                
                # Добавляем глобальное смещение (координаты экрана)
                global_x = center_crop_x + offset[0]
                global_y = center_crop_y + offset[1]
                
                return (global_x, global_y)

        return None