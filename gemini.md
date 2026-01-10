Техническая Спецификация TjnBuyer v5

1. Структура Проекта (File Tree)

TjnBuyer/

├── config/

│   ├── config.py           # Координаты, тайминги (генерируется калибровкой)

│   └── mods_config.py      # Правила парсинга (словарь Т1 модов)

├── core/

│   ├── inventory_manager.py # Состояние инвентаря (State)

│   ├── input_handler.py     # Низкоуровневый ввод (Mouse/Keyboard)

│   └── utils.py             # Вспомогательные функции (Math, Logging)

├── perception/

│   ├── item_scanner.py      # Парсинг Ctrl+Alt+C (Regex)

│   ├── ocr_engine.py        # Tesseract OCR (Поиск текста на экране)

│   └── shopping_vision.py   # Анализ пикселей (для Туджина)

├── logic/

│   └── matchmaker.py        # Алгоритм подбора пар (Business Logic)

├── executors/

│   ├── shopping_executor.py    # Сценарий скупки у Туджина

│   └── recombinator_executor.py # Сценарий крафта

├── ui/

│   └── main_ui.py           # GUI (CustomTkinter)

├── tests/                   # TDD MODULE

│   ├── fixtures/

│   │   ├── clipboard_dumps/ # .txt файлы с примерами предметов

│   │   └── screenshots/     # .png скрины рекомбинатора

│   ├── test_ocr.py

│   ├── test_parser.py

│   └── test_matchmaker.py

└── main.py                  # Точка входа (Launcher)



Подробная Архитектура Модулей

Модуль 1: Данные и Состояние (core/inventory_manager.py)

Ответственность: Single Source of Truth. Хранит виртуальное представление инвентаря 12x5.

Класс InventoryItem:



slot_index: int (0-59)

item_class: str ("Rings", "Amulets")

tags: List[str] (Пример: ["Life", "FireRes"])

status: Enum (EMPTY, TRASH, CRAFT_BASE, FINISHED, LOCKED)

TRASH: Нет Т1 модов.

CRAFT_BASE: 1 Т1 мод (или подходящая комбинация).

FINISHED: 2+ Т1 мода (Годлайк, не трогать).

LOCKED: Сейчас используется экзекьютором.

Класс InventoryManager:



__init__(): Генерирует 60 координат на основе config.TOP_LEFT и config.BOTTOM_RIGHT.

update_slot(index, item_obj): Обновляет данные.

get_candidate_items() -> List[InventoryItem]: Возвращает предметы со статусом CRAFT_BASE.

get_next_empty_slot() -> int: Для выгрузки результата крафта (если понадобится).



А. Глаза Инвентаря (perception/item_scanner.py)

Ответственность: Преобразование буфера обмена в объект InventoryItem.



scan_slot(slot_index):

input_handler.move_to_slot(index)

input_handler.copy_advanced() (Ctrl+Alt+C)

_parse_text(raw_text) -> InventoryItem

_parse_text(text):

Использует mods_config.WANTED_MODS_BY_CLASS.

Regex Логика: Ищет строку (Tier: 1), затем проверяет следующую строку на вхождение подстрок из конфига.

PoE 2 Spec: Корректно обрабатывает множественное число (Item Class: Rings).

Б. Глаза Рекомбинатора (perception/ocr_engine.py)

Ответственность: Найти координаты текста на картинке. Критичен для TDD.



find_text_center(image: np.array, target_text: str, roi: region=None) -> (x, y):

cv2.cvtColor -> Grayscale.

cv2.threshold -> Бинаризация (черный текст на белом фоне или наоборот).

pytesseract.image_to_data.

Перебор найденных слов. Fuzzy search (нечеткое сравнение), если OCR ошибся в 1 букве (напр. "Life" vs "Lif").

Возврат абсолютных координат центра слова.

Модуль 3: Логика (logic/matchmaker.py)

Ответственность: Принятие решений. Чистая функция, никаких сайд-эффектов.



create_crafting_queue(inventory: InventoryManager) -> List[Tuple[Item, Item]]:

