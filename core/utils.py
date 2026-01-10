import time
import keyboard
import pyautogui
import mss
import numpy as np
from colorama import init, Fore, Style

# Инициализация для цветного текста в консоли
init(autoreset=True)

print(f"{Fore.CYAN}--- Tujen Bot Calibrator v1.0 ---{Style.RESET_ALL}")
print("Этот скрипт поможет собрать координаты и цвета для config.py")
print("Убедись, что игра запущена в Windowed или Borderless режиме.")

def get_pixel_data():
    """Захватывает цвет и яркость под курсором мыши."""
    x, y = pyautogui.position()
    with mss.mss() as sct:
        # Захватываем маленькую область 10x10 вокруг мыши для яркости
        monitor = {"top": y - 5, "left": x - 5, "width": 10, "height": 10}
        img = np.array(sct.grab(monitor))
        
        # Считаем среднюю яркость (простое среднее по всем каналам)
        # img shape is (10, 10, 4) -> BGRA
        brightness = np.mean(img[:, :, :3]) # Берем только BGR, без Alpha

        # Захватываем точный цвет центрального пикселя для кнопок
        # mss возвращает BGRA, нам нужен RGB
        pixel_bgr = img[5, 5] 
        pixel_rgb = (pixel_bgr[2], pixel_bgr[1], pixel_bgr[0])
        
    return x, y, pixel_rgb, brightness

def calibrate_buttons():
    """Пошаговый мастер настройки кнопок."""
    results = {}
    steps = [
        ("REROLL_BTN", "Наведи на центр кнопки 'Reroll' (Обновить)"),
        ("BUY_BTN", "Наведи на кнопку 'Buy' (Купить/Confirm)"),
        ("TAKE_ITEM_BTN", "Наведи на кнопку 'Take Item' (Забрать) в окне крафта"),
        ("SAFE_ZONE", "Наведи на безопасное место (пустой фон), где нет всплывающих окон")
    ]

    print(f"\n{Fore.YELLOW}=== ЭТАП 1: КНОПКИ ==={Style.RESET_ALL}")
    print("Наводи мышь и жми 'C' (Capture).")

    for key, instruction in steps:
        print(f"\n> {instruction}")
        keyboard.wait('c') # Ждем нажатия C
        time.sleep(0.3)     # Небольшая пауза
        x, y, rgb, _ = get_pixel_data()
        
        results[f"{key}_COORDS"] = (x, y)
        if key == "REROLL_BTN":
            results[f"{key}_COLOR_ACTIVE"] = rgb # Сохраняем цвет только для реролла
        
        print(f"{Fore.GREEN}   [OK] Записано: {x}, {y}{Style.RESET_ALL}")
        time.sleep(0.5) # Защита от двойного нажатия

    return results

def calibrate_grid():
    """Сбор координат сетки инвентаря."""
    grid_coords = []
    print(f"\n{Fore.YELLOW}=== ЭТАП 2: СЕТКА ТОВАРОВ ==={Style.RESET_ALL}")
    print("Теперь нужно прокликать центры ячеек, где появляются товары.")
    print("Наводи на ячейку -> Жми 'C'.")
    print("Когда закончишь все ячейки -> Жми 'Q' (Quit).")

    while True:
        event = keyboard.read_event()
        if event.event_type == keyboard.KEY_DOWN:
            if event.name == 'c':
                x, y, _, _ = get_pixel_data()
                grid_coords.append((x, y))
                print(f"   Ячейка {len(grid_coords)}: ({x}, {y})")
                time.sleep(0.3)
            elif event.name == 'q':
                break
    
    return grid_coords

def test_brightness():
    """Инструмент для проверки яркости (найти Threshold)."""
    print(f"\n{Fore.YELLOW}=== ТЕСТ ЯРКОСТИ (ESC для выхода) ==={Style.RESET_ALL}")
    print("Наводи на ПОДСВЕЧЕННЫЙ предмет и на ЗАТЕМНЕННЫЙ.")
    print("Смотри на значение 'Brightness'.")
    
    try:
        while True:
            if keyboard.is_pressed('esc'):
                break
            
            x, y, rgb, bright = get_pixel_data()
            status = f"Pos: {x},{y} | RGB: {rgb} | {Fore.WHITE}{Style.BRIGHT}Brightness: {bright:.2f}{Style.RESET_ALL}"
            print(status, end='\r')
            time.sleep(0.3)
    except KeyboardInterrupt:
        pass
    print("\nТест завершен.")

def generate_config_text(buttons, grid):
    """Генерация текста для config.py"""
    print(f"\n{Fore.MAGENTA}========================================{Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}   СКОПИРУЙ ЭТО В config.py   {Style.RESET_ALL}")
    print(f"{Fore.MAGENTA}========================================{Style.RESET_ALL}\n")
    
    print("# Координаты кнопок (x, y)")
    for key, val in buttons.items():
        if "COORDS" in key:
            print(f"{key} = {val}")

    print("\n# Цвет активной кнопки Reroll (R, G, B)")
    if "REROLL_BTN_COLOR_ACTIVE" in buttons:
        print(f"REROLL_BTN_COLOR_ACTIVE = {buttons['REROLL_BTN_COLOR_ACTIVE']}")

    print("\n# Сетка инвентаря")
    print(f"INVENTORY_GRID = {grid}")
    
    print("\n# Настройки")
    print("BRIGHTNESS_THRESHOLD = 60  # <-- Подбери это значение через тест яркости")
    print("REROLL_COLOR_TOLERANCE = 15  # Допустимое отклонение цвета")

# --- Главное меню ---
if __name__ == "__main__":
    while True:
        print("\nМЕНЮ:")
        print("1. Собрать все координаты (Кнопки + Сетка)")
        print("2. Только Тест Яркости (для подбора Threshold)")
        print("3. Выход")
        
        choice = input("Выбор (1-3): ")
        
        if choice == '1':
            btns = calibrate_buttons()
            grid = calibrate_grid()
            generate_config_text(btns, grid)
            break
        elif choice == '2':
            test_brightness()
        elif choice == '3':
            break