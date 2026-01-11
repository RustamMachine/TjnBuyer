"""
Конфигурация бота Tujen-Auto-Buyer v4 (Guard V8) + Recombinator.
"""
# === LOGGING SETTINGS ===
DETAILED_LOGGING = True  # True для отладки, False для обычной работы

# ==========================================
# 1. КООРДИНАТЫ И ГРИДЫ (Coordinates)
# ==========================================

# --- СЕТКА ИНВЕНТАРЯ ИГРОКА (60 Слотов) ---
# Используется рекомбинатором для перемещения предметов
PLAYER_INVENTORY_TOP_LEFT = (1729, 826) 
PLAYER_INVENTORY_BOTTOM_RIGHT = (2505, 1106)

def generate_inventory_grid(top_left, bottom_right, cols=12, rows=5):
    """Генерирует список из 60 координат центров ячеек."""
    x1, y1 = top_left
    x2, y2 = bottom_right
    step_x = (x2 - x1) / (cols - 1)
    step_y = (y2 - y1) / (rows - 1)
    grid = []
    for r in range(rows):
        for c in range(cols):
            x = int(x1 + c * step_x)
            y = int(y1 + r * step_y)
            grid.append((x, y))
    return grid

PLAYER_INVENTORY_GRID = generate_inventory_grid(
    PLAYER_INVENTORY_TOP_LEFT, 
    PLAYER_INVENTORY_BOTTOM_RIGHT
)

# --- СЕТКА ТОВАРОВ ТУДЖИНА (Tujen Shop Grid) ---
# Используется шоппинг-экзекьютором для анализа товаров
INVENTORY_GRID = [
    (448, 403), (452, 470), (448, 538), (451, 612), 
    (451, 679), (452, 742), (451, 821), (450, 886)
]

# --- КНОПКИ ТУДЖИНА ---
REROLL_BTN_COORDS = (1275, 1183)
BUY_BTN_COORDS = (882, 1004)
TAKE_ITEM_BTN_COORDS = (622, 977)

# ==========================================
# 2. НАСТРОЙКИ РЕКОМБИНАТОРА (Recombinator)
# ==========================================

# Области списка модов (ROI)
RECOMB_ITEM_A_ROI = (65, 209, 821, 563)
RECOMB_ITEM_B_ROI = (1301, 209, 2040, 563)

# Сообщение об ошибке
RECOMB_FAIL_MSG_ROI = (870, 761, 1277, 839)

# Кнопки и слоты рекомбинатора
RECOMB_BTN_COMBINE_COORDS = (1064, 560)
RECOMB_OUTPUT_SLOT = (1063, 420)

# Слоты для возврата предметов (при ошибке)
# Примерные координаты! Проверьте их.
RECOMB_INPUT_SLOT_A = (860, 420)  
RECOMB_INPUT_SLOT_B = (1270, 420)

# Пороги яркости
RECOMB_RESULT_BRIGHTNESS_THRESHOLD = 20.0
MIN_INVENTORY_SLOT_BRIGHTNESS = 15.0

# ==========================================
# 3. НАСТРОЙКИ ЗРЕНИЯ (Vision & Triggers)
# ==========================================

# Для Shopping Executor
ANALYSIS_BOX_SIZE = 36
REROLL_COLOR_TOLERANCE = 15 

# Триггеры покупки (Guard V8 Logic)
MIN_SATURATION_TRIGGER = 20.0
MIN_SATURATION_FOR_BRIGHT_TRIGGER = 8.0
MIN_BRIGHTNESS_TRIGGER = 58.0
MIN_SUM_TRIGGER = 60.0
MIN_ABSOLUTE_BRIGHTNESS = 11.0

# ==========================================
# 4. ТАЙМИНГИ И AFK (Timings)
# ==========================================

# Мышь и клики
MOUSE_SPEED_FACTOR = 1.5 
TIME_CLICK_HOLD = (0.06, 0.015) 
TIME_BETWEEN_ACTIONS = (0.08, 0.02) 

# Anti-Bot Drift (случайное смещение мыши)
MOUSE_DRIFT_RADIUS = 4 

# Тайминги Туджина
TIME_REROLL_ANIMATION = 0.35
DELAY_POPUP_OPEN = 0.15   
DELAY_AFTER_TAKE = 0.15   

# Имитация раздумий (Humanizing)
CHANCE_TO_THINK = 0.05      
TIME_THINKING = (0.8, 0.3)  

# AFK система (Паузы в работе)
# Интервал между перерывами в минутах (мин, макс)
AFK_INTERVAL_MINUTES = (11, 27) 
# Длительность перерыва в секундах (мин, макс)
AFK_DURATION_SECONDS = (25, 93)

# ==========================================
# 5. СИСТЕМНЫЕ НАСТРОЙКИ (System)
# ==========================================
DEBUG_MODE = True
SAVE_DEBUG_SCREENSHOTS = False
DEBUG_SCREENSHOT_PATH = r"C:\TujenScreen"