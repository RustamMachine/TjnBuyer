
TEST_CASES = [
    # CASE 1: Идеальное кольцо (из описания)
    {
        "id": "ring_godlike_1",
        "description": "Кольцо с Т1 Жизнью и Т1 Холодом",
        "raw_text": """Item Class: Rings
Rarity: Rare
Bramble Loop
Gold Ring
--------
Item Level: 78
--------
{ Prefix Modifier "Hoarder's" (Tier: 1) }
16(16-19)% increased Rarity of Items found
{ Prefix Modifier "Entombing" (Tier: 1) — Damage, Elemental, Cold, Attack }
Adds 22(21-24) to 34(32-37) Cold damage to Attacks
{ Suffix Modifier "of the Lion" (Tier: 1) }
+89 to maximum Life
""",
        "expected_class": "Rings",
        "expected_tags": ["ColdAttack", "Life"],
        "should_be_none": False
    },

    # CASE 2: Мусор (нет Т1 модов)
    {
        "id": "trash_item_1",
        "description": "Кольцо без Т1 модов",
        "raw_text": """Item Class: Rings
Rarity: Rare
Trash Loop
--------
{ Prefix Modifier "Weak" (Tier: 5) }
+10 to maximum Life
""",
        "expected_class": None,
        "expected_tags": [],
        "should_be_none": True
    },
    
    # CASE 3: Амулет (PoE 2)
    {
        "id": "amulet_spirit",
        "description": "Амулет на Спирит",
        "raw_text": """Item Class: Amulets
Rarity: Rare
Spirit Talisman
--------
{ Suffix Modifier "of the Ghost" (Tier: 1) }
+15 to Spirit
""",
        "expected_class": "Amulets",
        "expected_tags": ["Spirit"],
        "should_be_none": False
    },

    # TC-1: T1 Lightning
    {
        "id": "tc_1_lightning",
        "description": "T1 Lightning Attack",
        "raw_text": """Item Class: Rings
Rarity: Magic
Electrocuting Sapphire Ring of the Seal
--------
Requires: Level 60
--------
Item Level: 79
--------
{ Implicit Modifier — Elemental, Cold, Resistance }
+28(20-30)% to Cold Resistance
--------
{ Prefix Modifier "Electrocuting" (Tier: 1) — Damage, Elemental, Lightning, Attack }
Adds 2(1-4) to 69(60-71) Lightning damage to Attacks

{ Suffix Modifier "of the Seal" (Tier: 8) — Elemental, Cold, Resistance }
+6(6-10)% to Cold Resistance
""",
        "expected_class": "Rings",
        "expected_tags": ["LightningAttack"],
        "should_be_none": False
    },

    # TC-2: T1 Cold (Single T1)
    {
        "id": "tc_2_cold",
        "description": "T1 Cold Attack with other garbage",
        "raw_text": """Item Class: Rings
Rarity: Rare
Honour Loop
Pearl Ring
--------
Requires: Level 60
--------
Item Level: 80
--------
{ Implicit Modifier — Caster, Speed }
10(7-10)% increased Cast Speed
--------
{ Prefix Modifier "Entombing" (Tier: 1) — Damage, Elemental, Cold, Attack }
Adds 24(21-24) to 35(32-37) Cold damage to Attacks

{ Suffix Modifier "of Eviction" (Tier: 4) — Chaos, Resistance }
+12(12-15)% to Chaos Resistance

{ Suffix Modifier "of the Crystal" (Tier: 5) — Elemental, Fire, Cold, Lightning, Resistance }
+4(3-5)% to all Elemental Resistances

{ Suffix Modifier "of the Lion" (Tier: 5) — Attribute }
+19(17-20) to Strength
""",
        "expected_class": "Rings",
        "expected_tags": ["ColdAttack"],
        "should_be_none": False
    },

    # TC-3: T1 Lightning T1 Fire (Multiple T1s)
    {
        "id": "tc_3_multi_t1",
        "description": "T1 Lightning, T1 Fire, T1 Hybrid Res, T1 Mana Regen",
        "raw_text": """Item Class: Rings
Rarity: Rare
Gloom Grasp
Sapphire Ring
--------
Quality (Attack Modifiers): +20% (augmented)
--------
Requires: Level 60
--------
Item Level: 78
--------
{ Implicit Modifier — Elemental, Cold, Resistance }
+25(20-30)% to Cold Resistance
--------
{ Prefix Modifier "Electrocuting" (Tier: 1) — Damage, Elemental, Lightning, Attack  — 20% Increased }
Adds 2(1-4) to 70(60-71) Lightning damage to Attacks

{ Prefix Modifier "Cremating" (Tier: 1) — Damage, Elemental, Fire, Attack  — 20% Increased }
Adds 28(25-29) to 44(37-45) Fire damage to Attacks

{ Prefix Modifier "Glaciated" (Tier: 3) — Damage, Elemental, Cold, Attack  — 20% Increased }
Adds 15(14-15) to 22(22-24) Cold damage to Attacks

{ Suffix Modifier "of Amanamu" (Tier: 1) — Elemental, Fire, Chaos, Resistance }
+15(13-17)% to Fire and Chaos Resistances

{ Suffix Modifier "of the Lightning" (Tier: 2) — Elemental, Lightning, Resistance }
+37(36-40)% to Lightning Resistance

{ Suffix Modifier "of the Hearth" (Tier: 1) — Mana }
20(18-22)% increased Mana Regeneration Rate
15% increased Light Radius
""",
        "expected_class": "Rings",
        "expected_tags": ["LightningAttack", "FireAttack", "FireChaosRes", "ManaRegen"],
        "should_be_none": False
    }
]
