# mods_config.py

# Словарь соответствия текстов модов и внутренних тегов
# Структура:
# "ItemClass": {
#     "Human Readable Group Name (Optional/Comment)": {
#         "Exact Substring in PoE2 Item Text": "InternalTag"
#     }
# }

WANTED_MODS_BY_CLASS = {
    "Rings": {
        "ElementalDamage": {
            "Cold damage to Attacks": "ColdAttack",
            "Lightning damage to Attacks": "LightningAttack",
            "Fire damage to Attacks": "FireAttack",
        },
        "Attributes": {
             # Можно добавить позже
        }
    },
    "Amulets": {
        "Resources": {
            # В PoE2 это обычно "+X to Spirit"
            "to Spirit": "Spirit" 
        },
        "GemLevels": {
            # Важные +N к уровню камней
            "Level of all Minion Skills": "GemMinion",
            "Level of all Spell Skills": "GemSpell",
            "Level of all Melee Skills": "GemMelee",
            "Level of all Projectile Skills": "GemProjectile"
        }
    }
}