# ========================================
# ★ ФАЗА СДАЧИ РЕСУРСОВ ★
# ========================================

import time
import logging
from config import *
from utils.chest import *
from utils.chat import *
from utils.esp import *
from utils.inventory import *

def deposit_phase(bot):
    """
    ФАЗА СДАЧИ РЕСУРСОВ (после 5 ваз):
    1. /an323
    2. Ищем сундук БЕЗ таблички
    3. Скидываем всё, кроме зелий и 2 еды
    4. Переход к EXIT
    """
    bot.check_for_start_command()
    if bot.waiting_for_start:
        logging.info("[DEPOSIT] Остановлен командой .start end")
        return
    
    logging.info("[DEPOSIT] Сдача ресурсов (после 5 ваз)")
    
    # 1. /an323
    logging.info("[DEPOSIT] /an323")
    bot.mc.player.sendChatMessage(COMMAND_AN323)
    time.sleep(1)
    
    # 2. Ищем сундук БЕЗ таблички
    chest = find_nearest_chest_without_sign(bot)
    
    if chest:
        bot.chest_without_sign = chest
        success = deposit_items_keep_essentials(bot, chest)
        
        if success:
            bot.total_farms += 1
            logging.info("[DEPOSIT] Ресурсы сданы, перехожу к EXIT")
            bot.phase = "EXIT"
        else:
            logging.warning("[DEPOSIT] Сундук полон, ищу другой")
            time.sleep(2)
    else:
        logging.info("[DEPOSIT] Сундук не найден")
        time.sleep(2)


def deposit_and_check_phase(bot):
    """
    ФАЗА СДАЧИ + ПРОВЕРКИ (когда кисточка сломалась):
    1. /an323
    2. Скидываем всё, кроме зелий и 2 еды
    3. Проверяем инвентарь
    4. Если не хватает → PREPARE
    5. Если всё есть → FARM
    """
    logging.info("[DEPOSIT_AND_CHECK] Начинаю сдачу ресурсов и проверку инвентаря")
    
    # 1. /an323
    logging.info("[DEPOSIT_AND_CHECK] /an323")
    bot.mc.player.sendChatMessage(COMMAND_AN323)
    time.sleep(1)
    
    # 2. Ищем сундук БЕЗ таблички
    logging.info("[DEPOSIT_AND_CHECK] Ищу сундук без таблички")
    chest = find_nearest_chest_without_sign(bot)
    
    if chest is None:
        logging.warning("[DEPOSIT_AND_CHECK] Сундук без таблички не найден, ищу дальше")
        time.sleep(2)
        return
    
    logging.info(f"[DEPOSIT_AND_CHECK] Нашёл сундук в {chest}")
    
    # 3. Скидываем всё, кроме зелий и еды
    deposit_items_keep_essentials(bot, chest)
    
    # 4. Закрываем сундук
    close_container(bot)
    
    # 5. ★★★ ПРОВЕРЯЕМ ИНВЕНТАРЬ ★★★
    bot.update_state()
    missing_items = check_missing_items(bot)
    
    if missing_items:
        logging.warning(f"[DEPOSIT_AND_CHECK] ❌ Не хватает: {', '.join(missing_items)}")
        logging.info("[DEPOSIT_AND_CHECK] Перехожу в PREPARE")
        bot.phase = "PREPARE"
    else:
        logging.info("[DEPOSIT_AND_CHECK] ✅ Все предметы есть! Продолжаю фарм")
        bot.phase = "FARM"
        bot.vases_broken_since_deposit = 0
        bot.last_progress = time.time()


def deposit_items_keep_essentials(bot, chest_pos):
    """
    Скидывает ВСЁ в сундук, КРОМЕ:
    - Зелье невидимости
    - Зелье скорости
    - Еда (оставляет 2 шт)
    """
    try:
        if not open_chest_safe(bot, chest_pos):
            logging.error("[DEPOSIT] Не удалось открыть сундук!")
            return False
        
        if not is_container_open(bot):
            logging.error("[DEPOSIT] Сундук не открыт!")
            close_container(bot)
            return False
        
        empty_slots = count_empty_slots_in_chest(bot)
        if empty_slots == 0:
            logging.warning("[⚠] Сундук полон!")
            close_container(bot)
            bot.chest_without_sign = None
            return False
        
        logging.info(f"[DEPOSIT] В сундуке {empty_slots} свободных слотов")
        
        inventory = bot.player.getInventory()
        food_to_keep = FOOD_NEEDED
        
        for slot in range(0, 36):
            try:
                item = inventory.getItem(slot)
                if item is None:
                    continue
                
                item_name = str(item.getItem().getRegistryName())
                should_keep = False
                current_count = item.getCount()
                
                # Зелья - оставляем
                if "invisibility" in item_name.lower():
                    should_keep = True
                    logging.debug("[DEPOSIT] Оставляю зелье невидимости")
                
                elif "swiftness" in item_name.lower() or "speed" in item_name.lower():
                    should_keep = True
                    logging.debug("[DEPOSIT] Оставляю зелье скорости")
                
                # Еда - оставляем только 2 шт
                elif bot.is_food(item):
                    if bot.food_count <= food_to_keep:
                        should_keep = True
                        logging.debug(f"[DEPOSIT] Оставляю еду ({bot.food_count}/{food_to_keep})")
                    else:
                        extra = bot.food_count - food_to_keep
                        to_drop = min(extra, current_count)
                        if to_drop > 0:
                            click_slot(bot, slot)
                            bot.food_count -= to_drop
                            logging.info(f"[DEPOSIT] Скинул лишнюю еду ({to_drop})")
                        
                        if bot.food_count <= food_to_keep:
                            should_keep = True
                
                # Всё остальное - скидываем
                if not should_keep:
                    click_slot(bot, slot)
                    logging.info(f"[DEPOSIT] Скинул: {item_name}")
            
            except Exception as e:
                logging.error(f"[DEPOSIT] Ошибка слота {slot}: {e}")
                continue
        
        close_container(bot)
        logging.info("[DEPOSIT] ✅ Сдача завершена!")
        return True
        
    except Exception as e:
        logging.error(f"[DEPOSIT] Ошибка: {e}")
        try:
            close_container(bot)
        except:
            pass
        return False


def check_missing_items(bot):
    """
    Проверяет, чего не хватает в инвентаре
    Возвращает список недостающих предметов
    """
    missing = []
    
    if not bot.has_invis_potion:
        missing.append("зелье невидимости")
    
    if not bot.has_speed_potion:
        missing.append("зелье скорости")
    
    if bot.food_count < FOOD_NEEDED:
        missing.append(f"еда ({bot.food_count}/{FOOD_NEEDED})")
    
    return missing