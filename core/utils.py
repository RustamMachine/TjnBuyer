import time
import keyboard
import pyautogui
import mss
import numpy as np
from colorama import init, Fore, Style

init(autoreset=True)

print(f"{Fore.CYAN}--- Tujen & Recombinator Calibrator v2.0 ---{Style.RESET_ALL}")

def get_pixel_data():
    x, y = pyautogui.position()
    with mss.mss() as sct:
        monitor = {"top": y - 5, "left": x - 5, "width": 10, "height": 10}
        img = np.array(sct.grab(monitor))
        brightness = np.mean(img[:, :, :3])
        pixel_bgr = img[5, 5] 
        pixel_rgb = (pixel_bgr[2], pixel_bgr[1], pixel_bgr[0])
    return x, y, pixel_rgb, brightness

def calibrate_buttons():
    results = {}
    steps = [
        ("REROLL_BTN", "Наведи на кнопку 'Reroll'"),
        ("BUY_BTN", "Наведи на кнопку 'Buy'"),
        ("TAKE_ITEM_BTN", "Наведи на кнопку 'Take Item'")
    ]
    print(f"\n{Fore.YELLOW}=== ЭТАП 1: КНОПКИ ТУДЖИНА ==={Style.RESET_ALL}")
    for key, instruction in steps:
        print(f"> {instruction} -> Жми 'C'")
        keyboard.wait('c')
        time.sleep(0.3)
        x, y, rgb, _ = get_pixel_data()
        results[f"{key}_COORDS"] = (x, y)
        print(f"   [OK] {key}: {x}, {y}")
    return results

def calibrate_recomb():
    """Калибровка для Рекомбинатора"""
    results = {}
    print(f"\n{Fore.YELLOW}=== ЭТАП 3: ИНВЕНТАРЬ И РЕКОМБИНАТОР ==={Style.RESET_ALL}")
    
    # 1. Инвентарь
    print("\n1. Наведи на САМЫЙ ПЕРВЫЙ слот инвентаря (Левый Верхний) -> Жми 'C'")
    keyboard.wait('c')
    time.sleep(0.3)
    x1, y1, _, _ = get_pixel_data()
    print(f"   TL: {x1}, {y1}")

    print("\n2. Наведи на САМЫЙ ПОСЛЕДНИЙ слот инвентаря (Правый Нижний, 60-й) -> Жми 'C'")
    keyboard.wait('c')
    time.sleep(0.3)
    x2, y2, _, _ = get_pixel_data()
    print(f"   BR: {x2}, {y2}")
    
    results["PLAYER_INVENTORY_TOP_LEFT"] = (x1, y1)
    results["PLAYER_INVENTORY_BOTTOM_RIGHT"] = (x2, y2)

    # 2. Кнопка Combine
    print("\n3. Наведи на кнопку 'COMBINE' в рекомбинаторе -> Жми 'C'")
    keyboard.wait('c')
    time.sleep(0.3)
    xc, yc, _, _ = get_pixel_data()
    results["RECOMB_BTN_COMBINE_COORDS"] = (xc, yc)
    
    # 3. Слот результата
    print("\n4. Наведи на СЛОТ РЕЗУЛЬТАТА (центр) -> Жми 'C'")
    keyboard.wait('c')
    time.sleep(0.3)
    xr, yr, _, _ = get_pixel_data()
    results["RECOMB_OUTPUT_SLOT"] = (xr, yr)

    return results

def print_config(tujen_btns=None, recomb_data=None):
    print(f"\n{Fore.MAGENTA}=== COPY TO config.py ==={Style.RESET_ALL}\n")
    
    if tujen_btns:
        for k, v in tujen_btns.items():
            print(f"{k} = {v}")
            
    if recomb_data:
        print("\n# === PLAYER INVENTORY ===")
        print(f"PLAYER_INVENTORY_TOP_LEFT = {recomb_data['PLAYER_INVENTORY_TOP_LEFT']}")
        print(f"PLAYER_INVENTORY_BOTTOM_RIGHT = {recomb_data['PLAYER_INVENTORY_BOTTOM_RIGHT']}")
        print("\n# Генератор сетки (вставьте функцию generate_inventory_grid из чата выше)")
        print("PLAYER_INVENTORY_GRID = generate_inventory_grid(PLAYER_INVENTORY_TOP_LEFT, PLAYER_INVENTORY_BOTTOM_RIGHT)")
        
        print("\n# === RECOMBINATOR ===")
        print(f"RECOMB_BTN_COMBINE_COORDS = {recomb_data['RECOMB_BTN_COMBINE_COORDS']}")
        print(f"RECOMB_OUTPUT_SLOT = {recomb_data['RECOMB_OUTPUT_SLOT']}")

if __name__ == "__main__":
    while True:
        print("\nМЕНЮ:")
        print("1. Калибровка Туджина (Кнопки)")
        print("2. Калибровка Рекомбинатора (Инвентарь + Кнопки)")
        print("3. Тест яркости")
        print("4. Выход")
        
        c = input("Выбор: ")
        
        if c == '1':
            btns = calibrate_buttons()
            print_config(tujen_btns=btns)
        elif c == '2':
            data = calibrate_recomb()
            print_config(recomb_data=data)
        elif c == '3':
            # (Тут код test_brightness из старого файла, можно оставить)
            pass 
        elif c == '4':
            break