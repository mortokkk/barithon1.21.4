# ========================================
# ★ ФАЗЫ ОЖИДАНИЯ ★
# ========================================

import time
import logging
import random
from config import *
from utils.chest import *
from utils.movement import *
from utils.esp import *

def wait_for_cooldown_phase(bot):
    """
    ФАЗА ОЖИДАНИЯ КД:
    1. Проверка зелий
    2. Прячемся у сундука или бегаем
    3. После КД → DEPOSIT
    """
    logging.info("[WAIT] Ожидаю КД")
    
    # Проверяем зелья
    if not bot.has_invis_potion or not bot.has_speed_potion:
        logging.warning("[WAIT] Закончились зелья! Иду за новыми")
        bot.phase = "PREPARE"
        return
    
    while time.time() < bot.cooldown_end:
        bot.update_state()
        
        if bot.check_if_dead():
            return
        
        # Проверяем зелья во время ожидания
        if not bot.has_invis_potion or not bot.has_speed_potion:
            logging.warning("[WAIT] Закончились зелья во время ожидания!")
            bot.phase = "PREPARE"
            return
        
        remaining = bot.cooldown_end - time.time()
        logging.info(f"[WAIT] Осталось {remaining:.1f}с")
        
        # Прячемся или бегаем
        chest = find_nearest_chest_without_sign(bot)
        if chest:
            hide_near_chest(bot, chest)
        else:
            random_walk_small(bot)
        
        bot.save_state()
        time.sleep(2)
    
    logging.info("[WAIT] КД прошёл, перехожу к DEPOSIT")
    bot.phase = "DEPOSIT"


def hide_near_chest(bot, chest):
    """Прячемся рядом с сундуком"""
    if chest:
        walk_to(bot, chest[0], chest[1], chest[2], timeout=5)
        bot.mc.options.keyShift.setPressed(True)
        time.sleep(1)
        bot.mc.options.keyShift.setPressed(False)
    else:
        logging.info("[WAIT] Нет сундука, стою на месте")
        time.sleep(1)


def random_walk_small(bot):
    """Маленькие рандомные перемещения"""
    for _ in range(3):
        x = bot.player.getX() + random.randint(-5, 5)
        z = bot.player.getZ() + random.randint(-5, 5)
        walk_to(bot, x, bot.player.getY(), z, timeout=3)
        time.sleep(random.uniform(0.5, 1.5))


def wait_for_portal_phase(bot):
    """
    ФАЗА ОЖИДАНИЯ ПОРТАЛА:
    1. Поиск портала в радиусе 10 блоков (по всем Y)
    2. Если найден → вход → FARM
    3. Если не найден → /spawn → ожидание .start end
    """
    logging.info("[PORTAL] Поиск портала в Энд")
    
    # Таймаут
    if time.time() - bot.portal_search_start > PORTAL_SEARCH_TIMEOUT:
        logging.warning(f"[PORTAL] Таймаут поиска портала ({PORTAL_SEARCH_TIMEOUT}с)! Перезапуск")
        bot.reset_everything()
        bot.phase = "PREPARE"
        return
    
    # Ищем портал
    portal = find_nearest_end_portal(bot)
    
    if portal:
        logging.info(f"[PORTAL] ✅ Нашёл портал в {portal}")
        bot.portal_coords = portal
        bot.portal_found = True
        
        # Заходим в портал
        walk_to(bot, portal[0], portal[1], portal[2], timeout=10)
        
        bot.mc.options.keyForward.setPressed(True)
        time.sleep(2)
        bot.mc.options.keyForward.setPressed(False)
        
        logging.info("[PORTAL] Зашёл в портал! Перехожу к фарму")
        bot.client_chat_log("✅ Зашёл в портал! Начинаю фарм")
        
        bot.phase = "FARM"
        bot.prepare_complete = True
        bot.vases_broken_since_deposit = 0
        bot.last_progress = time.time()
        bot.save_state()
        return
    
    # Портала нет
    logging.warning("[PORTAL] ❌ Портала нет в радиусе 10 блоков!")
    
    # /spawn
    logging.info("[PORTAL] /spawn")
    bot.mc.player.sendChatMessage(COMMAND_SPAWN)
    time.sleep(2)
    
    bot.an323_used = False
    
    # Останавливаемся
    logging.info("[PORTAL] Останавливаюсь")
    bot.baritone.getPathingBehavior().cancelEverything()
    
    # Логируем в клиентский чат
    bot.client_chat_log("❌ Портала нет в радиусе 10 блоков. Ожидаю команду .start end")
    logging.info("[PORTAL] Ожидаю команду .start end")
    
    # Включаем режим ожидания
    bot.waiting_for_start = True
    bot.baritone.getSettings().safeWalk.value = False
    bot.save_state()


def find_nearest_end_portal(bot):
    """Находит ближайший портал в Энд (по всем Y)"""
    px, py, pz = int(bot.player.getX()), int(bot.player.getY()), int(bot.player.getZ())
    
    for y in range(py - 10, py + 11):
        for x in range(px - PORTAL_SEARCH_RADIUS, px + PORTAL_SEARCH_RADIUS + 1):
            for z in range(pz - PORTAL_SEARCH_RADIUS, pz + PORTAL_SEARCH_RADIUS + 1):
                try:
                    block = bot.world.getBlockState(BlockPos(x, y, z))
                    block_name = str(block.getBlock().getRegistryName())
                    if "end_portal" in block_name.lower():
                        logging.info(f"[PORTAL] Нашёл портал в ({x}, {y}, {z})")
                        return (x, y, z)
                except:
                    continue
    
    logging.info("[PORTAL] Порталов не найдено")
    return None