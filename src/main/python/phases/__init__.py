# ========================================
# ★ ИНИЦИАЛИЗАЦИЯ ФАЗ ★
# ========================================

from .prepare import prepare_phase
from .farm import farm_phase
from .deposit import deposit_phase, deposit_and_check_phase
from .wait import wait_for_cooldown_phase, wait_for_portal_phase
from .exit import exit_phase

__all__ = [
    'prepare_phase',
    'farm_phase',
    'deposit_phase',
    'deposit_and_check_phase',
    'wait_for_cooldown_phase',
    'wait_for_portal_phase',
    'exit_phase'
]