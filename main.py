import time
import sys
import os
import random
import keyboard
import config
import vision
import input_handler
from colorama import init, Fore, Style

init(autoreset=True)

def kill_bot():
    print(f"\n{Fore.RED}!!! EMERGENCY STOP (F10) !!!{Style.RESET_ALL}")
    os._exit(0)

def main():
    print(f"{Fore.CYAN}=== Tujen Bot v4 (Turbo Human) ==={Style.RESET_ALL}")
    keyboard.add_hotkey('F10', kill_bot)
    
    print(f"Нажми {Fore.GREEN}F9{Style.RESET_ALL} для старта.")
    keyboard.wait('F9')
    print(f"{Fore.GREEN}>>> Started!{Style.RESET_ALL}")

    next_afk_time = time.time() + random.randint(config.AFK_INTERVAL_MINUTES[0], config.AFK_INTERVAL_MINUTES[1]) * 60
    should_reroll = True

    while True:
        # --- 1. FATIGUE ---
        if time.time() > next_afk_time:
            afk_duration = random.randint(*config.AFK_DURATION_SECONDS)
            print(f"{Fore.MAGENTA}>>> Fatigue Break: {afk_duration}s...{Style.RESET_ALL}")
            time.sleep(afk_duration)
            next_afk_time = time.time() + random.randint(*config.AFK_INTERVAL_MINUTES) * 60
            should_reroll = True

        # --- 2. CAMPING LOOP ---
        if should_reroll:
            if not vision.is_reroll_active():
                print(f"{Fore.RED}Reroll inactive. Out of coins? Stopping.{Style.RESET_ALL}")
                break

            # Клик по Рероллу
            input_handler.click_reroll_with_drift()
            
            # Ждем анимацию (теперь быстро)
            time.sleep(config.TIME_REROLL_ANIMATION)
            
            # Редкий микро-тупняк
            if random.random() < config.CHANCE_TO_THINK:
                time.sleep(abs(random.gauss(*config.TIME_THINKING)))

            should_reroll = False

        # --- 3. SCANNING ---
        items_to_buy = vision.scan_inventory_batch()
        
        if items_to_buy:
            print(f"{Fore.GREEN}Batch buy: {len(items_to_buy)} items.{Style.RESET_ALL}")
            
            # --- 4. FAST BATCH BUY ---
            for item_coords in items_to_buy:
                # Клик по предмету
                input_handler.human_click(item_coords)
                
                # Ждем открытия окна (минимально)
                time.sleep(config.DELAY_POPUP_OPEN) 
                
                # Жмем Buy
                input_handler.human_click(config.BUY_BTN_COORDS)
                
                # Ждем смены окна на Take (минимально)
                time.sleep(config.DELAY_POPUP_OPEN)
                
                # Жмем Take
                input_handler.human_click(config.TAKE_ITEM_BTN_COORDS)
                
                # Короткая пауза, чтобы предмет исчез
                time.sleep(config.DELAY_AFTER_TAKE)
            
            # Возврат к рероллу
            should_reroll = True
            input_handler.smooth_move(config.REROLL_BTN_COORDS[0], config.REROLL_BTN_COORDS[1])
            
        else:
            should_reroll = True
            # Мышь не двигаем, сразу реролл в следующем цикле

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped.")