Берет все предметы CRAFT_BASE.

Группировка: Разделяет на кольца и амулеты.

Матчинг:

Перебор: Item A vs Item B.

Правило: len(set(A.tags) + set(B.tags)) >= 2. (Если скрестим, можем получить 2 разных Т1).

Конфликты: Если Item A подходит и к B, и к C, выбираем лучшую пару (или первую попавшуюся).

Помечает выбранные предметы как LOCKED в менеджере (чтобы не использовать дважды).

Возвращает список пар.

Модуль 4: Исполнители (Executors)

executors/recombinator_executor.py

Ответственность: Оркестрация процесса крафта одной партии.



run_cycle():

scanner.scan_all() -> Обновить инвентарь.

plan = matchmaker.create_crafting_queue().

Если план пуст -> Stop или Switch State.

for pair in plan: _execute_combine(pair).

_execute_combine(item_a, item_b):

Input: Перетащить (Ctrl+Click) item_a и item_b в рекомбинатор.

Select Mods:

Сделать скриншот области модов рекомбинатора (mss).

Для каждого тега из item_a.tags и item_b.tags:

Получить текст мода из конфига (напр. "Fire Damage").

coords = ocr_engine.find_text_center(screenshot, text).

Если coords: Кликнуть.

Combine: Клик по кнопке Combine.

Result: Ждать анимацию. Проверить слот результата (пиксель-чек или Ctrl+C).

Успех -> Забрать.

Провал -> Очистить слоты в InventoryManager.

3. Архитектура Тестирования (TDD Deep Dive)

Это то, чем ты займешься в деревне. Тесты должны запускаться командой python -m unittest discover tests.



1. Тесты OCR (tests/test_ocr.py)

Самый сложный блок. Требует "золотых эталонов" (fixtures).



Fixture: Папка tests/fixtures/screenshots/. В ней лежат папки amulets / rings, со скриншотами

Test Case 1: распознавание текста с предмета А, и предмета Б

Загружает recomb_ring_life_fire.png.

Вызывает ocr.find_text_center(img, "Fire Damage").

Assert: Результат не None. Координаты (x, y) находятся в пределах ожидаемой области (ты заранее посмотришь в Paint, где там надпись, и задашь expected_region = (400, 300, 500, 350)).

Test Case 2: test_find_partial_match

Текст на скрине: "Adds 15 to 25 Fire Damage".

Ищем: "Fire Damage".

Assert: Должен найти.

2. Тесты Парсера (tests/test_parser.py)

в test_parser.md

3. Тесты Матчмейкера (tests/test_matchmaker.py)

Тут не нужны файлы, используем Mocks (фиктивные объекты).



Setup: Создать список InventoryItem вручную.

Slot 1: Ring, Tags=['Life']

Slot 2: Ring, Tags=['Mana'] (Мусор, не нужен нам)

Slot 3: Ring, Tags=['Chaos']

Slot 4: Ring, Tags=['Life', 'Chaos'] (Уже готовый, FINISHED)

Test Case:

Вызвать matchmaker.create_queue.

Assert:

Пара (Slot 1, Slot 3) — создана.

Slot 2 — игнорируется.

Slot 4 — игнорируется (защита готовых вещей).

4. UI/UX Спецификация (ui/main_ui.py)

Интерфейс должен быть неблокирующим.



Библиотека: customtkinter.

Layout:

Sidebar: Кнопки "Tujen Mode", "Recombinator Mode", "Calibration".

Main Area:

Log Console: CTkTextbox. Перенаправить sys.stdout сюда, чтобы принты шли в окно.

Status Bar: "Current Action: Scanning Slot 5...", "State: Running/Stopped".

Controls: Кнопка "EMERGENCY STOP (F10)" (дублирует физическую клавишу).

Multithreading:

При нажатии "Start Tujen":

Создается threading.Thread(target=shopping_executor.run).

Поток помечается как daemon=True.

Кнопка меняется на "Stop".

При нажатии "Stop": Устанавливается глобальный флаг stop_event.set(), который проверяют все циклы внутри экзекьюторов.

