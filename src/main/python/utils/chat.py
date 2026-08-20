# ========================================
# ★ РАБОТА С ЧАТОМ ★
# ========================================

import time
import logging


def send_command(bot, command):
    """Отправляет команду в чат"""
    try:
        bot.mc.player.sendChatMessage(command)
        logging.info(f"[CHAT] {command}")
        time.sleep(0.5)
        return True
    except Exception as e:
        logging.error(f"[CHAT] Ошибка: {e}")
        return False


def client_chat_log(bot, message):
    """Логирует сообщение в клиентский чат (только для игрока)"""
    try:
        bot.mc.player.sendSystemMessage(message)
        logging.info(f"[CLIENT] {message}")
    except Exception as e:
        logging.error(f"[CLIENT] Ошибка: {e}")