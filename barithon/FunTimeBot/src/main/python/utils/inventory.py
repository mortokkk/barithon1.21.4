# ========================================
# ★ РАБОТА С ИНВЕНТАРЁМ ★
# ========================================

import logging

def check_inventory_for_brush(bot):
    """Проверяет, есть ли кисточка в инвентаре"""
    inventory = bot.player.getInventory()
    for slot in range(0, 36):
        try:
            item = inventory.getItem(slot)
            if item is None:
                continue
            if "brush" in str(item.getItem().getRegistryName()):
                return True
        except:
            continue
    return False


def count_food_in_inventory(bot):
    """Считает еду в инвентаре"""
    count = 0
    inventory = bot.player.getInventory()
    for slot in range(0, 36):
        try:
            item = inventory.getItem(slot)
            if item is None:
                continue
            if is_food(bot, item):
                count += item.getCount()
        except:
            continue
    return count


def is_food(bot, item):
    """Проверяет, является ли предмет едой"""
    item_name = str(item.getItem().getRegistryName())
    food_items = ["apple", "bread", "steak", "porkchop", "chicken", "beef", "carrot", "potato", "golden_apple"]
    return any(f in item_name.lower() for f in food_items)


def get_item_in_slot(bot, slot):
    """Получает предмет из слота"""
    try:
        if slot < 9:
            return bot.player.getInventory().getStackInSlot(slot)
        else:
            return bot.player.getInventory().getItem(slot)
    except:
        return None