# ========================================
# ★ ПОИСК БЛОКОВ И ESP ★
# ========================================

import math
import logging
from net.minecraft.core.BlockPos import BlockPos


def find_blocks_with_radius(bot, block_type, radius):
    """Ищет блоки в радиусе по всем Y"""
    blocks = []
    px, py, pz = int(bot.player.getX()), int(bot.player.getY()), int(bot.player.getZ())
    
    for y in range(py - 5, py + 6):
        for x in range(px - radius, px + radius + 1):
            for z in range(pz - radius, pz + radius + 1):
                try:
                    block = bot.world.getBlockState(BlockPos(x, y, z))
                    if block_type in str(block.getBlock().getRegistryName()):
                        blocks.append((x, y, z))
                except:
                    continue
    return blocks


def scan_for_vases_esp(bot):
    """ESP сканирование ваз в радиусе"""
    bot.vase_list = []
    px, py, pz = int(bot.player.getX()), int(bot.player.getY()), int(bot.player.getZ())
    
    for y in range(py - 5, py + 6):
        for x in range(px - bot.ESP_RADIUS, px + bot.ESP_RADIUS + 1):
            for z in range(pz - bot.ESP_RADIUS, pz + bot.ESP_RADIUS + 1):
                try:
                    block = bot.world.getBlockState(BlockPos(x, y, z))
                    block_name = str(block.getBlock().getRegistryName())
                    if "vase" in block_name.lower() or "pot" in block_name.lower():
                        dist = math.sqrt((x-px)**2 + (y-py)**2 + (z-pz)**2)
                        bot.vase_list.append({
                            'x': x, 'y': y, 'z': z,
                            'distance': dist,
                            'block': block_name
                        })
                except:
                    continue
    
    bot.vase_list.sort(key=lambda v: v['distance'])


def has_sign_nearby(bot, x, y, z):
    """Проверяет, есть ли табличка рядом с блоком"""
    offsets = [(0,1,0), (0,-1,0), (1,0,0), (-1,0,0), (0,0,1), (0,0,-1)]
    for dx, dy, dz in offsets:
        try:
            block = bot.world.getBlockState(BlockPos(x + dx, y + dy, z + dz))
            if "sign" in str(block.getBlock().getRegistryName()).lower():
                return True
        except:
            continue
    return False