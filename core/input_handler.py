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

def smooth_move(target_x, target_y, speed_mult=1.0, drift_radius=None):
    """
    Плавное перемещение с кривыми Безье и случайным смещением (Drift).
    
    Args:
        target_x, target_y: Целевые координаты (идеальные).
        speed_mult: Множитель скорости (>1 быстрее).
        drift_radius: Если None, берется из config.MOUSE_DRIFT_RADIUS. 
                      Если 0, точное наведение.
    """
    start_x, start_y = pydirectinput.position()
    
    # Определяем радиус смещения
    if drift_radius is None:
        drift_radius = config.MOUSE_DRIFT_RADIUS
        
    # Применяем смещение к конечной точке (Anti-Bot)
    if drift_radius > 0:
        offset_x = random.randint(-drift_radius, drift_radius)
        offset_y = random.randint(-drift_radius, drift_radius)
        dest_x = target_x + offset_x
        dest_y = target_y + offset_y
    else:
        dest_x = target_x
        dest_y = target_y
    
    dist = math.hypot(dest_x - start_x, dest_y - start_y)
    
    # Если расстояние совсем маленькое, просто прыгаем
    if dist < 15:
        pydirectinput.moveTo(dest_x, dest_y)
        return

    # Рассчитываем количество шагов
    base_speed = config.MOUSE_SPEED_FACTOR / speed_mult
    steps = int(dist / (25 * speed_mult)) + 2
    if steps < 2: steps = 2
    
    for i in range(steps):
        t = (i + 1) / steps
        # Ease Out (замедление в конце)
        ease_t = t * (2 - t) 
        
        next_x = int(start_x + (dest_x - start_x) * ease_t)
        next_y = int(start_y + (dest_y - start_y) * ease_t)
        
        pydirectinput.moveTo(next_x, next_y)
        
        # Микро-паузы между шагами
        sleep_time = random.uniform(0.005, 0.008) * base_speed
        if sleep_time < 0.001: sleep_time = 0.001
        time.sleep(sleep_time)
        
    # Финальная доводка
    pydirectinput.moveTo(dest_x, dest_y)

# --- АЛИАС ДЛЯ СОВМЕСТИМОСТИ ---
move_smooth = smooth_move 

def release_all_modifiers():
    """
    Принудительно отпускает все модификаторы.
    """
    for key in ['ctrl', 'alt', 'shift']:
        pydirectinput.keyUp(key)

def human_click(coords=None, key_modifier=None, drift_override=None):
    """
    Клик с поддержкой модификаторов и настройки смещения.
    """
    if coords:
        # smooth_move сама применит глобальный MOUSE_DRIFT_RADIUS,
        # если мы не передадим drift_override явно.
        smooth_move(coords[0], coords[1], drift_radius=drift_override)
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
    Специальный клик для больших кнопок (можно использовать больший разброс).
    """
    base_x, base_y = config.REROLL_BTN_COORDS
    # Для кнопки реролла можно безопасно увеличить разброс, так как она большая
    human_click((base_x, base_y), drift_override=config.MOUSE_DRIFT_RADIUS * 2)

def copy_item_data():
    """
    Копирует данные предмета.
    Сначала ОЧИЩАЕТ буфер обмена, чтобы избежать чтения старых данных (фантомные предметы).
    """
    # 1. Очистка буфера (защита от "старого" текста)
    try:
        pyperclip.copy("") 
    except Exception:
        pass # Если вдруг не вышло, не страшно, попробуем переписать

    # 2. Нажатие Ctrl + Alt + C
    pydirectinput.keyDown('ctrl')
    pydirectinput.keyDown('alt')
    time.sleep(0.03) # Чуть увеличил паузу
    pydirectinput.press('c')
    time.sleep(0.03)
    pydirectinput.keyUp('alt')
    pydirectinput.keyUp('ctrl')
    
    # 3. Ожидание обновления буфера системой
    # Увеличил с 0.05 до 0.1, так как 50мс иногда мало для PoE
    time.sleep(0.1)
    
    try:
        data = pyperclip.paste()
        # Если вернулась пустая строка - значит копирование не удалось
        return data
    except Exception:
        return ""