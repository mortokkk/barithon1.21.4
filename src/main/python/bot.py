# ========================================
# ★ ГЛАВНЫЙ ФАЙЛ БОТА ★
# ========================================

import random
import time
import math
import json
import os
import logging

# BARITONE 1.21.4
from baritone.api.BaritoneAPI import BaritoneAPI
from baritone.api.pathing.goals import GoalBlock, GoalXZ

# MINECRAFT 1.21.4
from net.minecraft.core.BlockPos import BlockPos
from net.minecraft.world.phys.Vec3 import Vec3
from net.minecraft.world.item.Items import Items
from net.minecraft.world.item.alchemy.PotionUtils import PotionUtils
from net.minecraft.world.level.block.Blocks import Blocks
from net.minecraft.world.inventory import Slot
from net.minecraft.world.InteractionHand import InteractionHand
from net.minecraft.world.phys.BlockHitResult import BlockHitResult
from net.minecraft.core.Direction import Direction

# ★ ИМПОРТЫ ФАЗ ★
from phases.prepare import prepare_phase
from phases.farm import farm_phase
from phases.deposit import deposit_phase, deposit_and_check_phase
from phases.wait import wait_for_cooldown_phase, wait_for_portal_phase
from phases.exit import exit_phase

# ★ ИМПОРТЫ УТИЛИТ ★
from utils.inventory import *
from utils.chest import *
from utils.movement import *
from utils.combat import *
from utils.esp import *
from utils.chat import *

# ★ ИМПОРТ КОНФИГА ★
from config import *

# ========================================
# НАСТРОЙКА ЛОГИРОВАНИЯ
# ========================================
logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


