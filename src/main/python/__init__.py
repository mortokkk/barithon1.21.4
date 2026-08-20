# ========================================
# ★ ПАКЕТ БОТА ★
# ========================================

from .bot import FunTimeEndBot
from .config import *
from .phases import *
from .utils import *

__all__ = [
    'FunTimeEndBot',
    # config
    'CASTLE_COORDS',
    'NEURAL_TRIGGER',
    'HOLE_COORDS',
    'SAND_AREA',
    'VASES_BEFORE_DEPOSIT',
    'FOOD_NEEDED',
    'VASE_COOLDOWN',
    'PORTAL_SEARCH_RADIUS',
    'ESP_RADIUS',
    'SCAN_INTERVAL',
    'PREPARE_TIMEOUT',
    'MOVE_TIMEOUT',
    'FARM_TIMEOUT',
    'PORTAL_SEARCH_TIMEOUT',
    'HUB_WAIT_TIME',
    'COMMAND_AN323',
    'COMMAND_AN324',
    'COMMAND_HUB',
    'COMMAND_SPAWN',
    'COMMAND_KIT',
    # phases
    'prepare_phase',
    'farm_phase',
    'deposit_phase',
    'deposit_and_check_phase',
    'wait_for_cooldown_phase',
    'wait_for_portal_phase',
    'exit_phase',
    # utils
    'check_inventory_for_brush',
    'count_food_in_inventory',
    'is_food',
    'get_item_in_slot',
    'open_chest_safe',
    'is_container_open',
    'close_container',
    'get_chest_inventory',
    'click_slot',
    'count_empty_slots_in_chest',
    'walk_to',
    'distance_to',
    'break_block',
    'use_item_on_block',
    'collect_loot',
    'find_blocks_with_radius',
    'scan_for_vases_esp',
    'has_sign_nearby',
    'find_nearest_chest_with_sign',
    'find_nearest_chest_without_sign',
    'send_command',
    'client_chat_log'
]