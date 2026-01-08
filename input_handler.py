import time
import random
import math
import pydirectinput
import config

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
    """
    start_x, start_y = pydirectinput.position()
    
    # Добавляем микро-рандом к конечной точке (анти-пиксель-перфект)
    dest_x = target_x + random.randint(-2, 2)
    dest_y = target_y + random.randint(-2, 2)
    
    dist = math.hypot(dest_x - start_x, dest_y - start_y)
    
    if dist < 10:
        pydirectinput.moveTo(dest_x, dest_y)
        return

    # Количество шагов
    base_speed = config.MOUSE_SPEED_FACTOR / speed_mult
    steps = int(dist / 25) + 2
    
    for i in range(steps):
        t = (i + 1) / steps
        ease_t = t * (2 - t) # Ease Out
        
        next_x = int(start_x + (dest_x - start_x) * ease_t)
        next_y = int(start_y + (dest_y - start_y) * ease_t)
        
        pydirectinput.moveTo(next_x, next_y)
        time.sleep(random.uniform(0.005, 0.008) * base_speed)
        
    pydirectinput.moveTo(dest_x, dest_y)

def human_click(coords=None):
    """
    Клик. Если переданы координаты - сначала едет туда.
    Использует гауссовы тайминги.
    """
    if coords:
        smooth_move(coords[0], coords[1])
        # Пауза прицеливания (маленькая, рука набита)
        sleep_gauss(0.06, 0.01)

    pydirectinput.mouseDown()
    sleep_gauss(*config.TIME_CLICK_HOLD)
    pydirectinput.mouseUp()
    
    sleep_gauss(*config.TIME_BETWEEN_ACTIONS)

def click_reroll_with_drift():
    """
    Кликает по кнопке Реролла, но не в одну точку, а создавая 'пятно' (Drift).
    Не уводит мышь далеко.
    """
    base_x, base_y = config.REROLL_BTN_COORDS
    
    # Генерируем точку внутри радиуса дрейфа
    # Это создает видимость, что рука чуть дрожит/смещается, но остается на кнопке
    offset_x = random.randint(-config.MOUSE_DRIFT_RADIUS, config.MOUSE_DRIFT_RADIUS)
    offset_y = random.randint(-config.MOUSE_DRIFT_RADIUS, config.MOUSE_DRIFT_RADIUS)
    
    target_x = base_x + offset_x
    target_y = base_y + offset_y
    
    # Очень быстрое микро-движение (корректировка позиции)
    smooth_move(target_x, target_y, speed_mult=2.0)
    
    pydirectinput.mouseDown()
    sleep_gauss(*config.TIME_CLICK_HOLD)
    pydirectinput.mouseUp()