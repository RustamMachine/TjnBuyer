import time
import random
import math
import pydirectinput
import pyperclip
import config.config as config

pydirectinput.PAUSE = 0

def sleep_gauss(mean, sigma):
    """
    Спит случайное время по нормальному распределению (Гаусс).
    Никогда не спит меньше 0.01 сек.
    """
    val = random.gauss(mean, sigma)
    if val < 0.01: val = 0.01
    time.sleep(val)

def smooth_move(target_x, target_y, speed_mult=1.0):
    """
    Плавное перемещение с кривыми Безье.
    speed_mult > 1.0 делает движение быстрее.
    """
    start_x, start_y = pydirectinput.position()
    
    # Добавляем микро-рандом к конечной точке
    dest_x = target_x + random.randint(-1, 1)
    dest_y = target_y + random.randint(-1, 1)
    
    dist = math.hypot(dest_x - start_x, dest_y - start_y)
    
    if dist < 15:
        pydirectinput.moveTo(dest_x, dest_y)
        return

    # Количество шагов
    base_speed = config.MOUSE_SPEED_FACTOR / speed_mult
    steps = int(dist / (25 * speed_mult)) + 2
    if steps < 2: steps = 2
    
    for i in range(steps):
        t = (i + 1) / steps
        ease_t = t * (2 - t) # Ease Out
        
        next_x = int(start_x + (dest_x - start_x) * ease_t)
        next_y = int(start_y + (dest_y - start_y) * ease_t)
        
        pydirectinput.moveTo(next_x, next_y)
        sleep_time = random.uniform(0.005, 0.008) * base_speed
        if sleep_time < 0.001: sleep_time = 0.001
        time.sleep(sleep_time)
        
    pydirectinput.moveTo(dest_x, dest_y)

# --- АЛИАС ДЛЯ СОВМЕСТИМОСТИ (чтобы не ломать старый код) ---
move_smooth = smooth_move 

def release_all_modifiers():
    """
    Принудительно отпускает все модификаторы.
    """
    for key in ['ctrl', 'alt', 'shift']:
        pydirectinput.keyUp(key)

def human_click(coords=None, key_modifier=None):
    """
    Клик с поддержкой модификаторов.
    """
    if coords:
        smooth_move(coords[0], coords[1])
        sleep_gauss(0.05, 0.01)

    if key_modifier:
        pydirectinput.keyDown(key_modifier)
        time.sleep(random.uniform(0.05, 0.1))

    pydirectinput.mouseDown()
    sleep_gauss(*config.TIME_CLICK_HOLD)
    pydirectinput.mouseUp()
    
    if key_modifier:
        time.sleep(random.uniform(0.05, 0.1))
        pydirectinput.keyUp(key_modifier)
    
    sleep_gauss(*config.TIME_BETWEEN_ACTIONS)

def click_reroll_with_drift():
    """
    Кликает по кнопке Реролла со смещением.
    """
    base_x, base_y = config.REROLL_BTN_COORDS
    
    offset_x = random.randint(-config.MOUSE_DRIFT_RADIUS, config.MOUSE_DRIFT_RADIUS)
    offset_y = random.randint(-config.MOUSE_DRIFT_RADIUS, config.MOUSE_DRIFT_RADIUS)
    
    target_x = base_x + offset_x
    target_y = base_y + offset_y
    
    smooth_move(target_x, target_y, speed_mult=2.0)
    
    pydirectinput.mouseDown()
    sleep_gauss(*config.TIME_CLICK_HOLD)
    pydirectinput.mouseUp()

def copy_item_data():
    """
    Копирует данные предмета под курсором (Ctrl+C).
    """
    pydirectinput.keyDown('ctrl')
    pydirectinput.press('c')
    pydirectinput.keyUp('ctrl')
    time.sleep(0.05)
    try:
        return pyperclip.paste()
    except Exception:
        return ""