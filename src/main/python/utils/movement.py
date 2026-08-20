# ========================================
# ★ ДВИЖЕНИЕ И НАВИГАЦИЯ ★
# ========================================

import time
import math
import logging
from baritone.api.pathing.goals import GoalBlock


def walk_to(bot, x, y, z, timeout=10):
    """Идёт к координатам с таймаутом"""
    goal = GoalBlock(int(x), int(y), int(z))
    bot.baritone.getPathingBehavior().setGoal(goal)
    bot.baritone.getPathingBehavior().path()
    
    start = time.time()
    while time.time() - start < timeout:
        if bot.baritone.getPathingBehavior().isComplete():
            return True
        time.sleep(0.1)
    
    logging.warning(f"[WALK] Таймаут пути к {x}, {y}, {z}")
    bot.baritone.getPathingBehavior().cancelEverything()
    return False


def distance_to(bot, pos):
    """Расстояние до позиции"""
    return math.sqrt(
        (bot.player.getX() - pos[0])**2 +
        (bot.player.getY() - pos[1])**2 +
        (bot.player.getZ() - pos[2])**2
    )