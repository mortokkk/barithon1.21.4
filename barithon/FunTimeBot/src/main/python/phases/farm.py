# ========================================
# ★ ФАЗА ФАРМА ★
# ========================================

import time
import logging
import random
from config import *
from utils.movement import *
from utils.combat import *
from utils.esp import *
from utils.inventory import *

def farm_phase(bot):
    """
    ФАЗА ФАРМА:
    1. Проверка кисточки, зелий
    2. SAFE_WALK → NEURAL → RANDOM → BARITONE → FARM_SAND
    3. После 5 ваз → проверка КД → DEPOSIT или WAIT_FOR_COOLDOWN
    """
    try:
        if bot.check_if_dead():
            return
        
        # Проверка кисточки
        if not bot.has_brush:
            logging.warning("[⚠] Нет кисточки! Ищу новую")
            bot.searching_for_brush = True
            bot.mode = "RANDOM"
            return
        
        # Проверка зелий
        if not bot.has_invis_potion or not bot.has_speed_potion:
            logging.warning("[⚠] Закончились зелья!")
            bot.phase = "PREPARE"
            return
        
        # Проверка: разбито 5 ваз
        if bot.vases_broken_since_deposit >= VASES_BEFORE_DEPOSIT:
            logging.info(f"[FARM] Разбито {VASES_BEFORE_DEPOSIT} ваз")
            bot.vases_broken_since_deposit = 0
            bot.total_vases_broken += VASES_BEFORE_DEPOSIT
            
            if time.time() < bot.cooldown_end:
                remaining = bot.cooldown_end - time.time()
                logging.info(f"[FARM] КД активен ({remaining:.1f}с)")
                bot.phase = "WAIT_FOR_COOLDOWN"
                return
            else:
                logging.info("[FARM] КД нет, перехожу к DEPOSIT")
                bot.phase = "DEPOSIT"
                return
        
        # ★ ОБНОВЛЯЕМ СОСТОЯНИЕ ★
        bot.update_state()
        
        # ★ РЕЖИМЫ ДВИЖЕНИЯ ★
        if bot.mode == "SAFE_WALK":
            safe_walk_to_castle(bot)
        elif bot.mode == "NEURAL":
            neural_mode(bot)
        elif bot.mode == "RANDOM":
            random_with_esp(bot)
        elif bot.mode == "BARITONE":
            baritone_mode(bot)
        elif bot.mode == "FARM_SAND":
            farm_sand(bot)
        
        bot.last_progress = time.time()
        
    except Exception as e:
        logging.error(f"[FARM] Ошибка: {e}")
        time.sleep(1)


# ========================================
# ПОДРЕЖИМЫ
# ========================================

def safe_walk_to_castle(bot):
    """Идём к крепости с обходом дыр"""
    logging.info("[SAFE_WALK] Иду к крепости")
    bot.baritone.getSettings().safeWalk.value = True
    
    goal = GoalBlock(
        int(CASTLE_COORDS[0]),
        int(CASTLE_COORDS[1]),
        int(CASTLE_COORDS[2])
    )
    bot.baritone.getPathingBehavior().setGoal(goal)
    bot.baritone.getPathingBehavior().path()
    
    if bot.distance_to(NEURAL_TRIGGER) < 5:
        logging.info("[SAFE_WALK] Достиг триггера → NEURAL")
        bot.mode = "NEURAL"
        bot.baritone.getPathingBehavior().cancelEverything()


def neural_mode(bot):
    """Рывок к X=0 (дыра в полу)"""
    logging.info("[NEURAL] Рывок к X=0")
    bot.baritone.getSettings().safeWalk.value = False
    
    dx = HOLE_COORDS[0] - bot.player.getX()
    dz = HOLE_COORDS[2] - bot.player.getZ()
    target_yaw = math.degrees(math.atan2(dz, dx)) - 90
    
    # Плавный поворот
    current_yaw = bot.player.getYRot()
    delta = target_yaw - current_yaw
    while delta > 180:
        delta -= 360
    while delta < -180:
        delta += 360
    
    steps = 20
    for i in range(steps):
        bot.player.setYRot(current_yaw + delta / steps * i)
        time.sleep(0.01)
    
    # Бежим
    bot.mc.options.keyForward.setPressed(True)
    bot.mc.options.keySprint.setPressed(True)
    
    start = time.time()
    while time.time() - start < 5:
        if abs(bot.player.getX()) < 2:
            logging.info("[NEURAL] Достиг X=0")
            break
        if bot.player.getY() < 60:
            logging.info("[NEURAL] ПРОВАЛИЛСЯ В ДЫРУ!")
            break
        time.sleep(0.05)
    
    bot.mc.options.keyForward.setPressed(False)
    bot.mc.options.keySprint.setPressed(False)
    bot.mode = "RANDOM"


def random_with_esp(bot):
    """Рандомное движение с ESP поиском ваз"""
    logging.info("[RANDOM+ESP] Сканирую окружение")
    scan_for_vases_esp(bot)
    
    if bot.vase_list:
        nearest = get_nearest_vase(bot)
        if nearest:
            bot.target_vase = nearest
            bot.mode = "BARITONE"
            logging.info(f"[RANDOM+ESP] Нашёл вазу в {nearest}")
            return
    
    rand_x = random.randint(-15, 15)
    rand_z = random.randint(180, 220)
    rand_y = int(bot.player.getY())
    
    logging.info(f"[RANDOM+ESP] Иду рандомно к X={rand_x}, Z={rand_z}")
    walk_to(bot, rand_x, rand_y, rand_z, timeout=5)
    time.sleep(1)
    bot.mode = "RANDOM"