# ========================================
# ★ ГЛАВНЫЙ КЛАСС БОТА ★
# ========================================
class FunTimeEndBot:
    def __init__(self):
        """Инициализация бота"""
        
        # BARITONE 1.21.4
        self.baritone = BaritoneAPI.getProvider().getPrimaryBaritone()
        self.mc = self.baritone.getMinecraft()
        
        # ИГРОК И МИР 1.21.4
        self.player = self.mc.getPlayer()
        self.world = self.mc.getLevel()
        
        # ★ СОСТОЯНИЯ ★
        self.phase = "PREPARE"          # PREPARE, WAIT_FOR_PORTAL, FARM, WAIT_FOR_COOLDOWN, DEPOSIT, DEPOSIT_AND_CHECK, EXIT
        self.mode = "SAFE_WALK"         # SAFE_WALK, NEURAL, RANDOM, BARITONE, FARM_SAND
        self.paused = False
        
        # ★ ФЛАГИ ★
        self.has_invis_potion = False
        self.has_speed_potion = False
        self.has_food = False
        self.food_count = 0
        self.has_brush = False
        self.searching_for_brush = False
        
        # ★ СЧЁТЧИКИ ★
        self.vases_broken_since_deposit = 0
        self.total_vases_broken = 0
        self.total_farms = 0
        
        # ★ ВРЕМЕНА ★
        self.cooldown_end = 0
        self.last_scan = 0
        self.portal_search_start = None
        self.last_progress = time.time()
        
        # ★ ЦЕЛИ ★
        self.target_vase = None
        self.vase_list = []
        self.chest_with_sign = None
        self.chest_without_sign = None
        self.portal_coords = None
        self.target_chest = None
        
        # ★ ФЛАГИ ★
        self.an323_used = False
        self.deposit_done = False
        self.portal_found = False
        self.waiting_for_start = False
        self.prepare_complete = False
        
        # ★ ТАЙМАУТЫ ★
        self.last_progress = time.time()
        
        # ★ СОХРАНЕНИЕ ★
        self.state_file = "data/bot_state.json"
        self.load_state()
        
        logging.info("[INIT] Бот запущен (1.21.4)")
        logging.info(f"[INIT] Загружено: {self.total_farms} фармов, {self.total_vases_broken} ваз")
    
    # ========================================
    # 1. СОХРАНЕНИЕ/ЗАГРУЗКА СОСТОЯНИЯ
    # ========================================
    def save_state(self):
        """Сохраняет состояние бота в JSON"""
        state = {
            'total_vases_broken': self.total_vases_broken,
            'total_farms': self.total_farms,
            'phase': self.phase,
            'has_brush': self.has_brush,
            'has_invis_potion': self.has_invis_potion,
            'has_speed_potion': self.has_speed_potion,
            'food_count': self.food_count,
            'vases_broken_since_deposit': self.vases_broken_since_deposit,
            'cooldown_end': self.cooldown_end,
            'an323_used': self.an323_used,
            'waiting_for_start': self.waiting_for_start
        }
        try:
            # Создаём папку если её нет
            os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(state, f)
        except Exception as e:
            logging.error(f"[SAVE] Ошибка: {e}")
    
    def load_state(self):
        """Загружает состояние бота из JSON"""
        if not os.path.exists(self.state_file):
            return
        try:
            with open(self.state_file, 'r') as f:
                state = json.load(f)
                self.total_vases_broken = state.get('total_vases_broken', 0)
                self.total_farms = state.get('total_farms', 0)
                self.waiting_for_start = state.get('waiting_for_start', False)
                logging.info(f"[LOAD] Загружено: {self.total_farms} фармов, {self.total_vases_broken} ваз")
        except Exception as e:
            logging.error(f"[LOAD] Ошибка: {e}")
    
    # ========================================
    # 2. ПРОВЕРКА СМЕРТИ
    # ========================================
    def check_if_dead(self):
        """Проверяет, жив ли игрок"""
        try:
            if self.player.getHealth() <= 0:
                logging.warning("[⚠] Игрок умер! Перезапуск")
                self.reset_everything()
                self.phase = "PREPARE"
                return True
            return False
        except:
            return True
    
    # ========================================
    # 3. ОБНОВЛЕНИЕ СОСТОЯНИЯ
    # ========================================
    def update_state(self):
        """Обновляет состояние бота"""
        try:
            self.check_potions()
            self.has_brush = self.check_inventory_for_brush()
            self.food_count = self.count_food_in_inventory()
            self.has_food = self.food_count >= FOOD_NEEDED
            
            if time.time() - self.last_scan > SCAN_INTERVAL:
                self.scan_for_vases_esp()
                self.last_scan = time.time()
            
        except Exception as e:
            logging.error(f"[UPDATE] Ошибка: {e}")
    
    def check_potions(self):
        """Проверяет наличие зелий (эффекты + инвентарь)"""
        has_invis_effect = False
        has_speed_effect = False
        
        try:
            effects = self.player.getActiveEffects()
            for effect in effects:
                effect_name = str(effect.getEffect().getRegistryName())
                if "invisibility" in effect_name.lower():
                    has_invis_effect = True
                elif "speed" in effect_name.lower() or "swiftness" in effect_name.lower():
                    has_speed_effect = True
        except:
            pass
        
        if has_invis_effect:
            self.has_invis_potion = True
        if has_speed_effect:
            self.has_speed_potion = True
        
        if not has_invis_effect or not has_speed_effect:
            inventory = self.player.getInventory()
            for slot in range(0, 36):
                try:
                    item = inventory.getItem(slot)
                    if item is None:
                        continue
                    item_name = str(item.getItem().getRegistryName())
                    if "invisibility" in item_name.lower():
                        self.has_invis_potion = True
                    elif "swiftness" in item_name.lower() or "speed" in item_name.lower():
                        self.has_speed_potion = True
                except:
                    continue
    
    def check_inventory_for_brush(self):
        """Проверяет, есть ли кисточка в инвентаре"""
        inventory = self.player.getInventory()
        for slot in range(0, 36):
            try:
                item = inventory.getItem(slot)
                if item is None:
                    continue
                if "brush" in str(item.getItem().getRegistryName()):
                    return True
            except:
                continue
        return False
    
    def count_food_in_inventory(self):
        """Считает еду в инвентаре"""
        count = 0
        inventory = self.player.getInventory()
        for slot in range(0, 36):
            try:
                item = inventory.getItem(slot)
                if item is None:
                    continue
                if self.is_food(item):
                    count += item.getCount()
            except:
                continue
        return count
    
    def is_food(self, item):
        """Проверяет, является ли предмет едой"""
        item_name = str(item.getItem().getRegistryName())
        food_items = ["apple", "bread", "steak", "porkchop", "chicken", "beef", "carrot", "potato", "golden_apple"]
        return any(f in item_name.lower() for f in food_items)
    
    def distance_to(self, pos):
        """Расстояние до позиции"""
        return math.sqrt(
            (self.player.getX() - pos[0])**2 +
            (self.player.getY() - pos[1])**2 +
            (self.player.getZ() - pos[2])**2
        )
    
    # ========================================
    # 4. ПРОВЕРКА КОМАНДЫ .start end
    # ========================================
    def check_for_start_command(self):
        """Проверяет клиентский чат на .start end"""
        try:
            chat_gui = self.mc.gui.getChat()
            messages = chat_gui.getRecentMessages()
            
            for msg in messages:
                text = msg.getMessage()
                if ".start end" in text.lower():
                    logging.info(f"[COMMAND] Обнаружена команда: {text}")
                    self.on_start_command()
                    chat_gui.clearMessages()
                    break
                    
        except Exception as e:
            logging.error(f"[COMMAND] Ошибка: {e}")
    
    def on_start_command(self):
        """Обработчик команды .start end"""
        if self.waiting_for_start:
            logging.info("[COMMAND] ✅ Получена команда .start end! Запускаю фарм")
            self.client_chat_log("✅ Получена команда .start end! Запускаю фарм")
            
            self.waiting_for_start = False
            self.phase = "FARM"
            self.prepare_complete = True
            self.vases_broken_since_deposit = 0
            self.last_progress = time.time()
            
            self.baritone.getSettings().safeWalk.value = True
            self.save_state()
    
    def client_chat_log(self, message):
        """Логирует сообщение в клиентский чат"""
        try:
            self.mc.player.sendSystemMessage(message)
            logging.info(f"[CLIENT] {message}")
        except Exception as e:
            logging.error(f"[CLIENT] Ошибка: {e}")
    
    # ========================================
    # 5. СБРОС
    # ========================================
    def reset_everything(self):
        """Полный сброс состояния"""
        logging.info("[RESET] Сброс")
        self.an323_used = False
        self.vases_broken_since_deposit = 0
        self.has_invis_potion = False
        self.has_speed_potion = False
        self.has_food = False
        self.food_count = 0
        self.chest_with_sign = None
        self.chest_without_sign = None
        self.target_vase = None
        self.vase_list = []
        self.mode = "SAFE_WALK"
        self.searching_for_brush = False
        self.deposit_done = False
        self.portal_found = False
        self.portal_coords = None
        self.last_progress = time.time()
        self.cooldown_end = 0
        self.prepare_complete = False
        self.waiting_for_start = False
        self.portal_search_start = None
        self.save_state()
        
        self.baritone.getSettings().safeWalk.value = True
    
    # ========================================
    # 6. ГЛАВНЫЙ ЦИКЛ
    # ========================================
    def main_loop(self):
        """Главный цикл бота"""
        while True:
            if self.paused:
                time.sleep(1)
                continue
            
            self.check_for_start_command()
            
            if self.check_if_dead():
                continue
            
            self.update_state()
            
            if self.waiting_for_start:
                time.sleep(1)
                continue
            
            # Таймаут фарма
            if self.phase == "FARM":
                if time.time() - self.last_progress > FARM_TIMEOUT:
                    logging.warning(f"[⚠] Таймаут фарма ({FARM_TIMEOUT}с)! Перезапуск")
                    self.reset_everything()
                    self.phase = "PREPARE"
                    continue
            
            # ★ ВЫЗОВ ФАЗ ★
            if self.phase == "PREPARE":
                prepare_phase(self)
            elif self.phase == "WAIT_FOR_PORTAL":
                wait_for_portal_phase(self)
            elif self.phase == "FARM":
                farm_phase(self)
            elif self.phase == "WAIT_FOR_COOLDOWN":
                wait_for_cooldown_phase(self)
            elif self.phase == "DEPOSIT":
                deposit_phase(self)
            elif self.phase == "DEPOSIT_AND_CHECK":
                deposit_and_check_phase(self)
            elif self.phase == "EXIT":
                exit_phase(self)
            
            # Сохраняем состояние каждые 10 циклов
            if random.randint(0, 10) == 0:
                self.save_state()
            
            time.sleep(0.05)