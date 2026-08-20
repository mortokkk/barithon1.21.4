# ========================================
# ★ ФАЗА ПОДГОТОВКИ ★
# ========================================

import time
import logging
from config import *
from utils.chest import *
from utils.chat import *
from utils.esp import *

def prepare_phase(bot):
    """
    ФАЗА ПОДГОТОВКИ:
    1. /an323
    2. Ждём 3 секунды
    3. Ищем сундук с табличкой
    4. Берём: зелье невидимости, зелье скорости, еду (2 шт)
    5. Если не хватает → /hub → ждём 30 сек → повтор
    6. Если всё есть → /an324 → WAIT_FOR_PORTAL
    """
    logging.info("[PREPARE] Начинаю подготовку")
    
    while True:
        # Проверяем смерть
        if bot.check_if_dead():
            return
        
        # Проверяем команду .start end
        bot.check_for_start_command()
        if bot.waiting_for_start:
            return
        
        # 1. /an323 (один раз)
        if not bot.an323_used:
            logging.info("[PREPARE] /an323")
            bot.mc.player.sendChatMessage(COMMAND_AN323)
            bot.an323_used = True
            time.sleep(1)
        
        # 2. Ждём 3 секунды
        logging.info("[PREPARE] Жду 3 секунды...")
        time.sleep(3)
        
        # 3. Ищем сундук с табличкой
        logging.info("[PREPARE] Ищу сундук с табличкой")
        chest = find_nearest_chest_with_sign(bot)
        
        if chest is None:
            logging.info("[PREPARE] Сундук не найден, ищу дальше")
            time.sleep(2)
            continue
        
        bot.chest_with_sign = chest
        logging.info(f"[PREPARE] Нашёл сундук в {chest}")
        
        # 4. Пытаемся взять предметы
        success = take_items_from_chest(bot, chest)
        
        if success:
            logging.info("[PREPARE] ✅ Все предметы получены!")
            bot.client_chat_log("✅ Все предметы получены! Ищу портал...")
            
            # 6. Переход к поиску портала
            bot.phase = "WAIT_FOR_PORTAL"
            bot.portal_search_start = time.time()
            
            # /an324
            logging.info("[PREPARE] /an324")
            bot.mc.player.sendChatMessage(COMMAND_AN324)
            time.sleep(1)
            return
        
        # 5. НЕ УДАЛОСЬ - возврат на /hub
        logging.warning("[PREPARE] ❌ Не хватает предметов!")
        bot.client_chat_log("❌ Не хватает предметов! Возвращаюсь на /hub...")
        
        # Сбрасываем флаг
        bot.an323_used = False
        
        # /hub
        logging.info("[PREPARE] /hub")
        bot.mc.player.sendChatMessage(COMMAND_HUB)
        time.sleep(2)
        
        # Ждём 30 секунд
        for i in range(HUB_WAIT_TIME, 0, -1):
            logging.info(f"[PREPARE] Ожидание: {i}с...")
            if bot.check_if_dead():
                return
            time.sleep(1)