"""
Конфигурация модов для парсинга и поиска (OCR).
"""

# 1. СЛОВАРЬ ЦЕННЫХ МОДОВ
# Структура: "ItemClass": { "GroupName": { "Substring": "InternalTag" } }
WANTED_MODS_BY_CLASS = {
    "Rings": {
        "ElementalDamage": {
            "Cold damage to Attacks": "ColdAttack",
            "Lightning damage to Attacks": "LightningAttack",
            "Fire damage to Attacks": "FireAttack",
        },
        "Resistances": {
            "Chaos Resistance": "ChaosRes"
        }
    },
    "Amulets": {
        "Resources": {
            # ИЗМЕНЕНИЕ: Заменили "to Spirit" на конкретные значения T1 (45-65),
            # чтобы OCR не путал их с implicit (+11-20).
            "45 to Spirit": "Spirit",
            "46 to Spirit": "Spirit",
            "47 to Spirit": "Spirit",
            "48 to Spirit": "Spirit",
            "49 to Spirit": "Spirit",
            "50 to Spirit": "Spirit",
            "(47-50) to Spirit": "Spirit"
        },
        "GemLevels": {
            "Level of all Minion Skills": "GemMinion",
            "Level of all Spell Skills": "GemSpell",
            "Level of all Melee Skills": "GemMelee",
            "Level of all Projectile Skills": "GemProjectile"
        }
    }
}

# 2. ГРУППЫ КОНФЛИКТОВ
# Если два тега принадлежат одной группе из этого списка,
# предметы с этими тегами НЕЛЬЗЯ скрещивать.
# Пример: Нельзя скрестить +1 Spell и +1 Melee (оба из GemLevels).
MUTUALLY_EXCLUSIVE_GROUPS = {
    "Amulets": ["GemLevels"]
}

# Вспомогательный маппинг: Tag -> GroupName
# Генерируется автоматически для быстрого поиска в Matchmaker
TAG_TO_GROUP_MAP = {}
for cls, groups in WANTED_MODS_BY_CLASS.items():
    TAG_TO_GROUP_MAP[cls] = {}
    for group_name, mappings in groups.items():
        for _, tag in mappings.items():
            TAG_TO_GROUP_MAP[cls][tag] = group_name