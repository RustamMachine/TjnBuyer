"""
Конфигурация бота Tujen-Auto-Buyer v4 (Guard V8) + Recombinator.
"""
# === PLAYER INVENTORY (60 SLOTS) ===
# Сетка 12 колонок x 5 строк
# Координаты ПЕРВОГО слота (0,0) - Левый верхний
PLAYER_INVENTORY_TOP_LEFT = (1729, 826) # Пример для 2560x1440
# Координаты ПОСЛЕДНЕГО слота (11,4) - Правый нижний
PLAYER_INVENTORY_BOTTOM_RIGHT = (2505, 1106) # Пример для 2560x1440

def generate_inventory_grid(top_left, bottom_right, cols=12, rows=5):
    """Генерирует список из 60 координат центров ячеек."""
    x1, y1 = top_left
    x2, y2 = bottom_right
    
    # Шаг сетки
    step_x = (x2 - x1) / (cols - 1)
    step_y = (y2 - y1) / (rows - 1)
    
    grid = []
    for r in range(rows):
        for c in range(cols):
            x = int(x1 + c * step_x)
            y = int(y1 + r * step_y)
            grid.append((x, y))
    return grid

# Список из 60 кортежей (x, y)
PLAYER_INVENTORY_GRID = generate_inventory_grid(
    PLAYER_INVENTORY_TOP_LEFT, 
    PLAYER_INVENTORY_BOTTOM_RIGHT
)






# === SYSTEM & DEBUG ===
DEBUG_MODE = True
SAVE_DEBUG_SCREENSHOTS = False
DEBUG_SCREENSHOT_PATH = r"C:\TujenScreen"

# === КООРДИНАТЫ ТУДЖИНА (X, Y) ===
REROLL_BTN_COORDS = (1275, 1183)
BUY_BTN_COORDS = (882, 1004)
TAKE_ITEM_BTN_COORDS = (622, 977)

# Сетка товаров Туджина (8-10 слотов)
INVENTORY_GRID = [
    (448, 403), (452, 470), (448, 538), (451, 612), 
    (451, 679), (452, 742), (451, 821), (450, 886)
]

# === VISION V5 (PRECISION) ===
ANALYSIS_BOX_SIZE = 36
REROLL_COLOR_TOLERANCE = 15 

# === ЛОГИКА "ИЛИ" (GUARDED) ===

# Trigger 1: ЦВЕТ (Для цветных вещей)
MIN_SATURATION_TRIGGER = 20.0

# ГЛОБАЛЬНЫЙ ФИЛЬТР НАСЫЩЕННОСТИ
# Если S < 8.0, предмет считается бликом и игнорируется.
MIN_SATURATION_FOR_BRIGHT_TRIGGER = 8.0

# Trigger 2: ЯРКОСТЬ (Для белой валюты)
MIN_BRIGHTNESS_TRIGGER = 58.0

# Trigger 3: СУММА (Финальная проверка)
MIN_SUM_TRIGGER = 60.0

# Trigger 4: ПОЛ (Защита от пустоты)
MIN_ABSOLUTE_BRIGHTNESS = 11.0


# === TIMINGS & MOUSE (TURBO) ===
TIME_CLICK_HOLD = (0.05, 0.01)     
TIME_BETWEEN_ACTIONS = (0.06, 0.02) 
TIME_REROLL_ANIMATION = 0.35
DELAY_POPUP_OPEN = 0.15   
DELAY_AFTER_TAKE = 0.15   

AFK_INTERVAL_MINUTES = (11, 27) 
AFK_DURATION_SECONDS = (25, 93)
CHANCE_TO_THINK = 0.05      
TIME_THINKING = (0.8, 0.3)  

MOUSE_SPEED_FACTOR = 0.12  
MOUSE_DRIFT_RADIUS = 10

# === RECOMBINATOR SETTINGS ===

# 1. Области списка модов (ROI - Region of Interest)
# Формат: (Left, Top, Right, Bottom)
RECOMB_ITEM_A_ROI = (65, 209, 821, 563)   # Левая панель
RECOMB_ITEM_B_ROI = (1301, 209, 2040, 563) # Правая панель

# 2. Область сообщения об ошибке ("Recombination Failed")
RECOMB_FAIL_MSG_ROI = (870, 761, 1277, 839)

# 3. Кнопки и Слоты
# Кнопка "Combine" (Центр кнопки)
RECOMB_BTN_COMBINE_COORDS = (1064, 560)

# Слот результата (Центр слота, куда падает предмет)
RECOMB_OUTPUT_SLOT = (1063, 420)

# 4. Пороги
# Порог яркости для проверки наличия предмета в слоте результата.
# Если яркость > 30, значит предмет есть (успех). Иначе - пусто (провал).
RECOMB_RESULT_BRIGHTNESS_THRESHOLD = 20.0

# Порог яркости для проверки "Пустой ли слот инвентаря?"
# Если яркость < 15, считаем слот пустым и не тратим время на Ctrl+C
MIN_INVENTORY_SLOT_BRIGHTNESS = 15.0


# ==========================================
# НАСТРОЙКИ МЫШИ И ВВОДА (Input Settings)
# ==========================================

# Множитель скорости мыши. 
# 1.0 = стандартная скорость. 
# 2.0 = в 2 раза быстрее. 
# 0.5 = в 2 раза медленнее.
MOUSE_SPEED_FACTOR = 1.5 

# Время удерживания кнопки мыши при клике (Среднее, Разброс)
# Имитирует человеческое нажатие
TIME_CLICK_HOLD = (0.06, 0.015) 

# Пауза между действиями (Среднее, Разброс)
TIME_BETWEEN_ACTIONS = (0.08, 0.02) 

# Радиус случайного смещения для функции дрейфа (если используется)
MOUSE_DRIFT_RADIUS = 4 

# Координаты кнопки реролла (нужны для input_handler, даже если не используются в рекомбинаторе)
# Можно поставить заглушку, если крафтим только рекомбинатором
REROLL_BTN_COORDS = (0, 0)