"""
Конфигурация бота Tujen-Auto-Buyer v4 (Guard V8).
"""

# === SYSTEM & DEBUG ===
DEBUG_MODE = True
SAVE_DEBUG_SCREENSHOTS = False
DEBUG_SCREENSHOT_PATH = r"C:\TujenScreen"

# === КООРДИНАТЫ (X, Y) ===
REROLL_BTN_COORDS = (1275, 1183)
BUY_BTN_COORDS = (882, 1004)
TAKE_ITEM_BTN_COORDS = (622, 977)

INVENTORY_GRID = [
    (448, 403), (452, 470), (448, 538), (451, 612), 
    (451, 679), (452, 742), (451, 821), (450, 886)
]

# === VISION V5 (PRECISION) ===
ANALYSIS_BOX_SIZE = 36
REROLL_COLOR_TOLERANCE = 15 

# === ЛОГИКА "ИЛИ" (GUARDED) ===

# Trigger 1: ЦВЕТ (Для цветных вещей)
# Если насыщенность высокая, берем не глядя на яркость.
MIN_SATURATION_TRIGGER = 20.0

# ГЛОБАЛЬНЫЙ ФИЛЬТР НАСЫЩЕННОСТИ
# (Ранее MIN_SATURATION_FOR_BRIGHT_TRIGGER)
# Минимальная насыщенность для ЛЮБОГО срабатывания. 
# Если S < 8.0, предмет считается бликом и игнорируется, 
# даже если проходит по сумме или яркости.
MIN_SATURATION_FOR_BRIGHT_TRIGGER = 8.0

# Trigger 2: ЯРКОСТЬ (Для белой валюты)
# Предмет должен быть ярче этого значения.
MIN_BRIGHTNESS_TRIGGER = 58.0

# Trigger 3: СУММА (Финальная проверка)
# Если предыдущие проверки не прошли, проверяем общую сумму яркости и насыщенности.
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
# Координаты областей, где отображаются списки модов (ROI - Region of Interest)
# Формат: (Left, Top, Right, Bottom)
RECOMB_ITEM_A_ROI = (65, 209, 821, 563)   # Левая панель
RECOMB_ITEM_B_ROI = (1301, 209, 2040, 563) # Правая панель

# Координата кнопки "Combine" (примерная, нужно будет уточнить калибровкой)
RECOMB_BTN_COMBINE_COORDS = (992, 546, 1136, 572) # Заглушка, уточним позже