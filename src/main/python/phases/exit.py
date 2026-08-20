# ========================================
# ★ ФАЗА ВЫХОДА ★
# ========================================

import time
import logging
from config import *
from utils.movement import *
from utils.chat import *

def exit_phase(bot):
    """
    ФАЗА ВЫХОДА:
    1. /an324
    2. Ищем портал в Энд
    3. Заходим в портал
    4. Сброс → PREPARE
    """
    logging.info("[EXIT] Выход")
    
    # 1. /an324
    logging.info("[EXIT] /an324")
    bot.mc.player.sendChatMessage(COMMAND_AN324)
    time.sleep(1)
    
    # 2. Ищем портал
    portal = find_nearest_end_portal(bot)
    
    if portal:
        logging.info(f"[EXIT] Портал в {portal}")
        walk_to(bot, portal[0], portal[1], portal[2], timeout=10)
        
        # 3. Заходим в портал
        bot.mc.options.keyForward.setPressed(True)
        time.sleep(2)
        bot.mc.options.keyForward.setPressed(False)
        
        logging.info("[EXIT] Зашёл в портал!")
        bot.portal_found = True
        
        # 4. Сброс и начало заново
        time.sleep(3)
        bot.reset_everything()
        bot.phase = "PREPARE"
    else:
        logging.info("[EXIT] Портал не найден")
        time.sleep(2)