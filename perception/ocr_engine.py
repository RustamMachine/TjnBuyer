import cv2
import numpy as np
import pytesseract
from typing import Tuple, Optional, List

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
        Подготовка изображения: BGRA fix -> Max Channel -> Upscale -> Normalize -> Threshold
        """
        # 1. Защита от BGRA (mss отдает 4 канала, np.max ломается об Alpha=255)
        if len(image.shape) == 3 and image.shape[2] == 4:
            image = image[:, :, :3]

        # 2. Max Channel (лучший способ для белого текста)
        if len(image.shape) == 3:
            gray = np.max(image, axis=2)
        else:
            gray = image

        # 3. Upscale (для улучшения распознавания мелкого шрифта PoE)
        gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        
        # 4. Normalize & Threshold
        gray = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
        _, thresh = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)
        thresh = cv2.bitwise_not(thresh) # Tesseract любит черный текст на белом
        
        return thresh

    def find_text_coordinates(
        self, 
        image: np.array, 
        target_text: str, 
        offset: Tuple[int, int] = (0, 0)
    ) -> Optional[Tuple[int, int]]:
        """
        Ищет ФРАЗУ целиком и возвращает центр.
        """
        preprocessed = self.preprocess_image(image)
        
        # Получаем данные детально (слова + координаты)
        data = pytesseract.image_to_data(preprocessed, output_type=pytesseract.Output.DICT, config='--psm 6')
        
        n_boxes = len(data['text'])
        
        # Очищаем данные от пустых блоков (Tesseract часто выдает пустоты)
        valid_indices = [i for i in range(n_boxes) if data['text'][i].strip()]
        
        target_words = target_text.lower().split()
        if not target_words:
            return None
        
        target_len = len(target_words)

        # Проходим по всем найденным словам
        for i in range(len(valid_indices)):
            # Если слов осталось меньше, чем в искомой фразе - выход
            if i + target_len > len(valid_indices):
                break
            
            # Проверяем совпадение последовательности слов
            match = True
            current_sequence_indices = []
            
            for k in range(target_len):
                idx_in_data = valid_indices[i + k]
                found_word = data['text'][idx_in_data].lower().strip()
                expected_word = target_words[k]
                
                # Нечеткое сравнение: искомое слово должно быть частью найденного
                # (чтобы игнорировать знаки препинания, например "Level:" содержит "level")
                if expected_word not in found_word:
                    match = False
                    break
                
                current_sequence_indices.append(idx_in_data)
            
            if match:
                # Фраза найдена! Считаем общий Bounding Box для всей фразы.
                
                # Берем координаты первого слова
                first_idx = current_sequence_indices[0]
                last_idx = current_sequence_indices[-1]
                
                # Координаты на увеличенном изображении (x2)
                x1 = data['left'][first_idx]
                y1 = data['top'][first_idx]
                
                # Правый нижний угол последнего слова
                x2 = data['left'][last_idx] + data['width'][last_idx]
                y2 = data['top'][last_idx] + data['height'][last_idx]
                
                # Центр прямоугольника фразы
                center_x_2x = (x1 + x2) // 2
                center_y_2x = (y1 + y2) // 2
                
                # Возвращаем к масштабу 1:1
                orig_x = int(center_x_2x / 2)
                orig_y = int(center_y_2x / 2)
                
                # Добавляем глобальное смещение
                global_x = orig_x + offset[0]
                global_y = orig_y + offset[1]
                
                return (global_x, global_y)

        return None