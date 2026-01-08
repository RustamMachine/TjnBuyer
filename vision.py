import mss
import numpy as np
import cv2
import os
import time
import config
from colorama import Fore, Style

def get_pixel_color(coords):
    x, y = coords
    with mss.mss() as sct:
        monitor = {"top": y, "left": x, "width": 1, "height": 1}
        img = np.array(sct.grab(monitor))
        pixel = img[0, 0]
        return (pixel[2], pixel[1], pixel[0])

def is_reroll_active():
    c = get_pixel_color(config.REROLL_BTN_COORDS)
    r, g, b = int(c[0]), int(c[1]), int(c[2])
    color_diff = max(r, g, b) - min(r, g, b)
    return color_diff > config.REROLL_COLOR_TOLERANCE

def scan_inventory_batch():
    if config.DEBUG_MODE:
        print(f"\n{Fore.CYAN}--- SCAN START (V9 Absolute Sat Check) ---{Style.RESET_ALL}")
    
    found_items = []
    half_size = config.ANALYSIS_BOX_SIZE // 2
    
    xs = [p[0] for p in config.INVENTORY_GRID]
    ys = [p[1] for p in config.INVENTORY_GRID]
    min_x, max_x = min(xs) - 40, max(xs) + 40
    min_y, max_y = min(ys) - 40, max(ys) + 40
    full_monitor = {"top": min_y, "left": min_x, "width": max_x - min_x, "height": max_y - min_y}
    
    with mss.mss() as sct:
        debug_img = None
        if config.SAVE_DEBUG_SCREENSHOTS:
            mss_capture = sct.grab(full_monitor)
            debug_img = np.array(mss_capture)
            debug_img = cv2.cvtColor(debug_img, cv2.COLOR_BGRA2BGR)
        
        for i, slot_coords in enumerate(config.INVENTORY_GRID):
            x, y = slot_coords
            monitor = {
                "top": y - half_size, "left": x - half_size, 
                "width": config.ANALYSIS_BOX_SIZE, "height": config.ANALYSIS_BOX_SIZE
            }
            img = np.array(sct.grab(monitor))
            
            avg_brightness = np.mean(img[:, :, :3])
            saturation_map = np.ptp(img[:, :, :3], axis=2)
            avg_saturation = np.mean(saturation_map)
            
            # === ЛОГИКА V9 (ABSOLUTE SAT CHECK) ===
            
            # 1. Защита от пустоты (Пол)
            is_valid_floor = avg_brightness > config.MIN_ABSOLUTE_BRIGHTNESS

            # 2. Глобальная защита от бликов (Абсолютная насыщенность)
            # Если насыщенность ниже порога, предмет игнорируется ПОЛНОСТЬЮ,
            # даже если проходит по сумме или яркости.
            is_valid_global_sat = avg_saturation > config.MIN_SATURATION_FOR_BRIGHT_TRIGGER
            
            # 3. Trigger 1: Чистый цвет
            trigger_sat = avg_saturation > config.MIN_SATURATION_TRIGGER
            
            # 4. Trigger 2: Яркость
            # (Доп. проверка насыщенности здесь убрана, т.к. есть is_valid_global_sat)
            trigger_bright = avg_brightness > config.MIN_BRIGHTNESS_TRIGGER
            
            # 5. Trigger 3: Сумма (B + S)
            trigger_sum = (avg_brightness + avg_saturation) > config.MIN_SUM_TRIGGER
            
            # ИТОГОВОЕ УСЛОВИЕ:
            # (Есть пол) И (Есть минимальный цвет) И (Сработал любой триггер)
            is_match = is_valid_floor and is_valid_global_sat and (trigger_sat or trigger_bright or trigger_sum)
            
            # Логирование
            if config.DEBUG_MODE:
                if is_match:
                    if trigger_sat:
                        reason = f"SAT>{config.MIN_SATURATION_TRIGGER}"
                    elif trigger_bright:
                        reason = f"LUMA>{config.MIN_BRIGHTNESS_TRIGGER}"
                    else:
                        reason = f"SUM>{config.MIN_SUM_TRIGGER}"
                    
                    status_text = f"{Fore.GREEN}MATCH [{reason}]{Style.RESET_ALL}"
                else:
                    # Для отладки покажем, почему пропуск
                    if is_valid_floor and not is_valid_global_sat:
                         status_text = f"{Fore.RED}SKIP [LOW SAT]{Style.RESET_ALL}"
                    else:
                         status_text = f"{Fore.RED}SKIP{Style.RESET_ALL}"
                
                print(f"Slot {i}: B={avg_brightness:5.1f} | S={avg_saturation:5.1f} | Sum={avg_brightness+avg_saturation:5.1f} -> {status_text}")
            
            if is_match:
                found_items.append(slot_coords)

            if config.SAVE_DEBUG_SCREENSHOTS and debug_img is not None:
                local_x = x - min_x
                local_y = y - min_y
                color = (0, 255, 0) if is_match else (0, 0, 255)
                # Если пропуск из-за насыщенности (при высокой яркости), рисуем оранжевым
                if not is_match and is_valid_floor and not is_valid_global_sat:
                    color = (0, 165, 255) # Orange-ish BGR

                cv2.rectangle(debug_img, (local_x - half_size, local_y - half_size), (local_x + half_size, local_y + half_size), color, 2)
                cv2.putText(debug_img, f"B:{int(avg_brightness)}", (local_x - 18, local_y - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
                cv2.putText(debug_img, f"S:{int(avg_saturation)}", (local_x - 18, local_y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (255, 255, 255), 1)
                cv2.putText(debug_img, f"+:{int(avg_brightness+avg_saturation)}", (local_x - 18, local_y + 6), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 255, 255), 1)

        if config.SAVE_DEBUG_SCREENSHOTS and debug_img is not None:
            if not os.path.exists(config.DEBUG_SCREENSHOT_PATH):
                os.makedirs(config.DEBUG_SCREENSHOT_PATH)
            filename = f"scan_{int(time.time()*100)}.png"
            cv2.imwrite(os.path.join(config.DEBUG_SCREENSHOT_PATH, filename), debug_img)
            if config.DEBUG_MODE: print(f"Saved: {filename}")

    if config.DEBUG_MODE:
        print(f"{Fore.CYAN}--- SCAN END ---\n{Style.RESET_ALL}")
        
    return found_items