def get_nearest_vase(bot):
    """Возвращает координаты ближайшей вазы"""
    if not bot.vase_list:
        return None
    return (bot.vase_list[0]['x'], bot.vase_list[0]['y'], bot.vase_list[0]['z'])


def baritone_mode(bot):
    """Навигация к вазе или по координатам"""
    logging.info("[BARITONE] Навигация")
    
    if bot.target_vase:
        go_to_vase(bot, bot.target_vase)
        return
    
    if bot.vase_list:
        nearest = get_nearest_vase(bot)
        if nearest:
            bot.target_vase = nearest
            go_to_vase(bot, nearest)
            return
    
    rand_x = random.randint(-10, 10)
    rand_z = random.randint(180, 220)
    rand_y = int(bot.player.getY())
    
    goal = GoalBlock(rand_x, rand_y, rand_z)
    bot.baritone.getPathingBehavior().setGoal(goal)
    bot.baritone.getPathingBehavior().path()
    
    timeout = 10
    start = time.time()
    while time.time() - start < timeout:
        scan_for_vases_esp(bot)
        if bot.vase_list:
            logging.info("[BARITONE] Обнаружена новая ваза, меняю цель")
            bot.baritone.getPathingBehavior().cancelEverything()
            bot.target_vase = get_nearest_vase(bot)
            return
        time.sleep(0.5)
    
    logging.info("[BARITONE] Ничего не нашёл, переключаюсь на RANDOM")
    bot.mode = "RANDOM"


def go_to_vase(bot, vase_coords):
    """Идёт к вазе и ломает её"""
    logging.info(f"[BARITONE] Иду к вазе {vase_coords}")
    bot.baritone.getSettings().safeWalk.value = True
    
    goal = GoalBlock(
        int(vase_coords[0]),
        int(vase_coords[1]),
        int(vase_coords[2])
    )
    bot.baritone.getPathingBehavior().setGoal(goal)
    bot.baritone.getPathingBehavior().path()
    
    timeout = 15
    start = time.time()
    while bot.distance_to(vase_coords) > 2:
        if time.time() - start > timeout:
            logging.warning("[BARITONE] Таймаут достижения вазы")
            bot.target_vase = None
            bot.mode = "RANDOM"
            return
        time.sleep(0.1)
    
    logging.info("[BARITONE] Ломаю вазу!")
    break_block(bot, vase_coords)
    collect_loot(bot)
    
    bot.vases_broken_since_deposit += 1
    logging.info(f"[BARITONE] Разбито ваз: {bot.vases_broken_since_deposit}/{VASES_BEFORE_DEPOSIT}")
    
    if bot.check_inventory_for_brush():
        logging.info("[BARITONE] 🎉 КИСТОЧКА ВЫПАЛА ИЗ ВАЗЫ!")
        bot.has_brush = True
        bot.cooldown_end = time.time() + VASE_COOLDOWN
        bot.mode = "FARM_SAND"
    else:
        logging.info("[BARITONE] Кисточка НЕ выпала, ищу следующую")
        bot.target_vase = None
        bot.vase_list = []
        bot.mode = "RANDOM"


def farm_sand(bot):
    """Фарм песка кисточкой"""
    logging.info("[FARM_SAND] Фарм песка")
    
    # Проверяем КД
    if time.time() < bot.cooldown_end:
        remaining = bot.cooldown_end - time.time()
        logging.info(f"[FARM_SAND] Жду КД {remaining:.1f}с")
        time.sleep(min(remaining, 1))
        return
    
    # Ищем песок
    sand = find_sand_block(bot)
    
    if sand:
        logging.info(f"[FARM_SAND] Копаю песок в {sand}")
        use_item_on_block(bot, sand)
        
        # Проверяем, не сломалась ли кисточка
        if not bot.check_inventory_for_brush():
            logging.info("[FARM_SAND] ❌ Кисточка сломалась!")
            bot.has_brush = False
            
            if time.time() < bot.cooldown_end:
                logging.info("[FARM_SAND] КД активен, ищу вазы")
                bot.mode = "RANDOM"
            else:
                logging.info("[FARM_SAND] КД нет, перехожу к DEPOSIT_AND_CHECK")
                bot.phase = "DEPOSIT_AND_CHECK"
        else:
            logging.info("[FARM_SAND] Кисточка ещё есть, продолжаю")
            time.sleep(0.5)
    else:
        logging.info("[FARM_SAND] Песок не найден, ищу дальше")
        time.sleep(1)


def find_sand_block(bot):
    """Находит блок подозрительного песка"""
    sx, sy, sz = SAND_AREA
    
    for x in range(sx - 5, sx + 6):
        for z in range(sz - 5, sz + 6):
            try:
                block = bot.world.getBlockState(BlockPos(x, sy, z))
                block_name = str(block.getBlock().getRegistryName())
                if "suspicious_sand" in block_name.lower():
                    return (x, sy, z)
            except:
                continue
    return None