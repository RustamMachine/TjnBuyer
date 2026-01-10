# Technical Analysis: Matchmaking System

## 1. Goal
Implement a Matchmaking Service that processes a collection of items, identifies valuable modifiers based on configuration, and groups compatible items into pairs for recombination.

## 2. Core Components

### A. Config & Constants (`config/mods_config.py`)
* **Source of Truth:** Contains the dictionary `WANTED_MODS_BY_CLASS`.
* **Role:** Defines mapping between "Raw Text Substrings" and "Internal Tags" (e.g., `"to Spirit"` -> `"Spirit"`).

### B. Item Analyzer (`logic/analyzer.py`)
* **Responsibility:** Atomic function to parse a single item's text and assign tags.
* **Input:** `Item` object (or raw text + class).
* **Output:** Set of tags (e.g., `{"Spirit", "GemSpell"}`).
* **Logic:**
    1.  Check item class.
    2.  Iterate through `WANTED_MODS_BY_CLASS`.
    3.  If substring matches -> add Tag.

### C. Matchmaker Logic (`logic/matchmaker.py`)
* **Responsibility:** Takes a list of items and produces pairs.
* **Input:** `List[Item]` (Inventory).
* **Output:** `List[Tuple[Item, Item]]` (Pairs).
* **Algorithm:**
    1.  **Filter:** Select items that are:
        * Available (Status != 'busy').
        * Identified (have text).
        * Have at least 1 "Wanted Tag" (via `Item Analyzer`).
    2.  **Grouping:** Group items by `Item Class` (cannot recombinate Ring with Amulet).
    3.  **Pairing Strategy (Simple MVP):**
        * *Goal:* Combine items to stack mods.
        * *Logic:* Find two items within the same class that have **different** valuable tags.
        * *Example:* Item A (`Spirit`) + Item B (`GemSpell`) -> Pair.
        * *Constraint:* Do not pair an item with itself. Each item can be in only one pair per cycle.
    4.  **Logging:** Log created pairs if `config.MATCHMAKING_LOGGING_ENABLED` is True.

## 3. Data Structures

### Input Object (Mock or Real)
```python
class Item:
    id: str
    text: str
    item_class: str # "Rings", "Amulets"
    tags: Set[str] = set()
    status: str = "available" # or "processing", "matched"
```


### Output object
```pyhon
MatchResult = List[Tuple[Item, Item]]
```
## 4. Implementation Steps
Step 1: Implement mods_config.py (Static mappings).

Step 2: Implement analyze_item(item) function to populate item.tags.

Step 3: Implement create_pairs(inventory) function:

Iterate inventory -> Run analyze_item.

Filter "valuable" items (tags > 0).

Run matching loop.