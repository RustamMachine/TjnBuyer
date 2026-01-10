Тесты разбиты на два уровня: проверяем, что теги находятся правильно, и проверяем, что пары создаются логично.

```markdown
# Technical Analysis: Matchmaking Tests

## 1. Goal
Verify both the **text parsing accuracy** (Analyzer) and the **pairing logic** (Matchmaker) using `pytest`.

## 2. Fixtures (Mock Data)

### `inventory_fixture`
A list of `Item` objects representing a stash tab state:
1.  **Item_A (Amulet):** Text contains "to Spirit". (Expected Tag: `Spirit`)
2.  **Item_B (Amulet):** Text contains "Level of all Spell Skills". (Expected Tag: `GemSpell`)
3.  **Item_C (Amulet):** Text contains "Life Regeneration" (Junk mod). (Expected Tags: Empty)
4.  **Item_D (Ring):** Text contains "Cold damage to Attacks". (Expected Tag: `ColdAttack`)
5.  **Item_E (Ring):** Text contains "Fire damage to Attacks". (Expected Tag: `FireAttack`)

## 3. Test Cases

### Part A: Analyzer Tests (Unit Level)
*Focus: Does the system correctly identify mods based on `mods_config.py`?*

1.  **`test_analyze_amulet_spirit`**
    * Input: `Item_A`.
    * Assert: `Item_A.tags` == `{"Spirit"}`.
2.  **`test_analyze_junk_item`**
    * Input: `Item_C`.
    * Assert: `Item_C.tags` is Empty.
3.  **`test_analyze_complex_item`**
    * Input: An item with both "Spirit" and "GemMelee".
    * Assert: Tags contain both.

### Part B: Matchmaker Tests (Logic Level)
*Focus: Does the system create correct pairs from a list?*

4.  **`test_match_simple_pair`**
    * Input: List `[Item_A, Item_B]`.
    * Action: Run `create_pairs`.
    * Assert: Result has 1 pair: `(Item_A, Item_B)`.
    
5.  **`test_match_ignore_junk`**
    * Input: List `[Item_A, Item_C]`.
    * Action: Run `create_pairs`.
    * Assert: Result is Empty (Item C has no value, so A has no partner).

6.  **`test_match_distinct_classes`**
    * Input: List `[Item_A (Amulet), Item_D (Ring)]`.
    * Action: Run `create_pairs`.
    * Assert: Result is Empty (Cannot pair Amulet with Ring).

7.  **`test_match_rings`**
    * Input: List `[Item_D, Item_E]`.
    * Action: Run `create_pairs`.
    * Assert: Result has 1 pair `(Item_D, Item_E)`.

8.  **`test_match_logging`**
    * Toggle `config.MATCHMAKING_LOGGING_ENABLED = True`.
    * Run a successful match.
    * Assert: Logs contain "Pair created: Item_A + Item_B".

## 4. Execution Order
1.  Write these tests first. They will fail.
2.  Implement `mods_config.py`.
3.  Implement `analyzer.py` -> Tests Part A pass.
4.  Implement `matchmaker.py` -> Tests Part B pass.