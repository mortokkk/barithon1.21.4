# ========================================
# ★ РАБОТА С СУНДУКАМИ ★
# ========================================

import time
import logging
from net.minecraft.core.BlockPos import BlockPos
from net.minecraft.world.phys.Vec3 import Vec3
from net.minecraft.core.Direction import Direction
from net.minecraft.world.InteractionHand import InteractionHand
from net.minecraft.world.phys.BlockHitResult import BlockHitResult

from .esp import has_sign_nearby
from .movement import walk_to


def open_chest_safe(bot, chest_pos):
    """Открывает сундук в 1.21.4 (5 способов)"""
    bot.baritone.getPathingBehavior().cancelEverything()
    time.sleep(0.3)
    
    # Выбираем пустую руку
    inventory = bot.player.getInventory()
    empty_slot = -1
    for slot in range(9):
        if inventory.getItem(slot) is None:
            empty_slot = slot
            break
    
    if empty_slot != -1:
        inventory.selected = empty_slot
    else:
        inventory.selected = 0
    time.sleep(0.1)
    
    pos = BlockPos(chest_pos[0], chest_pos[1], chest_pos[2])
    
    # Способ 1: player.openChest
    try:
        bot.mc.player.openChest(pos)
        time.sleep(0.5)
        if is_container_open(bot):
            logging.info("[OPEN] Сундук открыт (способ 1)")
            return True
    except:
        pass
    
    # Способ 2: playerController.openChest
    try:
        bot.mc.playerController.openChest(pos)
        time.sleep(0.5)
        if is_container_open(bot):
            logging.info("[OPEN] Сундук открыт (способ 2)")
            return True
    except:
        pass
    
    # Способ 3: interactWithBlock
    try:
        vec = Vec3(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5)
        bot.player.lookAt(vec)
        time.sleep(0.1)
        result = BlockHitResult(vec, Direction.UP, pos, False)
        bot.mc.playerController.interactWithBlock(bot.player, result, InteractionHand.MAIN_HAND)
        time.sleep(0.5)
        if is_container_open(bot):
            logging.info("[OPEN] Сундук открыт (способ 3)")
            return True
    except:
        pass
    
    # Способ 4: пакет
    try:
        from net.minecraft.network.protocol.game import ServerboundUseItemOnPacket
        packet = ServerboundUseItemOnPacket(
            InteractionHand.MAIN_HAND,
            pos,
            Direction.UP,
            Vec3(0.5, 0.5, 0.5)
        )
        bot.mc.player.connection.send(packet)
        time.sleep(0.5)
        if is_container_open(bot):
            logging.info("[OPEN] Сундук открыт (способ 4)")
            return True
    except:
        pass
    
    # Способ 5: правый клик
    try:
        bot.player.lookAt(Vec3(pos.getX() + 0.5, pos.getY() + 0.5, pos.getZ() + 0.5))
        time.sleep(0.1)
        bot.mc.playerController.rightClickBlock(
            bot.player,
            pos,
            Direction.UP,
            Vec3(0.5, 0.5, 0.5)
        )
        time.sleep(0.5)
        if is_container_open(bot):
            logging.info("[OPEN] Сундук открыт (способ 5)")
            return True
    except:
        pass
    
    logging.error("[OPEN] ❌ Не удалось открыть сундук!")
    return False


def is_container_open(bot):
    """Проверяет, открыт ли контейнер"""
    try:
        container = bot.mc.player.containerMenu
        if container is None:
            return False
        container_class = str(container.getClass().getName())
        return "ChestMenu" in container_class or "Container" in container_class
    except:
        return False


def close_container(bot):
    """Закрывает открытый контейнер"""
    try:
        bot.mc.player.closeContainer()
        time.sleep(0.2)
        return True
    except:
        return False


def get_chest_inventory(bot):
    """Получает инвентарь открытого сундука"""
    try:
        container = bot.mc.player.containerMenu
        if container is None:
            return None
        if hasattr(container, 'getItems'):
            return container.getItems()
        if hasattr(container, 'slots'):
            items = []
            for slot in container.slots:
                if hasattr(slot, 'getItem'):
                    items.append(slot.getItem())
                else:
                    items.append(slot)
            return items
        return None
    except:
        return None


def click_slot(bot, slot):
    """Кликает по слоту в открытом контейнере"""
    try:
        container = bot.mc.player.containerMenu
        if container is None:
            return False
        
        if hasattr(container, 'click'):
            container.click(slot, 0, 0, bot.player)
            time.sleep(0.1)
            return True
        
        try:
            bot.mc.playerController.clickWindow(container.containerId, slot, 0, 0, bot.player)
            time.sleep(0.1)
            return True
        except:
            pass
        
        return False
    except:
        return False


def count_empty_slots_in_chest(bot):
    """Считает пустые слоты в сундуке"""
    try:
        items = get_chest_inventory(bot)
        if items is None:
            return 0
        return sum(1 for item in items if item is None)
    except:
        return 0


def find_nearest_chest_with_sign(bot):
    """Находит ближайший сундук с табличкой"""
    chests = find_blocks_with_radius(bot, "chest", 20)
    for chest in chests:
        if has_sign_nearby(bot, chest[0], chest[1], chest[2]):
            return chest
    return None


def find_nearest_chest_without_sign(bot):
    """Находит ближайший сундук БЕЗ таблички"""
    chests = find_blocks_with_radius(bot, "chest", 20)
    for chest in chests:
        if not has_sign_nearby(bot, chest[0], chest[1], chest[2]):
            return chest
    return None