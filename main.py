import time
import sys
import os
import random
import keyboard
from colorama import init, Fore, Style

# === ИМПОРТЫ ПРОЕКТА ===
import config.config as config
from core import input_handler

# Импорт логики Туджина (из perception/shopping_vision.py)
# Используем псевдоним vision, чтобы старый код работал без изменений
from perception import shopping_vision as vision

# Импорт логики Рекомбинатора
# (Предполагается, что файл executors/recombinator_executor.py создан)
from executors.recombinator_executor import RecombinatorExecutor

# Инициализация цвета
init(autoreset=True)

def kill_bot():
    """Экстренная остановка бота."""
    print(f"\n{Fore.RED}!!! EMERGENCY STOP (F12) !!!{Style.RESET_ALL}")
    os._exit(0)

# ==========================================
# 1. ЛОГИКА TUJEN (Auto-Buyer)
# ==========================================
def run_tujen():
    print(f"{Fore.CYAN}=== Tujen Bot v4 (Turbo Human) ==={Style.RESET_ALL}")
    print("Режим: Покупка валюты и проходок.")
    
    # Горячая клавиша для выхода
    keyboard.add_hotkey('F12', kill_bot)
    
    print(f"Нажми {Fore.GREEN}F9{Style.RESET_ALL} для старта.")
    keyboard.wait('F9')
    print(f"{Fore.GREEN}>>> Started!{Style.RESET_ALL}")

    next_afk_time = time.time() + random.randint(config.AFK_INTERVAL_MINUTES[0], config.AFK_INTERVAL_MINUTES[1]) * 60
    should_reroll = True

    try:
        while True:
            # --- 1. FATIGUE (Усталость) ---
            if time.time() > next_afk_time:
                afk_duration = random.randint(*config.AFK_DURATION_SECONDS)
                print(f"{Fore.MAGENTA}>>> Fatigue Break: {afk_duration}s...{Style.RESET_ALL}")
                time.sleep(afk_duration)
                next_afk_time = time.time() + random.randint(*config.AFK_INTERVAL_MINUTES) * 60
                should_reroll = True

            # --- 2. CAMPING LOOP (Реролл) ---
            if should_reroll:
                if not vision.is_reroll_active():
                    print(f"{Fore.RED}Reroll inactive. Out of coins? Stopping.{Style.RESET_ALL}")
                    break

                # Клик по Рероллу
                input_handler.click_reroll_with_drift()
                
                # Ждем анимацию
                time.sleep(config.TIME_REROLL_ANIMATION)
                
                # Редкий микро-тупняк (Humanization)
                if random.random() < config.CHANCE_TO_THINK:
                    time.sleep(abs(random.gauss(*config.TIME_THINKING)))

                should_reroll = False

            # --- 3. SCANNING (Поиск товаров) ---
            items_to_buy = vision.scan_inventory_batch()
            
            if items_to_buy:
                print(f"{Fore.GREEN}Batch buy: {len(items_to_buy)} items.{Style.RESET_ALL}")
                
                # --- 4. FAST BATCH BUY ---
                for item_coords in items_to_buy:
                    # Клик по предмету
                    input_handler.human_click(item_coords)
                    
                    # Ждем открытия окна
                    time.sleep(config.DELAY_POPUP_OPEN) 
                    
                    # Жмем Buy
                    input_handler.human_click(config.BUY_BTN_COORDS)
                    
                    # Ждем смены окна на Take
                    time.sleep(config.DELAY_POPUP_OPEN)
                    
                    # Жмем Take
                    input_handler.human_click(config.TAKE_ITEM_BTN_COORDS)
                    
                    # Короткая пауза
                    time.sleep(config.DELAY_AFTER_TAKE)
                
                # Возврат к рероллу
                should_reroll = True
                input_handler.smooth_move(config.REROLL_BTN_COORDS[0], config.REROLL_BTN_COORDS[1])
                
            else:
                should_reroll = True
                # Мышь не двигаем, сразу реролл в следующем цикле

    except KeyboardInterrupt:
        print("\nBot stopped.")

# ==========================================
# 2. ЛОГИКА RECOMBINATOR (Crafter)
# ==========================================
def run_recombinator():
    print(f"\n{Fore.MAGENTA}=== RECOMBINATOR BOT v1.0 ==={Style.RESET_ALL}")
    print("Режим: Автоматический крафт колец/амулетов.")
    print("Требования:")
    print("1. Открыт инвентарь (I).")
    print("2. Открыто окно рекомбинатора.")
    print("3. В инвентаре есть предметы, соответствующие config/mods_config.py.")
    
    # Горячая клавиша для выхода
    keyboard.add_hotkey('F12', kill_bot)

    print(f"\nНажми {Fore.GREEN}F10{Style.RESET_ALL} для старта цикла крафта.")
    keyboard.wait('F10')
    
    # Инициализация исполнителя
    executor = RecombinatorExecutor()
    print(f"{Fore.GREEN}>>> Recombinator Started!{Style.RESET_ALL}")
    
    try:
        while True:
            # Запуск одного полного цикла (Скан -> Пары -> Крафт)
            has_work = executor.execute_cycle()
            
            if not has_work:
                print(f"{Fore.YELLOW}[MAIN] Нет пар для крафта. Ожидание 5 сек...{Style.RESET_ALL}")
                time.sleep(5)
                # Можно добавить проверку нажатия клавиш для выхода из цикла ожидания
            else:
                # Небольшая пауза между циклами крафта
                time.sleep(1.0)
                
    except KeyboardInterrupt:
        print("\nBot stopped.")
    except Exception as e:
        print(f"\n{Fore.RED}Critical Error: {e}{Style.RESET_ALL}")

# ==========================================
# MAIN MENU
# ==========================================
def main():
    print(f"{Fore.CYAN}--- TjnBuyer & Recombinator Suite ---{Style.RESET_ALL}")
    print("Выберите режим работы:")
    print(f"{Fore.YELLOW}1.{Style.RESET_ALL} Tujen Auto-Buyer (Покупки)")
    print(f"{Fore.YELLOW}2.{Style.RESET_ALL} Recombinator Crafter (Крафт)")
    print(f"{Fore.YELLOW}3.{Style.RESET_ALL} Выход")
    
    choice = input("\nВведите номер (1-3): ").strip()
    
    if choice == '1':
        run_tujen()
    elif choice == '2':
        run_recombinator()
    elif choice == '3':
        print("Выход.")
        sys.exit()
    else:
        print("Неверный ввод. Попробуйте снова.")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nЗавершение работы.")