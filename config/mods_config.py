# Словарь соответствия текстов модов и внутренних тегов
# Формат: "Подстрока в PoE2": "Внутренний тег"

WANTED_MODS_BY_CLASS = {
    "Rings": {
        "Adds": { # Для урона обычно ищем стихию + Attack
            "Cold damage to Attacks": "ColdAttack",
            "Lightning damage to Attacks": "LightningAttack",
            "Fire damage to Attacks": "FireAttack",
        },
        "maximum Life": "Life",
        "maximum Spirit": "Spirit",
        "to Fire and Chaos Resistances": "FireChaosRes",
        "increased Mana Regeneration Rate": "ManaRegen",
    },
    "Amulets": {
        "maximum Spirit": "Spirit",
        "to Spirit": "Spirit",
        "maximum Life": "Life",
        # Добавь другие моды по мере необходимости
    }
}
