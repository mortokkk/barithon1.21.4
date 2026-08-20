# ========================================
# ★ ЛОМАНИЕ БЛОКОВ И БОЙ ★
# ========================================

import time
import logging
from net.minecraft.core.BlockPos import BlockPos

from .movement import walk_to


def break_block(bot, coords):
    """Ломает блок в 1.21.4"""
    try:
        block_pos = BlockPos(int(coords[0]), int(coords[1]), int(coords[2]))
        bot.mc.playerController.clickBlock(block_pos)
        time.sleep(0.3)
        return True
    except Exception as e:
        logging.error(f"[BREAK] Ошибка: {e}")
        return False


def use_item_on_block(bot, pos):
    """Использует предмет на блоке (кисточка на песке)"""
    try:
        block_pos = BlockPos(int(pos[0]), int(pos[1]), int(pos[2]))
        bot.mc.playerController.useItemOn(block_pos)
        time.sleep(0.3)
        return True
    except Exception as e:
        logging.error(f"[USE] Ошибка: {e}")
        return False


def collect_loot(bot):
    """Подбирает выпавший лут"""
    try:
        entities = bot.world.getEntities()
        for entity in entities:
            if entity is None:
                continue
            if "item" in str(entity.getType().getRegistryName()).lower():
                x, y, z = entity.getX(), entity.getY(), entity.getZ()
                walk_to(bot, x, y, z, timeout=3)
                time.sleep(0.2)
                logging.info(f"[COLLECT] Подобрал предмет в ({x}, {y}, {z})")
                return True
    except Exception as e:
        logging.error(f"[COLLECT] Ошибка: {e}")
    return False