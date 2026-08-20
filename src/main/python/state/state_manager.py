# ========================================
# ★ МЕНЕДЖЕР СОСТОЯНИЯ БОТА ★
# ========================================

import json
import os
import logging

# Настройка логирования
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def save_state(bot):
    """
    Сохраняет состояние бота в JSON файл
    
    Args:
        bot: Экземпляр FunTimeEndBot
    """
    state = {
        'total_vases_broken': bot.total_vases_broken,
        'total_farms': bot.total_farms,
        'phase': bot.phase,
        'has_brush': bot.has_brush,
        'has_invis_potion': bot.has_invis_potion,
        'has_speed_potion': bot.has_speed_potion,
        'food_count': bot.food_count,
        'vases_broken_since_deposit': bot.vases_broken_since_deposit,
        'cooldown_end': bot.cooldown_end,
        'an323_used': bot.an323_used,
        'waiting_for_start': bot.waiting_for_start,
        'prepare_complete': bot.prepare_complete,
        'deposit_done': bot.deposit_done,
        'portal_found': bot.portal_found,
        'portal_search_start': bot.portal_search_start,
        'last_progress': bot.last_progress,
        'mode': bot.mode
    }
    
    try:
        # Создаём папку если её нет
        os.makedirs(os.path.dirname(bot.state_file), exist_ok=True)
        
        with open(bot.state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=4, ensure_ascii=False)
        
        logging.debug(f"[SAVE] Состояние сохранено: {bot.state_file}")
        return True
        
    except Exception as e:
        logging.error(f"[SAVE] Ошибка сохранения: {e}")
        return False


def load_state(bot):
    """
    Загружает состояние бота из JSON файла
    
    Args:
        bot: Экземпляр FunTimeEndBot
    
    Returns:
        bool: True если загрузка успешна, иначе False
    """
    if not os.path.exists(bot.state_file):
        logging.info("[LOAD] Файл состояния не найден, создаю новый")
        return False
    
    try:
        with open(bot.state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # Загружаем значения с проверкой на существование
        bot.total_vases_broken = state.get('total_vases_broken', 0)
        bot.total_farms = state.get('total_farms', 0)
        bot.phase = state.get('phase', 'PREPARE')
        bot.has_brush = state.get('has_brush', False)
        bot.has_invis_potion = state.get('has_invis_potion', False)
        bot.has_speed_potion = state.get('has_speed_potion', False)
        bot.food_count = state.get('food_count', 0)
        bot.vases_broken_since_deposit = state.get('vases_broken_since_deposit', 0)
        bot.cooldown_end = state.get('cooldown_end', 0)
        bot.an323_used = state.get('an323_used', False)
        bot.waiting_for_start = state.get('waiting_for_start', False)
        bot.prepare_complete = state.get('prepare_complete', False)
        bot.deposit_done = state.get('deposit_done', False)
        bot.portal_found = state.get('portal_found', False)
        bot.portal_search_start = state.get('portal_search_start', None)
        bot.last_progress = state.get('last_progress', time.time())
        bot.mode = state.get('mode', 'SAFE_WALK')
        
        logging.info(f"[LOAD] Загружено состояние:")
        logging.info(f"  - Фармов: {bot.total_farms}")
        logging.info(f"  - Ваз разбито: {bot.total_vases_broken}")
        logging.info(f"  - Фаза: {bot.phase}")
        logging.info(f"  - Кисточка: {'есть' if bot.has_brush else 'нет'}")
        logging.info(f"  - Ожидание .start end: {'да' if bot.waiting_for_start else 'нет'}")
        
        return True
        
    except Exception as e:
        logging.error(f"[LOAD] Ошибка загрузки: {e}")
        return False


def reset_state(bot):
    """
    Сбрасывает состояние бота (удаляет файл сохранения)
    
    Args:
        bot: Экземпляр FunTimeEndBot
    """
    try:
        if os.path.exists(bot.state_file):
            os.remove(bot.state_file)
            logging.info(f"[RESET] Файл состояния удалён: {bot.state_file}")
        return True
    except Exception as e:
        logging.error(f"[RESET] Ошибка удаления: {e}")
        return False


def get_state_info(bot):
    """
    Возвращает информацию о текущем состоянии бота для отладки
    
    Args:
        bot: Экземпляр FunTimeEndBot
    
    Returns:
        dict: Словарь с информацией о состоянии
    """
    return {
        'phase': bot.phase,
        'mode': bot.mode,
        'has_brush': bot.has_brush,
        'has_invis_potion': bot.has_invis_potion,
        'has_speed_potion': bot.has_speed_potion,
        'food_count': bot.food_count,
        'vases_broken_since_deposit': bot.vases_broken_since_deposit,
        'total_vases_broken': bot.total_vases_broken,
        'total_farms': bot.total_farms,
        'cooldown_remaining': max(0, bot.cooldown_end - time.time()),
        'waiting_for_start': bot.waiting_for_start,
        'an323_used': bot.an323_used,
        'portal_found': bot.portal_found,
        'target_vase': bot.target_vase,
        'vases_in_esp': len(bot.vase_list)
    }


def print_state_info(bot):
    """
    Выводит информацию о состоянии бота в лог
    
    Args:
        bot: Экземпляр FunTimeEndBot
    """
    info = get_state_info(bot)
    logging.info("=" * 50)
    logging.info("📊 СТАТУС БОТА:")
    logging.info(f"  Фаза: {info['phase']}")
    logging.info(f"  Режим: {info['mode']}")
    logging.info(f"  Кисточка: {'✅' if info['has_brush'] else '❌'}")
    logging.info(f"  Зелье невидимости: {'✅' if info['has_invis_potion'] else '❌'}")
    logging.info(f"  Зелье скорости: {'✅' if info['has_speed_potion'] else '❌'}")
    logging.info(f"  Еда: {info['food_count']} шт")
    logging.info(f"  Ваз разбито: {info['vases_broken_since_deposit']}/{VASES_BEFORE_DEPOSIT}")
    logging.info(f"  Всего ваз: {info['total_vases_broken']}")
    logging.info(f"  Всего фармов: {info['total_farms']}")
    logging.info(f"  КД: {info['cooldown_remaining']:.1f}с")
    logging.info(f"  Ваз в ESP: {info['vases_in_esp']}")
    logging.info(f"  Ожидание .start end: {'✅' if info['waiting_for_start'] else '❌'}")
    logging.info("=" * 50)