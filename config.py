"""
Конфигурация бота Tujen-Auto-Buyer v4 (Guard V8).
"""

# === SYSTEM & DEBUG ===
DEBUG_MODE = True
SAVE_DEBUG_SCREENSHOTS = True
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

# Trigger 2: ЯРКОСТЬ (Для белой валюты)
# Теперь это КОМБИНИРОВАННЫЙ триггер.
# Предмет должен быть Ярким (B > 58) ...
MIN_BRIGHTNESS_TRIGGER = 58.0
# ... И при этом иметь хоть какой-то цвет (S > 6), чтобы не путать с бликами.
MIN_SATURATION_FOR_BRIGHT_TRIGGER = 6.0

# Trigger 3: ПОЛ (Защита от пустоты)
MIN_ABSOLUTE_BRIGHTNESS = 11.0


# === TIMINGS & MOUSE (TURBO) ===
TIME_CLICK_HOLD = (0.05, 0.01)     
TIME_BETWEEN_ACTIONS = (0.06, 0.02) 
TIME_REROLL_ANIMATION = 0.45
DELAY_POPUP_OPEN = 0.15   
DELAY_AFTER_TAKE = 0.15   

AFK_INTERVAL_MINUTES = (11, 27) 
AFK_DURATION_SECONDS = (25, 93)
CHANCE_TO_THINK = 0.05      
TIME_THINKING = (0.8, 0.3)  

MOUSE_SPEED_FACTOR = 0.12  
MOUSE_DRIFT_RADIUS = 10