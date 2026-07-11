import arcade
import random
import math
import time
import json
import datetime
import os
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any

import sounds
sounds.generate_all()

# ============================================================
# КОНСТАНТЫ
# ============================================================
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 650
SCREEN_TITLE = "🧠 Психо-Бой: Битва со Страхами"

PLAYER_RADIUS = 18
BULLET_SPEED = 8
LASER_SPEED = 14
ENEMY_BASE_SPEED = 1.0
ENEMIES_PER_LEVEL = 12
BOSS_BASE_HP = 20
MAX_PARTICLES = 150

UI_HEIGHT = 50
GAME_TOP = SCREEN_HEIGHT - UI_HEIGHT

POWERUP_DURATION = {
    'shield': 600,
    'power': 400,
    'laser': 300,
    'helper': 500,
}

DIFFICULTY = {
    'easy': {'speed': 1.0, 'hp': 1.0, 'boss_hp': 1.0, 'enemy_count': 10, 'boss_speed': 1.0},
    'normal': {'speed': 1.3, 'hp': 1.3, 'boss_hp': 1.4, 'enemy_count': 12, 'boss_speed': 1.2},
    'hard': {'speed': 1.6, 'hp': 1.6, 'boss_hp': 1.8, 'enemy_count': 15, 'boss_speed': 1.4},
}

# ============================================================
# ДАННЫЕ УРОВНЕЙ (10 уровней)
# ============================================================
LEVELS = [
    {
        'id': 'zoo',
        'name': 'Зоофобии',
        'subtitle': 'Животные и насекомые',
        'bg_color': (10, 13, 10),
        'accent': (76, 175, 80),
        'star_color': (165, 214, 167),
        'bg_pattern': 'forest',
        'enemies_needed': 50,
        'enemies': [
            {'name': 'Паук', 'emoji': '🕷️', 'color': (139, 0, 139), 'size': 32, 'hp': 1},
            {'name': 'Змея', 'emoji': '🐍', 'color': (46, 125, 50), 'size': 34, 'hp': 1},
            {'name': 'Оса', 'emoji': '🐝', 'color': (245, 127, 23), 'size': 28, 'hp': 1},
            {'name': 'Собака', 'emoji': '🐕', 'color': (78, 52, 46), 'size': 36, 'hp': 1},
            {'name': 'Летучая мышь', 'emoji': '🦇', 'color': (49, 27, 146), 'size': 32, 'hp': 1},
        ],
        'boss': {'name': 'Король Членистоногих', 'emoji': '🕷️', 'color': (74, 0, 51), 'size': 64},
        'affirmations': ['Я в безопасности', 'Природа прекрасна', 'Я спокоен'],
        'enemy_count': 10,
    },
    {
        'id': 'ocean',
        'name': 'Гидрофобии',
        'subtitle': 'Морские глубины',
        'bg_color': (5, 10, 30),
        'accent': (0, 150, 200),
        'star_color': (100, 200, 255),
        'bg_pattern': 'ocean',
        'enemies_needed': 55,
        'enemies': [
            {'name': 'Акула', 'emoji': '🦈', 'color': (80, 90, 110), 'size': 38, 'hp': 1},
            {'name': 'Осьминог', 'emoji': '🐙', 'color': (180, 60, 120), 'size': 34, 'hp': 1},
            {'name': 'Медуза', 'emoji': '🪼', 'color': (200, 100, 200), 'size': 30, 'hp': 1},
        ],
        'boss': {'name': 'Левиафан', 'emoji': '🐋', 'color': (10, 60, 120), 'size': 70},
        'affirmations': ['Вода — это жизнь', 'Я спокоен в глубине', 'Океан убаюкивает'],
        'enemy_count': 12,
    },
    {
        'id': 'medical',
        'name': 'Ятрофобии',
        'subtitle': 'Больницы и врачи',
        'bg_color': (25, 10, 15),
        'accent': (200, 50, 50),
        'star_color': (255, 150, 150),
        'bg_pattern': 'medical',
        'enemies_needed': 60,
        'enemies': [
            {'name': 'Шприц', 'emoji': '💉', 'color': (200, 200, 200), 'size': 30, 'hp': 1},
            {'name': 'Таблетка', 'emoji': '💊', 'color': (240, 60, 60), 'size': 28, 'hp': 1},
            {'name': 'Скальпель', 'emoji': '🔪', 'color': (180, 180, 180), 'size': 32, 'hp': 1},
        ],
        'boss': {'name': 'Доктор Страх', 'emoji': '🧑‍⚕️', 'color': (150, 20, 20), 'size': 68},
        'affirmations': ['Я здоров', 'Больница — место помощи', 'Моё тело в порядке'],
        'enemy_count': 14,
    },
    {
        'id': 'city',
        'name': 'Агорафобии',
        'subtitle': 'Городские джунгли',
        'bg_color': (20, 20, 25),
        'accent': (180, 150, 50),
        'star_color': (255, 220, 150),
        'bg_pattern': 'city',
        'enemies_needed': 65,
        'enemies': [
            {'name': 'Толпа', 'emoji': '👥', 'color': (120, 120, 130), 'size': 36, 'hp': 1},
            {'name': 'Метро', 'emoji': '🚇', 'color': (200, 100, 30), 'size': 34, 'hp': 1},
            {'name': 'Сигнал', 'emoji': '📢', 'color': (220, 50, 50), 'size': 30, 'hp': 1},
        ],
        'boss': {'name': 'Городской Гул', 'emoji': '🏙️', 'color': (80, 60, 30), 'size': 72},
        'affirmations': ['Я часть города', 'Улицы безопасны', 'Я контролирую ситуацию'],
        'enemy_count': 16,
    },
    {
        'id': 'abstract',
        'name': 'Тревожность',
        'subtitle': 'Тёмные мысли',
        'bg_color': (10, 5, 15),
        'accent': (150, 50, 200),
        'star_color': (200, 150, 255),
        'bg_pattern': 'abstract',
        'enemies_needed': 70,
        'enemies': [
            {'name': 'Тень', 'emoji': '🌑', 'color': (40, 10, 50), 'size': 36, 'hp': 2},
            {'name': 'Сомнение', 'emoji': '❓', 'color': (120, 40, 140), 'size': 32, 'hp': 1},
            {'name': 'Паника', 'emoji': '💢', 'color': (200, 50, 80), 'size': 30, 'hp': 1},
        ],
        'boss': {'name': 'Голос Тревоги', 'emoji': '👁️', 'color': (100, 0, 120), 'size': 66},
        'affirmations': ['Я спокоен', 'Мысли не опасны', 'Я сильнее страха'],
        'enemy_count': 18,
    },
    {
        'id': 'void',
        'name': 'Экзистенциальный',
        'subtitle': 'Пустота и одиночество',
        'bg_color': (5, 5, 8),
        'accent': (100, 100, 120),
        'star_color': (200, 200, 210),
        'bg_pattern': 'void',
        'enemies_needed': 75,
        'enemies': [
            {'name': 'Тишина', 'emoji': '🤐', 'color': (60, 60, 70), 'size': 34, 'hp': 2},
            {'name': 'Пустота', 'emoji': '🕳️', 'color': (10, 10, 15), 'size': 38, 'hp': 1},
            {'name': 'Призрак', 'emoji': '👻', 'color': (130, 130, 150), 'size': 36, 'hp': 2},
        ],
        'boss': {'name': 'Бездна', 'emoji': '🌌', 'color': (30, 30, 50), 'size': 74},
        'affirmations': ['Я не один', 'Бытие прекрасно', 'Пустота — это тишина'],
        'enemy_count': 20,
    },
    {
        'id': 'tech',
        'name': 'Технофобии',
        'subtitle': 'Машины и ИИ',
        'bg_color': (8, 12, 18),
        'accent': (0, 230, 118),
        'star_color': (0, 255, 150),
        'bg_pattern': 'tech',
        'enemies_needed': 80,
        'enemies': [
            {'name': 'Робот', 'emoji': '🤖', 'color': (0, 180, 80), 'size': 36, 'hp': 2},
            {'name': 'Дрон', 'emoji': '🚁', 'color': (200, 200, 50), 'size': 30, 'hp': 1},
            {'name': 'Вирус', 'emoji': '🦠', 'color': (0, 230, 0), 'size': 28, 'hp': 2},
        ],
        'boss': {'name': 'Главный Процессор', 'emoji': '🧠', 'color': (0, 150, 60), 'size': 70},
        'affirmations': ['Технологии — это инструмент', 'Я управляю машинами', 'Прогресс — это хорошо'],
        'enemy_count': 22,
    },
    {
        'id': 'cosmic',
        'name': 'Космофобии',
        'subtitle': 'Космос и неизвестность',
        'bg_color': (5, 5, 20),
        'accent': (80, 50, 200),
        'star_color': (180, 180, 255),
        'bg_pattern': 'cosmic',
        'enemies_needed': 85,
        'enemies': [
            {'name': 'Астероид', 'emoji': '☄️', 'color': (180, 120, 50), 'size': 34, 'hp': 2},
            {'name': 'Инопланетянин', 'emoji': '👽', 'color': (50, 200, 50), 'size': 36, 'hp': 2},
            {'name': 'Черная дыра', 'emoji': '🕳️', 'color': (80, 20, 100), 'size': 38, 'hp': 2},
        ],
        'boss': {'name': 'Космический Ужас', 'emoji': '🛸', 'color': (40, 20, 100), 'size': 72},
        'affirmations': ['Вселенная прекрасна', 'Я часть космоса', 'Неизвестность манит'],
        'enemy_count': 24,
    },
    {
        'id': 'myth',
        'name': 'Мифофобии',
        'subtitle': 'Древние страхи',
        'bg_color': (15, 8, 12),
        'accent': (200, 100, 20),
        'star_color': (255, 180, 100),
        'bg_pattern': 'myth',
        'enemies_needed': 90,
        'enemies': [
            {'name': 'Гарпия', 'emoji': '🦅', 'color': (150, 50, 20), 'size': 36, 'hp': 2},
            {'name': 'Цербер', 'emoji': '🐺', 'color': (80, 20, 20), 'size': 40, 'hp': 3},
            {'name': 'Василиск', 'emoji': '🐉', 'color': (30, 120, 30), 'size': 38, 'hp': 2},
        ],
        'boss': {'name': 'Титан Страха', 'emoji': '🗿', 'color': (100, 50, 10), 'size': 76},
        'affirmations': ['Мифы — это сказки', 'Я сильнее древних', 'Легенды оживают в играх'],
        'enemy_count': 26,
    },
    {
        'id': 'xeno',
        'name': 'Ксенофобии',
        'subtitle': 'Чужое и неизвестное',
        'bg_color': (10, 5, 18),
        'accent': (255, 50, 80),
        'star_color': (255, 100, 150),
        'bg_pattern': 'xeno',
        'enemies_needed': 100,
        'enemies': [
            {'name': 'Мутант', 'emoji': '👾', 'color': (200, 30, 100), 'size': 36, 'hp': 3},
            {'name': 'Слизень', 'emoji': '🟣', 'color': (150, 20, 120), 'size': 34, 'hp': 2},
            {'name': 'Химера', 'emoji': '🐲', 'color': (255, 50, 20), 'size': 40, 'hp': 3},
        ],
        'boss': {'name': 'Финальный Страх', 'emoji': '💀', 'color': (180, 0, 50), 'size': 80},
        'affirmations': ['Новое — это опыт', 'Я принимаю неизвестное', 'Страх — это вызов'],
        'enemy_count': 28,
    },
]

# ============================================================
# ДОСТИЖЕНИЯ
# ============================================================
ACHIEVEMENTS = [
    {'id': 'first_kill', 'name': 'Первый страх', 'desc': 'Убей 1 врага', 'icon': '🎯', 'need': 1},
    {'id': '10_kills', 'name': 'Охотник', 'desc': 'Убей 10 врагов', 'icon': '🔪', 'need': 10},
    {'id': '50_kills', 'name': 'Истребитель', 'desc': 'Убей 50 врагов', 'icon': '⚔️', 'need': 50},
    {'id': '100_kills', 'name': 'Легенда', 'desc': 'Убей 100 врагов', 'icon': '🏆', 'need': 100},
    {'id': '200_kills', 'name': 'Психо-воин', 'desc': 'Убей 200 врагов', 'icon': '⚔️', 'need': 200},
    {'id': 'level_3', 'name': 'Путешественник', 'desc': 'Достигни 3 уровня', 'icon': '🗺️', 'need': 3},
    {'id': 'level_6', 'name': 'Мастер', 'desc': 'Достигни 6 уровня', 'icon': '👑', 'need': 6},
    {'id': 'level_10', 'name': 'Повелитель', 'desc': 'Пройди все 10 уровней', 'icon': '👾', 'need': 10},
    {'id': 'boss_1', 'name': 'Убийца боссов', 'desc': 'Убей 1 босса', 'icon': '👹', 'need': 1},
    {'id': 'boss_all', 'name': 'Завоеватель', 'desc': 'Убей всех 10 боссов', 'icon': '💀', 'need': 10},
    {'id': 'combo_10', 'name': 'Комбо-мастер', 'desc': 'Сделай комбо из 10', 'icon': '🔥', 'need': 10},
    {'id': 'combo_20', 'name': 'Легендарное комбо', 'desc': 'Сделай комбо из 20', 'icon': '⚡', 'need': 20},
    {'id': 'shield_user', 'name': 'Защитник', 'desc': 'Используй щит', 'icon': '🛡️', 'need': 1},
    {'id': 'laser_user', 'name': 'Лазерный луч', 'desc': 'Используй лазер', 'icon': '🔴', 'need': 1},
    {'id': 'no_damage', 'name': 'Неуязвимый', 'desc': 'Пройти уровень без потери HP', 'icon': '💎', 'need': 1},
    {'id': 'fast_boss', 'name': 'Спринтер', 'desc': 'Убить босса за 30 секунд', 'icon': '🏃', 'need': 1},
    {'id': 'collector', 'name': 'Коллекционер', 'desc': 'Собрать все типы бонусов', 'icon': '🧩', 'need': 1},
]


# ============================================================
# КЛАССЫ ОБЪЕКТОВ
# ============================================================

@dataclass
class Player:
    x: float = SCREEN_WIDTH / 2
    y: float = UI_HEIGHT + 50  # <-- ИГРОК ВНИЗУ!
    radius: float = PLAYER_RADIUS
    speed: float = 4.0
    change_x: float = 0
    skin: str = '🧠'
    skin_name: str = 'Мозг'
    invincible: bool = False
    invincible_timer: int = 0
    super_charge: float = 0
    super_ready: bool = False

    def update(self):
        self.x += self.change_x
        self.x = max(self.radius, min(SCREEN_WIDTH - self.radius, self.x))
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False
        if self.super_charge < 100:
            self.super_charge += 0.5
        else:
            self.super_ready = True

    def collides_with(self, other) -> bool:
        if self.invincible:
            return False
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy) < self.radius + other.radius


class Bullet:
    def __init__(self, x, y, speed=8, damage=1, radius=5, color=(79, 195, 247), is_laser=False, is_super=False):
        self.x = x
        self.y = y
        self.speed = speed
        self.damage = damage
        self.radius = radius
        self.color = color
        self.is_laser = is_laser
        self.is_super = is_super
        self.trail = []

    def collides_with(self, other) -> bool:
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy) < self.radius + other.radius

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 10:
            self.trail.pop(0)
        self.y += self.speed  # <-- ПУЛИ ЛЕТЯТ ВВЕРХ!


class Enemy:
    def __init__(self, x, y, radius=16, speed=1.0, hp=1, max_hp=1,
                 emoji='👾', color=(255, 0, 0), name='Враг', damage=1,
                 move_type=0, special_type=None, special_timer=0, special_visible=True):
        self.x = x
        self.y = y
        self.radius = radius
        self.speed = speed
        self.hp = hp
        self.max_hp = max_hp
        self.emoji = emoji
        self.color = color
        self.name = name
        self.damage = damage
        self.move_type = move_type
        self.special_type = special_type
        self.special_timer = special_timer
        self.special_visible = special_visible
        self.hit_timer = 0
        self.is_boss_projectile = False
        self.trail = []
        self.base_x = x
        self.wobble = random.random() * math.pi * 2

    def update(self):
        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

        if self.hit_timer > 0:
            self.hit_timer -= 1

        if getattr(self, '_custom_update', False):
            self.x += getattr(self, 'vx', 0)
            self.y += getattr(self, 'vy', 0)
            return

        if self.move_type == 0:
            self.y -= self.speed  # Вниз к игроку
        elif self.move_type == 1:
            self.wobble += 0.05
            self.x += math.sin(self.wobble) * 1.5
            self.y -= self.speed  # Вниз к игроку
        elif self.move_type == 2:
            self.wobble += 0.08
            self.x += math.sin(self.wobble) * 3
            self.y -= self.speed * 0.8  # Вниз к игроку

        if self.special_type == 'teleport' and random.random() < 0.01:
            self.x = random.random() * (SCREEN_WIDTH - 80) + 40
            self.y = max(self.y, GAME_TOP * 0.3)


class Boss:
    def __init__(self, x, y, radius=32, hp=50, max_hp=50, emoji='👹', color=(255, 0, 0),
                 name='Босс', speed=0.7, level=1):
        self.x = x
        self.y = y
        self.radius = radius
        self.hp = hp
        self.max_hp = max_hp
        self.emoji = emoji
        self.color = color
        self.name = name
        self.speed = speed
        self.level = level
        self.scale = 1.0
        self.hit_timer = 0
        self.attack_timer = max(30, 60 - level * 3)
        self.attack_phase = 0

        # Плавное плавающее движение (фигура Лиссажу)
        self.float_time = random.random() * math.pi * 2
        self.center_x = x
        self.center_y = GAME_TOP * 0.4
        self.float_radius_x = SCREEN_WIDTH * 0.3
        self.float_radius_y = GAME_TOP * 0.2
        self.float_speed_x = 0.008 + random.random() * 0.003
        self.float_speed_y = 0.012 + random.random() * 0.003
        self.entered = False

    def update(self):
        if self.hit_timer > 0:
            self.hit_timer -= 1

        if not self.entered:
            self.y -= 1.5
            if self.y <= GAME_TOP * 0.5:
                self.entered = True
                self.center_y = self.y
            return

        # Плавное синусоидальное плавающее движение
        self.float_time += 1
        self.x = self.center_x + math.sin(self.float_time * self.float_speed_x) * self.float_radius_x
        self.y = self.center_y + math.sin(self.float_time * self.float_speed_y) * self.float_radius_y

        # Масштаб пульсирует синхронно с движением
        self.scale = 1.0 + 0.05 * math.sin(self.float_time * 0.03)

        if self.attack_timer > 0:
            self.attack_timer -= 1

    def check_hit(self, bullet) -> bool:
        dx = self.x - bullet.x
        dy = self.y - bullet.y
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < self.radius * self.scale * 1.4 + bullet.radius:
            self.hp -= bullet.damage
            self.hit_timer = 10
            return True
        return False

    def attack(self):
        """Выпускает врагов в разные стороны. Количество растёт с уровнем."""
        self.attack_phase += 1
        enemies = []

        # Количество врагов: 3 + уровень босса + фаза атаки
        count = min(4 + self.level // 2 + self.attack_phase // 2, 12)

        # Список эмодзи для врагов
        emoji_list = ['👾', '👻', '💀', '👹', '🤖', '🦠', '☄️', '🕳️']

        for i in range(count):
            # Случайный угол во всех направлениях
            angle = random.random() * math.pi * 2
            # Скорость варьируется
            spd = random.uniform(1.0, 3.0) + self.level * 0.15

            # Тип движения (хаотический)
            move_type = random.randint(0, 2)

            # Размер врага
            sz = random.randint(6, 14)

            enemy = Enemy(
                self.x, self.y,
                radius=sz,
                speed=spd,
                hp=max(1, self.level // 3),
                max_hp=max(1, self.level // 3),
                emoji=random.choice(emoji_list),
                color=self.color,
                name='Порождение',
                damage=1,
                move_type=move_type,
            )
            # Кастомное движение в разные стороны
            enemy._custom_update = True
            enemy.vx = math.cos(angle) * spd
            enemy.vy = math.sin(angle) * spd
            enemy.is_boss_projectile = True
            enemies.append(enemy)

        return enemies


class Powerup:
    SYMBOLS = {
        'shield': ('🛡️', 'Щит', (79, 195, 247)),
        'power': ('⚡', 'Мощь', (255, 215, 64)),
        'laser': ('🔴', 'Лазер', (255, 23, 68)),
        'helper': ('🤖', 'Помощник', (105, 240, 174)),
        'life': ('❤️', 'Жизнь', (255, 82, 82)),
        'bomb': ('💥', 'Бомба', (255, 165, 0)),
        'barrier': ('🛡️', 'Барьер', (0, 200, 255)),
    }

    def __init__(self, x, y, powerup_type):
        self.x = x
        self.y = y
        self.type = powerup_type
        self.radius = 14
        self.wobble = 0
        symbol_data = self.SYMBOLS.get(powerup_type, ('❓', 'Неизвестно', (200, 200, 200)))
        self.symbol = symbol_data[0]
        self.name = symbol_data[1]
        self.color = symbol_data[2]

    def update(self):
        self.y -= 1.5
        self.wobble += 0.04

    def collides_with(self, player) -> bool:
        dx = self.x - player.x
        dy = self.y - player.y
        return math.sqrt(dx * dx + dy * dy) < self.radius + player.radius


class Particle:
    def __init__(self, x, y, vx, vy, color, life, size):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.life = life
        self.max_life = life
        self.size = size

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy -= 0.15
        self.life -= 1

    @property
    def alive(self):
        return self.life > 0

    @property
    def alpha(self):
        return max(0, int((self.life / self.max_life) * 255))


class ParticlePool:
    def __init__(self, max_particles=150):
        self.particles = []
        self.max_particles = max_particles

    def add(self, x, y, vx, vy, color, life, size):
        if len(self.particles) >= self.max_particles:
            self.particles.pop(0)
        self.particles.append(Particle(x, y, vx, vy, color, life, size))

    def update(self):
        for p in self.particles[:]:
            p.update()
            if not p.alive:
                self.particles.remove(p)

    def clear(self):
        self.particles = []

    def draw(self):
        for p in self.particles:
            alpha = p.alpha
            if alpha > 0:
                arcade.draw_circle_filled(
                    p.x, p.y,
                    p.size,
                    (p.color[0], p.color[1], p.color[2], alpha)
                )


# ============================================================
# ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ
# ============================================================
def draw_rect_filled(center_x, center_y, width, height, color):
    left = center_x - width / 2
    bottom = center_y - height / 2
    arcade.draw_lbwh_rectangle_filled(left, bottom, width, height, color)


# ============================================================
# ГЛАВНЫЙ КЛАСС ИГРЫ
# ============================================================
class PsychoBattle(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.total_frame = 0
        self.fps_display = arcade.Text("", 5, SCREEN_HEIGHT - 15, color=arcade.color.WHITE, font_size=12)
        self.difficulty_name = 'normal'
        self.difficulty_data = DIFFICULTY[self.difficulty_name]
        self.mouse_x = SCREEN_WIDTH / 2
        self.mouse_y = SCREEN_HEIGHT / 2
        self._last_click_time = 0.0
        self.current_skin = '🧠'
        self.stats = self.load_stats()
        self.setup()
        self.boss_spawn_time = 0
        self.no_damage_run = True
        self.collected_powerups = set()
        self.bomb_cooldown = 0
        self.barrier_active = False
        self.barrier_timer = 0
        self.super_bullet_active = False
        self.super_bullet_charging = False
        self.super_bullet_timer = 0

        # Мобильное управление
        self.touch_fire_id: Optional[int] = None
        self.touch_move_id: Optional[int] = None
        self.touch_bomb_id: Optional[int] = None
        self.touch_barrier_id: Optional[int] = None
        self.touch_buttons_visible = False

        # Звуки
        self.sfx: Dict[str, arcade.Sound] = {}
        self.sfx_players: List[Any] = []  # храним ссылки на проигрыватели, чтобы GC не убил
        self._load_sounds()
        self.current_music: Optional[arcade.Sound] = None
        self.current_music_player = None

    def load_stats(self):
        try:
            with open('psycho_stats.json', 'r') as f:
                return json.load(f)
        except:
            return {
                'total_kills': 0,
                'total_bosses': 0,
                'max_level': 1,
                'max_level_reached': 1,
                'max_combo': 0,
                'high_score': 0,
                'shield_used': 0,
                'laser_used': 0,
                'play_time': 0,
                'last_played': '',
                'games_played': 0,
                'achievements': {},
            }

    def save_stats(self):
        self.stats['achievements'] = {k: v for k, v in self.achievements.items()}
        self.stats['total_kills'] = self.total_kills
        self.stats['total_bosses'] = self.bosses_killed_total
        self.stats['max_level'] = self.max_level_reached
        self.stats['max_level_reached'] = self.max_level_reached
        self.stats['max_combo'] = self.max_combo
        self.stats['high_score'] = max(self.stats.get('high_score', 0), self.score)
        self.stats['shield_used'] = self.shield_used
        self.stats['laser_used'] = self.laser_used
        self.stats['play_time'] = self.play_time
        self.stats['last_played'] = datetime.datetime.now().strftime('%d.%m.%Y %H:%M')
        self.stats['games_played'] = self.stats.get('games_played', 0) + 1
        try:
            with open('psycho_stats.json', 'w') as f:
                json.dump(self.stats, f)
        except:
            pass

    def _load_sounds(self):
        """Загрузка звуковых эффектов из sounds.py."""
        sfx_names = ['shoot', 'laser', 'hit', 'explosion', 'powerup', 'boss_warning', 'victory']
        for name in sfx_names:
            path = sounds.get_path(name)
            if path and os.path.exists(path):
                self.sfx[name] = arcade.Sound(path)
        self.music_tracks = {}
        for i in range(1, 11):
            name = f'level{i}'
            path = sounds.get_path(name)
            if path and os.path.exists(path):
                self.music_tracks[i] = arcade.Sound(path)

    def _play_sfx(self, name: str, volume: float = 1.0):
        """Play a sound effect by name."""
        snd = self.sfx.get(name)
        if snd:
            try:
                player = snd.play(volume)
                self.sfx_players.append(player)
                if len(self.sfx_players) > 128:
                    self.sfx_players = self.sfx_players[-64:]
            except Exception as e:
                print(f"[SOUND] {name}: {e}")

    def _start_music(self, level_num: int):
        """Start looping background music for a level."""
        self._stop_music()
        track = self.music_tracks.get(level_num)
        if track:
            self.current_music_player = track.play(0.5, loop=True)
            self.current_music = track

    def _stop_music(self):
        """Stop current background music."""
        if self.current_music_player is not None:
            try:
                self.current_music_player.pause()
                self.current_music_player.delete()
            except Exception:
                pass
            self.current_music_player = None
            self.current_music = None

    def setup(self):
        self.game_started = False
        self.game_over = False
        self.victory = False
        self.show_main_menu = True
        self.show_stats = False
        self.show_controls = False
        self.paused = False

        self.player = Player()
        self.player.skin = self.current_skin
        self.keys = {'left': False, 'right': False, 'space': False, 'bomb': False, 'barrier': False}
        self.is_pointer_down = False
        self.pointer_down_time = 0
        self.mouse_x = SCREEN_WIDTH / 2
        self.mouse_y = SCREEN_HEIGHT / 2
        self._last_click_time = 0.0

        self.enemies: List[Enemy] = []
        self.bullets: List[Bullet] = []
        self.powerups: List[Powerup] = []
        self.helpers: List[Dict] = []
        self.particle_pool = ParticlePool(max_particles=MAX_PARTICLES)
        self.stars: List[Dict] = []
        self.bombs: List[Dict] = []

        self.lives = 3
        self.score = 0
        self.level = 1
        self.combo = 0
        self.max_combo = 0
        self.total_kills = 0
        self.bosses_killed = 0
        self.max_level_reached = 1
        self.shield_used = 0
        self.laser_used = 0
        self.play_time = 0
        self.bosses_killed_total = 0
        self.no_damage_run = True
        self.collected_powerups = set()
        self.boss_spawn_time = 0
        self.boss_defeated_time = 0
        self.enemies_killed_in_level = 0

        self.shoot_cooldown = 0
        self.laser_cooldown = 0
        self.enemy_spawn_timer = 30
        self.enemies_spawned = 0
        self.enemies_per_level = ENEMIES_PER_LEVEL
        self.max_enemies = 4
        self.enemy_speed = ENEMY_BASE_SPEED
        self.difficulty_modifier = 0.0
        self.bomb_cooldown = 0
        self.barrier_active = False
        self.barrier_timer = 0
        self.super_bullet_active = False
        self.super_bullet_charging = False
        self.super_bullet_timer = 0

        self.boss: Optional[Boss] = None
        self.boss_active = False
        self.boss_spawned = False
        self.boss_warning_timer = 0
        self.boss_warning_name = ""

        self.powerups_active = {
            'shield': False,
            'power': False,
            'laser': False,
            'helper': False,
            'bomb': False,
            'barrier': False,
        }
        self.powerups_timers = {
            'shield': 0,
            'power': 0,
            'laser': 0,
            'helper': 0,
            'bomb': 0,
            'barrier': 0,
        }

        self.screen_shake = 0
        self.flash_effect = 0
        self.hit_flash = 0

        self.affirmation_text = ""
        self.affirmation_sub = ""
        self.affirmation_timer = 0
        self.level_complete_timer = 0

        self.achievements = {a['id']: False for a in ACHIEVEMENTS}
        saved_achievements = self.stats.get('achievements', {})
        for ach_id in self.achievements:
            if saved_achievements.get(ach_id, False):
                self.achievements[ach_id] = True

        self.transition_timer = 0
        self.transition_callback = None

        self.current_level_data = self.get_current_level_data()
        self.init_stars()
        self.apply_difficulty()

    def apply_difficulty(self):
        diff = DIFFICULTY.get(self.difficulty_name, DIFFICULTY['normal'])
        self.enemy_speed = ENEMY_BASE_SPEED * diff['speed']
        self.enemies_per_level = int(diff['enemy_count'])

    def init_stars(self):
        self.stars = []
        theme = self.current_level_data
        star_color = theme.get('star_color', (200, 200, 200))
        for _ in range(80):
            self.stars.append({
                'x': random.random() * SCREEN_WIDTH,
                'y': random.random() * SCREEN_HEIGHT,
                'size': random.uniform(0.5, 3.0),
                'speed': random.uniform(0.05, 0.35),
                'brightness': random.uniform(0.3, 1.0),
                'color': star_color,
                'twinkle_speed': random.uniform(0.01, 0.04),
                'twinkle_offset': random.uniform(0, math.pi * 2),
                'pulse': random.uniform(0.5, 1.5),
            })

    def get_current_level_data(self):
        idx = (self.level - 1) % len(LEVELS)
        return LEVELS[idx]

    def get_enemies_needed_for_boss(self):
        level_data = self.get_current_level_data()
        return level_data.get('enemies_needed', 50 + self.level * 10)

    def reset_powerups(self):
        for key in self.powerups_active:
            self.powerups_active[key] = False
            self.powerups_timers[key] = 0
        self.helpers = []

    # ============================================================
    # МЕТОДЫ ОБНОВЛЕНИЯ
    # ============================================================

    def on_update(self, delta_time):
        self.total_frame += 1
        self.play_time += delta_time

        if self.show_main_menu or self.show_stats or self.game_over or self.paused:
            return

        if self.show_controls:
            return

        if self.transition_timer > 0:
            self.transition_timer -= 1
            if self.transition_timer <= 0 and self.transition_callback:
                self.transition_callback()
                self.transition_callback = None
            return

        self.update_timers()

        self.player.change_x = 0
        if self.keys['left']:
            self.player.change_x = -self.player.speed
        if self.keys['right']:
            self.player.change_x = self.player.speed
        self.player.update()

        is_shooting = self.keys['space'] or self.is_pointer_down or self.touch_fire_id is not None
        if is_shooting:
            if self.player.super_ready and not self.super_bullet_active and self.keys['space']:
                self.super_bullet_charging = True
                self.super_bullet_timer += 1
                if self.super_bullet_timer > 30:
                    self.fire_super_bullet()
            else:
                self.shoot()

        if self.keys['bomb'] and self.bomb_cooldown <= 0:
            self.activate_bomb()
            self.keys['bomb'] = False

        if self.keys['barrier'] and not self.barrier_active:
            self.activate_barrier()
            self.keys['barrier'] = False

        self.update_enemies()
        self.update_bullets()
        self.update_powerups()
        self.update_particles()
        self.update_helpers()
        self.update_stars()
        self.update_boss()
        self.update_spawning()
        self.update_bombs()

        self.check_collisions()

        self.update_effects()
        self.update_affirmation()
        if self.boss_warning_timer > 0:
            self.boss_warning_timer -= 1
        if self.level_complete_timer > 0:
            self.level_complete_timer -= 1

        fps = int(1 / delta_time) if delta_time > 0 else 60
        self.fps_display.text = f"FPS: {fps}"

    def update_timers(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        if self.laser_cooldown > 0:
            self.laser_cooldown -= 1
        if self.bomb_cooldown > 0:
            self.bomb_cooldown -= 1

        if self.barrier_active:
            self.barrier_timer -= 1
            if self.barrier_timer <= 0:
                self.barrier_active = False
                self.player.invincible = False

        for key in self.powerups_active:
            if self.powerups_active[key]:
                self.powerups_timers[key] -= 1
                if self.powerups_timers[key] <= 0:
                    self.powerups_active[key] = False
                    if key == 'helper':
                        self.helpers = []

    def update_enemies(self):
        for enemy in self.enemies[:]:
            enemy.update()
            # Враги удаляются если вышли за границы экрана
            if (enemy.y < -50 or enemy.y > SCREEN_HEIGHT + 50 or
                    enemy.x < -50 or enemy.x > SCREEN_WIDTH + 50):
                if enemy in self.enemies:
                    self.enemies.remove(enemy)

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y > SCREEN_HEIGHT + 30 or bullet.x < -30 or bullet.x > SCREEN_WIDTH + 30:
                self.bullets.remove(bullet)

    def update_powerups(self):
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.y < -20:
                self.powerups.remove(powerup)

    def update_particles(self):
        self.particle_pool.update()

    def update_helpers(self):
        if self.powerups_active['helper']:
            while len(self.helpers) < 2:
                side = -1 if len(self.helpers) == 0 else 1
                self.helpers.append({
                    'x': self.player.x + side * 40,
                    'y': self.player.y + 20,
                    'side': side,
                    'shoot_timer': random.randint(20, 40),
                })

            for helper in self.helpers:
                helper['x'] += (self.player.x + helper['side'] * 40 - helper['x']) * 0.08
                helper['y'] += (self.player.y + 20 - helper['y']) * 0.08

                helper['shoot_timer'] -= 1
                if helper['shoot_timer'] <= 0:
                    self.bullets.append(Bullet(
                        helper['x'], helper['y'] - 14,
                        speed=7, damage=1, radius=4,
                        color=(105, 240, 174), is_laser=False
                    ))
                    helper['shoot_timer'] = random.randint(20, 40)
        else:
            self.helpers = []

    def update_stars(self):
        for star in self.stars:
            star['y'] += star['speed']
            if star['y'] > SCREEN_HEIGHT:
                star['y'] = 0
                star['x'] = random.random() * SCREEN_WIDTH

    def update_bombs(self):
        for bomb in self.bombs[:]:
            bomb['y'] += 2
            bomb['radius'] += 1
            bomb['life'] -= 1
            if bomb['life'] <= 0:
                self.bombs.remove(bomb)

    def update_boss(self):
        if not self.boss_active or not self.boss:
            return

        self.boss.update()

        if self.boss.attack_timer <= 0:
            enemies = self.boss.attack()
            self.enemies.extend(enemies)
            self.boss.attack_timer = max(25, 60 - self.level * 3 - self.boss.attack_phase * 4)
            self.screen_shake = max(self.screen_shake, 3)

    def update_spawning(self):
        if self.boss_active or self.boss_spawned or self.level_complete_timer > 0:
            return

        spawn_rate = max(10, 40 - self.level * 2 - int(self.difficulty_modifier * 2))

        self.enemy_spawn_timer -= 1
        if self.enemy_spawn_timer <= 0:
            if len(self.enemies) < self.max_enemies + self.level // 2:
                self.spawn_enemy()
            self.enemy_spawn_timer = spawn_rate + random.randint(0, 20)
            self.enemies_spawned += 1

        enemies_needed = self.get_enemies_needed_for_boss()
        if self.enemies_killed_in_level >= enemies_needed and not self.boss_spawned:
            self.spawn_boss()
            self.boss_spawned = True
            self.boss_spawn_time = self.total_frame

    def update_effects(self):
        if self.screen_shake > 0:
            self.screen_shake *= 0.92
            if self.screen_shake < 0.1:
                self.screen_shake = 0

        if self.flash_effect > 0:
            self.flash_effect -= 1

        if self.hit_flash > 0:
            self.hit_flash -= 1

    def update_affirmation(self):
        if self.affirmation_timer > 0:
            self.affirmation_timer -= 1

    # ============================================================
    # СПЕЦИАЛЬНЫЕ АТАКИ
    # ============================================================

    def activate_bomb(self, force=False):
        if self.bomb_cooldown > 0:
            return

        if not force and not self.powerups_active.get('bomb', False):
            return

        for enemy in self.enemies[:]:
            self.spawn_particles(enemy.x, enemy.y, (255, 215, 0), 20)
            self.score += 5
            self.combo += 1
            self.total_kills += 1
            self.enemies.remove(enemy)

        self.bomb_cooldown = 300
        self.screen_shake = 20
        self.flash_effect = 30
        self.show_affirmation("💥 БОМБА!", "Все страхи уничтожены!")
        self._play_sfx('explosion')

        self.bombs.append({
            'x': SCREEN_WIDTH / 2,
            'y': SCREEN_HEIGHT / 2,
            'radius': 10,
            'life': 30,
        })

        self.powerups_active['bomb'] = False

    def activate_barrier(self):
        if self.barrier_active:
            return

        if not self.powerups_active.get('barrier', False):
            return

        self.barrier_active = True
        self.barrier_timer = 180
        self.player.invincible = True
        self.show_affirmation("🛡️ БАРЬЕР!", "Неуязвимость на 3 секунды")
        self.powerups_active['barrier'] = False

    def fire_super_bullet(self):
        if not self.player.super_ready:
            return

        self.super_bullet_active = True
        self.super_bullet_timer = 0
        self.player.super_ready = False
        self.player.super_charge = 0

        self.bullets.append(Bullet(
            self.player.x, self.player.y - PLAYER_RADIUS - 4,
            speed=BULLET_SPEED * 0.8,
            damage=5,
            radius=15,
            color=(255, 215, 0),
            is_laser=False,
            is_super=True,
        ))

        self.screen_shake = max(self.screen_shake, 5)
        self.show_affirmation("⚡ СУПЕР-ВЫСТРЕЛ!", "Мощь x5!")
        self.super_bullet_active = False

    # ============================================================
    # МЕТОДЫ ДЕЙСТВИЙ
    # ============================================================

    def shoot(self):
        if self.shoot_cooldown > 0:
            return

        if self.powerups_active['laser']:
            if self.laser_cooldown <= 0:
                self.bullets.append(Bullet(
                    self.player.x, self.player.y - PLAYER_RADIUS - 4,
                    speed=LASER_SPEED, damage=3, radius=8,
                    color=(255, 23, 68), is_laser=True
                ))
                self.laser_cooldown = 4
                self.screen_shake = max(self.screen_shake, 2)
                self.laser_used += 1
                self.check_achievements()
                self._play_sfx('laser')
            return

        count = 3 if self.powerups_active['power'] else 1
        damage = 2 if self.powerups_active['power'] else 1

        if self.combo >= 5 and self.combo < 10:
            damage += 1
        elif self.combo >= 15:
            damage += 2

        for i in range(count):
            offset = 0 if count == 1 else (i - (count - 1) / 2) * 12
            color = (255, 215, 64) if self.powerups_active['power'] else (79, 195, 247)
            self.bullets.append(Bullet(
                self.player.x + offset,
                self.player.y - PLAYER_RADIUS - 4,
                speed=BULLET_SPEED,
                damage=damage,
                radius=5,
                color=color,
                is_laser=False
            ))

        self.shoot_cooldown = 10 if self.powerups_active['power'] else 14
        self._play_sfx('shoot')

    def spawn_enemy(self):
        theme = self.current_level_data
        enemy_data = random.choice(theme['enemies'])
        diff = DIFFICULTY.get(self.difficulty_name, DIFFICULTY['normal'])

        size = enemy_data['size'] + (self.level - 1) * 1.5
        x = random.random() * (SCREEN_WIDTH - 80) + 40

        # Враги появляются сверху и летят вниз
        y = SCREEN_HEIGHT + size

        hp = max(1, int((enemy_data.get('hp', 1) + self.difficulty_modifier // 2) * diff['hp']))

        special_type = None
        if self.level >= 3 and random.random() < 0.15 + self.level * 0.01:
            special_types = ['bomber', 'diver', 'shield', 'teleport']
            special_type = random.choice(special_types[:min(len(special_types), self.level - 2)])

        enemy = Enemy(
            x, y,  # y за верхней границей экрана
            radius=size / 2,
            speed=(self.enemy_speed + random.random() * 0.3) * diff['speed'],
            hp=hp,
            max_hp=hp,
            emoji=enemy_data['emoji'],
            color=enemy_data['color'],
            name=enemy_data['name'],
            damage=1,
            move_type=random.randint(0, 2),
            special_type=special_type,
            special_timer=0,
            special_visible=True,
        )
        self.enemies.append(enemy)

    def spawn_boss(self):
        boss_data = self.current_level_data['boss']
        diff = DIFFICULTY.get(self.difficulty_name, DIFFICULTY['normal'])

        self.boss = Boss(
            SCREEN_WIDTH / 2, SCREEN_HEIGHT + 60,  # появляется сверху и летит вниз
            radius=boss_data['size'] / 2 * (1 + self.level * 0.03),
            hp=int((30 + self.level ** 2 * 4.0) * diff['boss_hp']),
            max_hp=int((30 + self.level ** 2 * 4.0) * diff['boss_hp']),
            emoji=boss_data['emoji'],
            color=boss_data['color'],
            name=boss_data['name'],
            speed=(0.7 + self.level * 0.04) * diff['boss_speed'],
            level=self.level
        )
        self.boss_active = True
        self.boss_warning_timer = 120
        self.boss_warning_name = boss_data['name']
        self.enemies = []
        self.screen_shake = 10
        self.boss_spawn_time = self.total_frame
        self._play_sfx('boss_warning')

        for _ in range(15):
            angle = random.random() * math.pi * 2
            speed = random.random() * 4 + 1
            self.particle_pool.add(
                SCREEN_WIDTH / 2, SCREEN_HEIGHT + 60,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                boss_data['color'],
                random.randint(10, 20),
                random.uniform(1, 3)
            )

        self.show_affirmation(f"👹 БОСС: {boss_data['name']}", "Приготовься к битве!")

    def apply_powerup(self, powerup_type: str):
        if powerup_type == 'life':
            self.lives = min(3, self.lives + 1)
            self.show_affirmation("❤️ +1 ЖИЗНЬ!", "Ты сильнее, чем думаешь")
            self.collected_powerups.add('life')
            return

        if powerup_type == 'bomb':
            self.powerups_active['bomb'] = True
            self.bomb_cooldown = 0
            self.show_affirmation("💥 БОМБА ГОТОВА!", "Нажми B для активации")
            self.collected_powerups.add('bomb')
            return

        if powerup_type == 'barrier':
            self.powerups_active['barrier'] = True
            self.show_affirmation("🛡️ БАРЬЕР ГОТОВ!", "Нажми E для активации")
            self.collected_powerups.add('barrier')
            return

        self.powerups_active[powerup_type] = True
        self.powerups_timers[powerup_type] = POWERUP_DURATION[powerup_type]
        self.collected_powerups.add(powerup_type)

        if powerup_type == 'shield':
            self.shield_used += 1
            self.show_affirmation("🛡️ ЩИТ АКТИВИРОВАН!", "Защита на 10 секунд")
        elif powerup_type == 'power':
            self.show_affirmation("⚡ ДВОЙНОЙ ВЫСТРЕЛ!", "3 пули вместо 1")
        elif powerup_type == 'laser':
            self.laser_used += 1
            self.show_affirmation("🔴 ЛАЗЕР АКТИВИРОВАН!", "Мощный непрерывный луч")
        elif powerup_type == 'helper':
            self.show_affirmation("🤖 ПОМОЩНИКИ ПРИЗВАНЫ!", "2 робота стреляют за тебя")

        self.check_achievements()
        self._play_sfx('powerup')

    def enemy_killed(self, enemy: Enemy):
        self.score += 10 + self.level * 2
        self.combo += 1
        self.total_kills += 1
        self.enemies_killed_in_level += 1
        self.difficulty_modifier += 0.05

        if self.combo > self.max_combo:
            self.max_combo = self.combo

        if self.combo == 5:
            self.show_affirmation("⚡ КОМБО x5!", "Усиленные пули!")
            self.powerups_active['power'] = True
            self.powerups_timers['power'] = 180
        elif self.combo == 10:
            self.show_affirmation("💥 КОМБО x10!", "Автоматическая бомба!")
            self.activate_bomb(force=True)
        elif self.combo == 15:
            self.show_affirmation("🤖 КОМБО x15!", "Призыв помощников!")
            self.powerups_active['helper'] = True
            self.powerups_timers['helper'] = 300

        self.check_achievements()

        if self.combo > 0 and self.combo % 3 == 0 and self.combo <= 15:
            affirm = random.choice(self.current_level_data['affirmations'])
            self.show_affirmation(affirm, f"✦ {self.current_level_data['name']} ✦")

        if random.random() < 0.04 + self.difficulty_modifier * 0.001:
            types = ['shield', 'power', 'laser', 'helper', 'life', 'bomb', 'barrier']
            weights = [25, 6, 4, 4, 8, 10, 10]
            total = sum(weights)
            rand = random.random() * total
            selected = types[0]
            for i, w in enumerate(weights):
                rand -= w
                if rand <= 0:
                    selected = types[i]
                    break
            self.powerups.append(Powerup(enemy.x, enemy.y, selected))

        self.spawn_particles(enemy.x, enemy.y, enemy.color, 10)

    def boss_defeated(self):
        self.score += 100 + self.level * 20
        self.boss_active = False
        self.bosses_killed += 1
        self.bosses_killed_total += 1
        self.screen_shake = 12
        self.flash_effect = 15
        self.boss_defeated_time = self.total_frame
        self._play_sfx('explosion')

        self.check_achievements()

        for _ in range(30):
            angle = random.random() * math.pi * 2
            speed = random.random() * 8 + 2
            colors = [(255, 23, 68), (255, 215, 0), (79, 195, 247), (255, 111, 0), self.boss.color]
            self.particle_pool.add(
                self.boss.x + random.uniform(-20, 20),
                self.boss.y + random.uniform(-20, 20),
                math.cos(angle) * speed,
                math.sin(angle) * speed - 1,
                random.choice(colors),
                random.randint(20, 50),
                random.uniform(2, 5)
            )

        if self.no_damage_run and self.lives == 3:
            self.unlock_achievement_by_id('no_damage')

        if self.total_frame - self.boss_spawn_time < 1800:
            self.unlock_achievement_by_id('fast_boss')

        if self.level < 10:
            self.level_complete_timer = 180
            self.show_affirmation(
                f"🎉 УРОВЕНЬ {self.level} ПРОЙДЕН!",
                f"{self.current_level_data['name']} — побеждён!"
            )

            self.transition_timer = 200
            self.transition_callback = self._start_next_level
        else:
            self.victory = True
            self.game_over = True
            self.show_affirmation("🏆 Молодец! Ты справился со своими фобиями! 🏆", "Ты — настоящий герой!")
            self.unlock_achievement_by_id('level_10')
            self.save_stats()
            self._play_sfx('victory')
            self._stop_music()

    def _start_next_level(self):
        self.level += 1
        if self.level > self.max_level_reached:
            self.max_level_reached = self.level
        self.enemies_spawned = 0
        self.boss_spawned = False
        self.boss_active = False
        self.boss = None
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.enemies_killed_in_level = 0
        self.current_level_data = self.get_current_level_data()
        self.enemy_spawn_timer = 30
        self.max_enemies = 4 + self.level // 2
        self.enemies_per_level = ENEMIES_PER_LEVEL + self.level * 2
        self.enemy_speed = ENEMY_BASE_SPEED + (self.level - 1) * 0.1
        self.difficulty_modifier = 0.0
        self.lives = min(3, self.lives + 1)
        self.no_damage_run = True
        self.level_complete_timer = 0
        self.init_stars()
        self.show_affirmation(
            f"⬆ УРОВЕНЬ {self.level}!",
            f"{self.current_level_data['name']}: {self.current_level_data['subtitle']}"
        )
        self.check_achievements()
        self.save_stats()
        self._start_music(self.level)

    def lose_life(self):
        self.reset_powerups()
        self.no_damage_run = False

        self.lives -= 1
        self.hit_flash = 20
        self.screen_shake = 12
        self.combo = 0
        self.player.invincible = True
        self.player.invincible_timer = 60
        self._play_sfx('hit')

        if self.lives <= 0:
            self.game_over = True
            self.save_stats()
            self._stop_music()

    # ============================================================
    # МЕТОДЫ ПРОВЕРКИ КОЛЛИЗИЙ
    # ============================================================

    def check_collisions(self):
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                if bullet.collides_with(enemy):
                    enemy.hp -= bullet.damage
                    enemy.hit_timer = 10
                    self.bullets.remove(bullet)
                    self.screen_shake = max(self.screen_shake, 2)
                    self.spawn_particles(enemy.x, enemy.y, enemy.color, 6)
                    self._play_sfx('hit')

                    if enemy.hp <= 0:
                        self.enemy_killed(enemy)
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                    break

        for enemy in self.enemies[:]:
            if self.player.collides_with(enemy):
                if self.powerups_active['shield']:
                    self.powerups_active['shield'] = False
                    self.powerups_timers['shield'] = 0
                    self.spawn_particles(self.player.x, self.player.y, (79, 195, 247), 15)
                    self.enemies.remove(enemy)
                    self.show_affirmation("🛡️ Щит поглотил удар!", "Защита сработала")
                    continue

                if self.barrier_active:
                    self.spawn_particles(self.player.x, self.player.y, (79, 195, 247), 10)
                    self.enemies.remove(enemy)
                    continue

                self.lose_life()
                self.enemies.remove(enemy)
                if self.game_over:
                    return

        if self.boss_active and self.boss:
            for bullet in self.bullets[:]:
                if self.boss.check_hit(bullet):
                    self.bullets.remove(bullet)
                    self.screen_shake = max(self.screen_shake, 4)
                    self.spawn_particles(self.boss.x, self.boss.y, self.boss.color, 10)

                    if self.boss.hp <= 0:
                        self.boss_defeated()
                    break

        for powerup in self.powerups[:]:
            if powerup.collides_with(self.player):
                self.apply_powerup(powerup.type)
                self.spawn_particles(powerup.x, powerup.y, powerup.color, 15)
                self.powerups.remove(powerup)

    # ============================================================
    # МЕТОДЫ ЭФФЕКТОВ
    # ============================================================

    def spawn_particles(self, x, y, color, count):
        count = min(count, 15)
        for _ in range(count):
            angle = random.random() * math.pi * 2
            speed = random.random() * 6 + 2
            self.particle_pool.add(
                x, y,
                math.cos(angle) * speed,
                math.sin(angle) * speed,
                color,
                random.randint(15, 30),
                random.uniform(1, 4)
            )

    def show_affirmation(self, text, sub=""):
        self.affirmation_text = text
        self.affirmation_sub = sub
        self.affirmation_timer = 150

    # ============================================================
    # ДОСТИЖЕНИЯ
    # ============================================================

    def check_achievements(self):
        for ach in ACHIEVEMENTS:
            if self.achievements.get(ach['id'], False):
                continue

            if ach['id'] == 'first_kill' and self.total_kills >= 1:
                self.unlock_achievement(ach)
            elif ach['id'] == '10_kills' and self.total_kills >= 10:
                self.unlock_achievement(ach)
            elif ach['id'] == '50_kills' and self.total_kills >= 50:
                self.unlock_achievement(ach)
            elif ach['id'] == '100_kills' and self.total_kills >= 100:
                self.unlock_achievement(ach)
            elif ach['id'] == '200_kills' and self.total_kills >= 200:
                self.unlock_achievement(ach)
            elif ach['id'] == 'level_3' and self.max_level_reached >= 3:
                self.unlock_achievement(ach)
            elif ach['id'] == 'level_6' and self.max_level_reached >= 6:
                self.unlock_achievement(ach)
            elif ach['id'] == 'level_10' and self.max_level_reached >= 10:
                self.unlock_achievement(ach)
            elif ach['id'] == 'boss_1' and self.bosses_killed_total >= 1:
                self.unlock_achievement(ach)
            elif ach['id'] == 'boss_all' and self.bosses_killed_total >= 10:
                self.unlock_achievement(ach)
            elif ach['id'] == 'combo_10' and self.max_combo >= 10:
                self.unlock_achievement(ach)
            elif ach['id'] == 'combo_20' and self.max_combo >= 20:
                self.unlock_achievement(ach)
            elif ach['id'] == 'shield_user' and self.shield_used >= 1:
                self.unlock_achievement(ach)
            elif ach['id'] == 'laser_user' and self.laser_used >= 1:
                self.unlock_achievement(ach)
            elif ach['id'] == 'collector' and len(self.collected_powerups) >= 7:
                self.unlock_achievement(ach)

    def unlock_achievement_by_id(self, ach_id):
        for ach in ACHIEVEMENTS:
            if ach['id'] == ach_id and not self.achievements.get(ach_id, False):
                self.unlock_achievement(ach)
                break

    def unlock_achievement(self, ach):
        self.achievements[ach['id']] = True
        self.show_affirmation(f"🏆 ДОСТИЖЕНИЕ: {ach['name']}", f"{ach['icon']} {ach['desc']}")
        self.save_stats()

    # ============================================================
    # МЕТОДЫ ОТРИСОВКИ
    # ============================================================

    def on_draw(self):
        self.clear()

        if self.show_main_menu:
            self.draw_main_menu()
            return

        if self.show_stats:
            self.draw_stats()
            return

        if self.game_over:
            self.draw_game_over()
            return

        shake_x, shake_y = 0, 0
        if self.screen_shake > 0.5:
            shake_x = (random.random() - 0.5) * self.screen_shake * 1.5
            shake_y = (random.random() - 0.5) * self.screen_shake * 1.5

        bg_color = self.current_level_data['bg_color']
        draw_rect_filled(SCREEN_WIDTH / 2 + shake_x, SCREEN_HEIGHT / 2 + shake_y, SCREEN_WIDTH, SCREEN_HEIGHT, bg_color)

        self.draw_background_pattern()
        self.draw_stars()
        self.draw_particles()
        self.draw_powerups()
        self.draw_helpers()
        self.draw_enemies()
        self.draw_boss()
        self.draw_bullets()
        self.draw_player()
        self.draw_ui()
        self.draw_combo()
        self.draw_progress()
        self.draw_affirmation()
        self.draw_bombs()

        if self.boss_warning_timer > 0:
            self.draw_boss_warning()

        if self.level_complete_timer > 0:
            self.draw_level_complete()

        if self.flash_effect > 0:
            alpha = self.flash_effect / 40 * 0.6
            draw_rect_filled(
                SCREEN_WIDTH / 2 + shake_x, SCREEN_HEIGHT / 2 + shake_y,
                SCREEN_WIDTH, SCREEN_HEIGHT,
                (255, 255, 255, int(alpha * 255))
            )

        if self.barrier_active:
            pulse = 1 + 0.05 * math.sin(self.total_frame * 0.08)
            arcade.draw_circle_outline(
                self.player.x, self.player.y,
                PLAYER_RADIUS * 3 * pulse,
                (79, 195, 247),
                3
            )
            glow = (79, 195, 247, 40)
            arcade.draw_circle_filled(
                self.player.x, self.player.y,
                PLAYER_RADIUS * 3 * pulse,
                glow
            )

        self.fps_display.draw()

        # Тач кнопки поверх всего (только для мобильных)
        if self.touch_buttons_visible:
            self.draw_touch_buttons()

    def draw_bombs(self):
        for bomb in self.bombs:
            alpha = bomb['life'] / 30
            arcade.draw_circle_filled(
                bomb['x'], bomb['y'],
                bomb['radius'],
                (255, 215, 0, int(alpha * 200))
            )
            arcade.draw_circle_outline(
                bomb['x'], bomb['y'],
                bomb['radius'] * 2,
                (255, 215, 0, int(alpha * 100)),
                2
            )

    def draw_stars(self):
        for star in self.stars:
            twinkle = 0.5 + 0.5 * math.sin(
                self.total_frame * star['twinkle_speed'] + star['twinkle_offset']
            )
            alpha = star['brightness'] * twinkle
            size = star['size'] * (0.5 + 0.5 * twinkle)
            arcade.draw_circle_filled(
                star['x'], star['y'],
                size,
                (star['color'][0], star['color'][1], star['color'][2], int(alpha * 200))
            )

    def draw_background_pattern(self):
        pattern_type = self.current_level_data.get('bg_pattern', 'default')

        if pattern_type == 'forest':
            for i in range(15):
                x = (i / 15) * SCREEN_WIDTH + math.sin(i * 1.5 + self.total_frame * 0.002) * 20
                h = 20 + math.sin(i * 2 + self.total_frame * 0.003) * 15 + 30
                arcade.draw_line(x, SCREEN_HEIGHT - h - 20, x, SCREEN_HEIGHT, (76, 175, 80, 20), 3)
        elif pattern_type == 'ocean':
            for i in range(20):
                x = (i / 20) * SCREEN_WIDTH
                y = SCREEN_HEIGHT - 30 + math.sin(i * 0.5 + self.total_frame * 0.005) * 15
                arcade.draw_arc_filled(x, y, 40, 20, (33, 150, 243, 20), 0, 180)
        elif pattern_type == 'medical':
            for i in range(10):
                x = (i / 10) * SCREEN_WIDTH + math.sin(i + self.total_frame * 0.001) * 30
                y = (i % 4) * 160 + 30 + math.sin(i * 2 + self.total_frame * 0.002) * 20
                arcade.draw_text('⚕️', x, y, (244, 67, 54, 30), font_size=25)
        elif pattern_type == 'city':
            for i in range(18):
                x = (i / 18) * SCREEN_WIDTH
                h = 20 + math.sin(i * 3 + self.total_frame * 0.002) * 20 + 40
                draw_rect_filled(x, SCREEN_HEIGHT - h / 2 - 20, 5, h, (156, 39, 176, 20))
                for w in range(3):
                    draw_rect_filled(x, SCREEN_HEIGHT - h + 5 + w * 15, 2, 4, (255, 215, 0, 15))
        elif pattern_type == 'abstract':
            for i in range(20):
                x = (i / 20) * SCREEN_WIDTH + math.sin(i * 2 + self.total_frame * 0.004) * 20
                y = 50 + math.sin(i * 1.5 + self.total_frame * 0.003) * 120 + 100
                arcade.draw_circle_filled(x, y, 5 + math.sin(i + self.total_frame * 0.005) * 3, (255, 111, 0, 30))
                arcade.draw_circle_outline(x, y, 15 + math.sin(i * 1.3 + self.total_frame * 0.004) * 5,
                                           (255, 111, 0, 15), 1)
        elif pattern_type == 'void':
            for i in range(15):
                x = (i / 15) * SCREEN_WIDTH + math.sin(i * 1.7 + self.total_frame * 0.002) * 30
                y = (i % 5) * 130 + 30 + math.sin(i * 2.3 + self.total_frame * 0.003) * 20
                arcade.draw_text('✦', x, y, (233, 30, 99, 20), font_size=20)
        elif pattern_type == 'tech':
            for i in range(12):
                x = (i / 12) * SCREEN_WIDTH
                y = (i % 6) * 100 + 20
                draw_rect_filled(x, y, 30, 2, (0, 150, 255, 15))
                draw_rect_filled(x, y + 8, 20, 1, (0, 150, 255, 10))
        elif pattern_type == 'cosmic':
            for i in range(20):
                x = random.random() * SCREEN_WIDTH
                y = (i / 20) * SCREEN_HEIGHT + math.sin(i + self.total_frame * 0.001) * 10
                size = random.uniform(1, 3)
                arcade.draw_circle_filled(x, y, size, (150, 100, 255, 20))
        elif pattern_type == 'myth':
            symbols = ['🏛️', '⚡', '🐉', '🦅']
            for i in range(8):
                x = (i / 8) * SCREEN_WIDTH + math.sin(i * 1.3 + self.total_frame * 0.001) * 20
                y = (i % 4) * 150 + 50 + math.sin(i * 1.7 + self.total_frame * 0.002) * 20
                arcade.draw_text(symbols[i % len(symbols)], x, y, (200, 80, 0, 20), font_size=25)
        elif pattern_type == 'xeno':
            for i in range(15):
                x = (i / 15) * SCREEN_WIDTH + math.sin(i * 2 + self.total_frame * 0.003) * 15
                y = (i % 5) * 120 + 40 + math.sin(i * 1.8 + self.total_frame * 0.002) * 15
                arcade.draw_text('👾', x, y, (0, 200, 150, 20), font_size=20)

    def draw_player(self):
        if self.hit_flash > 0 and self.hit_flash % 6 < 3:
            return

        glow_color = (100, 200, 255, 40)
        arcade.draw_circle_filled(
            self.player.x, self.player.y,
            PLAYER_RADIUS * 5,
            glow_color
        )

        if self.powerups_active['shield']:
            shield_pulse = 1 + 0.05 * math.sin(self.total_frame * 0.08)
            arcade.draw_circle_outline(
                self.player.x, self.player.y,
                PLAYER_RADIUS * 2.4 * shield_pulse,
                (79, 195, 247),
                3
            )
            shield_glow = (79, 195, 247, 30)
            arcade.draw_circle_filled(
                self.player.x, self.player.y,
                PLAYER_RADIUS * 2.4 * shield_pulse,
                shield_glow
            )

        if self.player.super_charge > 0:
            charge_angle = (self.player.super_charge / 100) * 360
            arcade.draw_arc_outline(
                self.player.x, self.player.y - PLAYER_RADIUS - 10,
                20, 8,
                (255, 215, 0),
                0, charge_angle,
                3
            )
            if self.player.super_ready:
                arcade.draw_text(
                    "⚡",
                    self.player.x, self.player.y - PLAYER_RADIUS - 22,
                    (255, 215, 0),
                    font_size=12,
                    anchor_x='center',
                    anchor_y='center'
                )

        # Рисуем мозг (игрок)
        arcade.draw_ellipse_filled(
            self.player.x - 6, self.player.y,
            PLAYER_RADIUS * 0.55 * 2,
            PLAYER_RADIUS * 0.8 * 2,
            (255, 138, 128)
        )
        arcade.draw_ellipse_filled(
            self.player.x + 6, self.player.y,
            PLAYER_RADIUS * 0.55 * 2,
            PLAYER_RADIUS * 0.8 * 2,
            (240, 98, 146)
        )
        arcade.draw_ellipse_filled(
            self.player.x, self.player.y - 2,
            6,
                           PLAYER_RADIUS * 0.7 * 2,
            (200, 100, 120, 80)
        )
        arcade.draw_ellipse_filled(
            self.player.x - 6, self.player.y - 4,
            10, 8,
            (255, 255, 255, 40)
        )
        arcade.draw_ellipse_filled(
            self.player.x + 6, self.player.y - 4,
            10, 8,
            (255, 255, 255, 40)
        )
        arcade.draw_circle_filled(
            self.player.x - 6, self.player.y - 3,
            4,
            (255, 100, 150, 80)
        )
        arcade.draw_circle_filled(
            self.player.x + 6, self.player.y - 3,
            4,
            (255, 100, 150, 80)
        )

    def draw_enemies(self):
        for enemy in self.enemies:
            if len(enemy.trail) > 1:
                for i, pos in enumerate(enemy.trail[:-1]):
                    alpha = (i / len(enemy.trail)) * 0.3
                    arcade.draw_circle_filled(
                        pos[0], pos[1],
                        enemy.radius * 0.2 * (i / len(enemy.trail)),
                        (enemy.color[0], enemy.color[1], enemy.color[2], int(alpha * 255))
                    )

            if enemy.special_type == 'diver' and not enemy.special_visible:
                continue

            glow_alpha = 80 if enemy.hit_timer == 0 else 200
            arcade.draw_circle_filled(
                enemy.x, enemy.y,
                enemy.radius * 3.5,
                (enemy.color[0], enemy.color[1], enemy.color[2], glow_alpha)
            )

            size = enemy.radius * 1.8
            arcade.draw_text(
                enemy.emoji,
                enemy.x, enemy.y,
                (255, 255, 255),
                font_size=size,
                anchor_x='center',
                anchor_y='center'
            )

            if enemy.max_hp > 1 and not enemy.is_boss_projectile:
                bar_width = enemy.radius * 2
                bar_y = enemy.y - enemy.radius - 14
                draw_rect_filled(enemy.x, bar_y, bar_width, 5, (0, 0, 0, 180))
                hp_ratio = enemy.hp / enemy.max_hp if enemy.max_hp > 0 else 0
                hp_color = (79, 195, 247) if hp_ratio > 0.3 else (255, 23, 68)
                draw_rect_filled(enemy.x - bar_width / 2 + bar_width * hp_ratio / 2, bar_y, bar_width * hp_ratio, 5,
                                 hp_color)

            if enemy.special_type == 'shield':
                shield_pulse = 1 + 0.03 * math.sin(self.total_frame * 0.05)
                arcade.draw_circle_outline(
                    enemy.x, enemy.y,
                    enemy.radius * 1.6 * shield_pulse,
                    (79, 195, 247, 150),
                    3
                )

    def draw_boss(self):
        if not self.boss_active or not self.boss:
            return

        b = self.boss

        glow_alpha = 100 if b.hit_timer == 0 else 200
        arcade.draw_circle_filled(
            b.x, b.y,
            b.radius * 6 * b.scale,
            (b.color[0], b.color[1], b.color[2], glow_alpha)
        )

        for ring in range(3):
            ring_size = (b.radius * (2 + ring * 0.8) * b.scale +
                         math.sin(self.total_frame * (0.03 + ring * 0.01) + ring * 1.5) * (8 + ring * 3))
            arcade.draw_circle_outline(
                b.x, b.y,
                ring_size,
                (b.color[0], b.color[1], b.color[2], 30 - ring * 8),
                2 - ring * 0.4
            )

        arcade.draw_circle_filled(
            b.x, b.y,
            b.radius * 1.4 * b.scale,
            (b.color[0], b.color[1], b.color[2], 100)
        )

        size = b.radius * 2.4 * b.scale
        arcade.draw_text(
            b.emoji,
            b.x, b.y,
            (255, 255, 255),
            font_size=size,
            anchor_x='center',
            anchor_y='center'
        )

        arcade.draw_text(
            b.name,
            b.x, b.y - b.radius * 1.8 * b.scale,
            (255, 255, 255, 180),
            font_size=14,
            anchor_x='center',
            anchor_y='center'
        )

        bar_width = b.radius * 3.5 * b.scale
        bar_y = b.y - b.radius * b.scale - 32
        draw_rect_filled(b.x, bar_y, bar_width + 4, 14, (0, 0, 0, 200))

        hp_ratio = b.hp / b.max_hp if b.max_hp > 0 else 0
        hp_color = (79, 195, 247) if hp_ratio > 0.3 else (255, 23, 68)
        draw_rect_filled(b.x - bar_width / 2 + bar_width * hp_ratio / 2, bar_y, bar_width * hp_ratio, 10, hp_color)

        arcade.draw_text(
            f"HP {b.hp:.0f} / {b.max_hp}",
            b.x, bar_y,
            (255, 255, 255, 150),
            font_size=9,
            anchor_x='center',
            anchor_y='center'
        )

    def draw_bullets(self):
        for bullet in self.bullets:
            if len(bullet.trail) > 1:
                for i, pos in enumerate(bullet.trail[:-1]):
                    alpha = (i / len(bullet.trail)) * 0.5
                    color = (255, 215, 64) if bullet.is_laser else bullet.color
                    arcade.draw_circle_filled(
                        pos[0], pos[1],
                        bullet.radius * 0.5 * (i / len(bullet.trail)),
                        (color[0], color[1], color[2], int(alpha * 255))
                    )

            glow_radius = bullet.radius * 6 if bullet.is_laser else bullet.radius * 4
            glow_color = (255, 23, 68, 120) if bullet.is_laser else (bullet.color[0], bullet.color[1], bullet.color[2],
                                                                     120)
            arcade.draw_circle_filled(
                bullet.x, bullet.y,
                glow_radius,
                glow_color
            )

            color = (255, 215, 0) if bullet.is_super else (255, 255, 255)
            arcade.draw_circle_filled(
                bullet.x, bullet.y,
                bullet.radius,
                color
            )

            if bullet.is_laser:
                arcade.draw_line(
                    bullet.x, bullet.y + 10,
                    bullet.x, bullet.y + 60,
                    (255, 23, 68, 100),
                    6
                )

    def draw_powerups(self):
        for powerup in self.powerups:
            float_offset = math.sin(powerup.wobble) * 4
            pulse = 1 + 0.08 * math.sin(powerup.wobble * 1.5)

            arcade.draw_circle_filled(
                powerup.x, powerup.y + float_offset,
                           powerup.radius * 4 * pulse,
                (powerup.color[0], powerup.color[1], powerup.color[2], 80)
            )

            arcade.draw_circle_filled(
                powerup.x, powerup.y + float_offset,
                           powerup.radius * pulse,
                powerup.color
            )

            arcade.draw_text(
                powerup.symbol,
                powerup.x, powerup.y + float_offset,
                (255, 255, 255),
                font_size=powerup.radius * 1.6,
                anchor_x='center',
                anchor_y='center'
            )

            arcade.draw_text(
                powerup.name,
                powerup.x, powerup.y + float_offset - powerup.radius * pulse - 14,
                (255, 255, 255, 80),
                font_size=8,
                anchor_x='center',
                anchor_y='center'
            )

    def draw_helpers(self):
        for helper in self.helpers:
            arcade.draw_circle_filled(
                helper['x'], helper['y'],
                36,
                (105, 240, 174, 60)
            )

            arcade.draw_circle_filled(
                helper['x'], helper['y'],
                12,
                (105, 240, 174)
            )

            arcade.draw_text(
                '🤖',
                helper['x'], helper['y'],
                (255, 255, 255),
                font_size=16,
                anchor_x='center',
                anchor_y='center'
            )

            arcade.draw_line(
                helper['x'], helper['y'],
                self.player.x, self.player.y,
                (105, 240, 174, 30),
                1
            )

    def draw_particles(self):
        self.particle_pool.draw()

    def draw_ui(self):
        lives_text = '❤️' * max(0, self.lives) + '🖤' * max(0, 3 - self.lives)
        arcade.draw_text(
            lives_text,
            10, SCREEN_HEIGHT - 32,
            (255, 255, 255),
            font_size=20
        )

        arcade.draw_text(
            f"🎯 {self.score}",
            110, SCREEN_HEIGHT - 32,
            (255, 255, 255),
            font_size=16
        )

        theme = self.current_level_data
        level_text = f"🌌 Уровень {self.level}"
        arcade.draw_text(
            level_text,
            SCREEN_WIDTH - 150, SCREEN_HEIGHT - 32,
            (theme['accent'][0], theme['accent'][1], theme['accent'][2], 200),
            font_size=14
        )

        arcade.draw_text(
            f"{theme['name']}",
            SCREEN_WIDTH - 150, SCREEN_HEIGHT - 52,
            (255, 255, 255, 100),
            font_size=10,
            anchor_x='left'
        )

        y_pos = SCREEN_HEIGHT - 52
        indicators = []
        if self.powerups_active['shield']:
            indicators.append('🛡️')
        if self.powerups_active['power']:
            indicators.append('⚡')
        if self.powerups_active['laser']:
            indicators.append('🔴')
        if self.powerups_active['helper']:
            indicators.append('🤖')
        if self.powerups_active['bomb']:
            indicators.append('💥')
        if self.powerups_active['barrier']:
            indicators.append('🛡️')
        if self.bomb_cooldown > 0:
            indicators.append(f'⏳{self.bomb_cooldown // 60 + 1}s')

        if indicators:
            text = ' '.join(indicators)
            arcade.draw_text(
                text,
                10, y_pos,
                (255, 255, 255),
                font_size=16
            )

    def draw_combo(self):
        if self.combo > 1:
            alpha = min(1, self.combo / 15)
            size = 18 + min(self.combo, 25)
            arcade.draw_text(
                f"🔥 x{self.combo}",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT - 32,
                (255, 215, 0, int(alpha * 200)),
                font_size=size,
                anchor_x='center',
                anchor_y='bottom'
            )

    def draw_progress(self):
        if not self.boss_active and not self.boss_spawned and self.level_complete_timer == 0:
            enemies_needed = self.get_enemies_needed_for_boss()
            progress = min(1, self.enemies_killed_in_level / enemies_needed) if enemies_needed > 0 else 1
            theme = self.current_level_data

            draw_rect_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 10, 140, 5, (255, 255, 255, 20))
            draw_rect_filled(
                SCREEN_WIDTH / 2 - 70 + 70 * progress,
                SCREEN_HEIGHT - 10,
                140 * progress, 5,
                (theme['accent'][0], theme['accent'][1], theme['accent'][2], 200)
            )

            arcade.draw_text(
                f"👹 {self.enemies_killed_in_level}/{enemies_needed}",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT - 18,
                (255, 255, 255, 80),
                font_size=7,
                anchor_x='center',
                anchor_y='bottom'
            )

    def draw_affirmation(self):
        if self.affirmation_timer > 0:
            alpha = min(1, self.affirmation_timer / 20)
            arcade.draw_text(
                self.affirmation_text,
                SCREEN_WIDTH / 2, SCREEN_HEIGHT - 100,
                (255, 255, 255, int(alpha * 255)),
                font_size=18,
                anchor_x='center',
                anchor_y='center'
            )
            arcade.draw_text(
                self.affirmation_sub,
                SCREEN_WIDTH / 2, SCREEN_HEIGHT - 120,
                (255, 255, 255, int(alpha * 150)),
                font_size=12,
                anchor_x='center',
                anchor_y='center'
            )

    def draw_boss_warning(self):
        if self.boss_warning_timer > 0:
            alpha = min(1, self.boss_warning_timer / 30)

            arcade.draw_text(
                "👹 БОСС",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30,
                (255, 23, 68, int(alpha * 255)),
                font_size=38,
                anchor_x='center',
                anchor_y='center'
            )
            arcade.draw_text(
                self.boss_warning_name or "Повелитель Страхов",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 10,
                (255, 255, 255, int(alpha * 150)),
                font_size=16,
                anchor_x='center',
                anchor_y='center'
            )

    def draw_level_complete(self):
        if self.level_complete_timer > 0:
            alpha = min(1, self.level_complete_timer / 30)

            arcade.draw_text(
                "🎉 УРОВЕНЬ ПРОЙДЕН!",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 30,
                (255, 215, 0, int(alpha * 255)),
                font_size=32,
                anchor_x='center',
                anchor_y='center'
            )
            arcade.draw_text(
                f"{self.current_level_data['name']} — побеждён!",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 10,
                (255, 255, 255, int(alpha * 150)),
                font_size=16,
                anchor_x='center',
                anchor_y='center'
            )

    # ============================================================
    # МЕНЮ
    # ============================================================

    def draw_main_menu(self):
        draw_rect_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 230))

        arcade.draw_text(
            "🧠",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 140,
            (255, 255, 255),
            font_size=70,
            anchor_x='center',
            anchor_y='center'
        )

        arcade.draw_text(
            "ПСИХО-БОЙ",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 80,
            (108, 92, 231),
            font_size=44,
            anchor_x='center',
            anchor_y='center'
        )

        arcade.draw_text(
            "✦ БИТВА СО СТРАХАМИ ✦",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 35,
            (255, 255, 255, 150),
            font_size=16,
            anchor_x='center',
            anchor_y='center'
        )

        buttons = [
            ("⚔️ НАЧАТЬ БИТВУ", SCREEN_HEIGHT / 2 - 20, self.start_game),
            ("📊 СТАТИСТИКА", SCREEN_HEIGHT / 2 - 70, None),
        ]

        for text, y, _ in buttons:
            is_hover = (SCREEN_WIDTH / 2 - 120 < self.mouse_x < SCREEN_WIDTH / 2 + 120 and
                        y - 20 < self.mouse_y < y + 20)
            color = (108, 92, 231) if is_hover else (255, 255, 255, 50)
            draw_rect_filled(SCREEN_WIDTH / 2, y, 240, 40, color)
            arcade.draw_text(
                text,
                SCREEN_WIDTH / 2, y,
                (255, 255, 255),
                font_size=16,
                anchor_x='center',
                anchor_y='center'
            )

        arcade.draw_text(
            "v6.0 — 10 уровней страхов",
            SCREEN_WIDTH / 2, 15,
            (255, 255, 255, 40),
            font_size=10,
            anchor_x='center',
            anchor_y='center'
        )

    def draw_stats(self):
        draw_rect_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 230))

        arcade.draw_text(
            "📊 СТАТИСТИКА",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT - 60,
            (108, 92, 231),
            font_size=30,
            anchor_x='center',
            anchor_y='center'
        )

        stats = self.load_stats()

        lines = [
            f"🎯 Всего очков: {stats.get('high_score', 0)}",
            f"💀 Всего убито: {stats.get('total_kills', 0)}",
            f"👹 Боссов убито: {stats.get('total_bosses', 0)}",
            f"🔥 Макс. комбо: {stats.get('max_combo', 0)}",
            f"🏆 Макс. уровень: {stats.get('max_level_reached', 1)}",
            f"🛡️ Щитов использовано: {stats.get('shield_used', 0)}",
            f"🔴 Лазеров использовано: {stats.get('laser_used', 0)}",
            f"⏱ Сыграно: {stats.get('games_played', 0)} игр",
        ]

        last_played = stats.get('last_played', '')
        if last_played:
            lines.append(f"📅 Последняя игра: {last_played}")

        # Достижения
        achievements = stats.get('achievements', {})
        unlocked = sum(1 for v in achievements.values() if v)
        lines.append(f"🏅 Достижений: {unlocked}/{len(ACHIEVEMENTS)}")

        y_offset = SCREEN_HEIGHT - 110
        for line in lines:
            arcade.draw_text(
                line,
                SCREEN_WIDTH / 2, y_offset,
                (255, 255, 255, 200),
                font_size=16,
                anchor_x='center',
                anchor_y='center'
            )
            y_offset -= 30

        # Кнопка "Назад"
        btn_y = 40
        is_hover = (SCREEN_WIDTH / 2 - 100 < self.mouse_x < SCREEN_WIDTH / 2 + 100 and
                    btn_y - 20 < self.mouse_y < btn_y + 20)
        color = (108, 92, 231) if is_hover else (255, 255, 255, 50)
        draw_rect_filled(SCREEN_WIDTH / 2, btn_y, 200, 40, color)
        arcade.draw_text(
            "← НАЗАД",
            SCREEN_WIDTH / 2, btn_y,
            (255, 255, 255),
            font_size=18,
            anchor_x='center',
            anchor_y='center'
        )

    def draw_game_over(self):
        draw_rect_filled(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2, SCREEN_WIDTH, SCREEN_HEIGHT, (0, 0, 0, 200))

        if self.victory:
            arcade.draw_text(
                "🏆 Молодец!",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60,
                (255, 215, 0),
                font_size=38,
                anchor_x='center',
                anchor_y='center'
            )
            arcade.draw_text(
                "Ты справился со своими фобиями!",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 25,
                (255, 215, 0, 180),
                font_size=16,
                anchor_x='center',
                anchor_y='center'
            )
        else:
            arcade.draw_text(
                "💀 Тьма победила",
                SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 60,
                (255, 23, 68),
                font_size=44,
                anchor_x='center',
                anchor_y='center'
            )

        arcade.draw_text(
            f"Ты справился с {self.score} страхами",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 10,
            (255, 255, 255, 150),
            font_size=18,
            anchor_x='center',
            anchor_y='center'
        )

        arcade.draw_text(
            f"Уровень: {self.level}",
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 20,
            (255, 255, 255, 100),
            font_size=16,
            anchor_x='center',
            anchor_y='center'
        )

        buttons = [
            ("🔄 Ещё раз", SCREEN_WIDTH / 2 - 80, SCREEN_HEIGHT / 2 - 80, self.restart_game),
            ("🏠 В меню", SCREEN_WIDTH / 2 + 80, SCREEN_HEIGHT / 2 - 80, self.go_to_menu),
        ]

        for text, x, y, _ in buttons:
            draw_rect_filled(x, y, 130, 45, (108, 92, 231) if "Ещё" in text else (255, 255, 255, 20))
            arcade.draw_text(
                text,
                x, y,
                (255, 255, 255),
                font_size=16,
                anchor_x='center',
                anchor_y='center'
            )

    # ============================================================
    # ОБРАБОТКА СОБЫТИЙ
    # ============================================================

    def on_key_press(self, key, modifiers):
        if self.show_main_menu:
            if key == arcade.key.ENTER or key == arcade.key.SPACE:
                self.start_game()
            elif key == arcade.key.ESCAPE:
                return

        if self.game_over:
            return

        if key == arcade.key.LEFT or key == arcade.key.A:
            self.keys['left'] = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.keys['right'] = True
        elif key == arcade.key.SPACE or key == arcade.key.UP or key == arcade.key.W:
            self.keys['space'] = True
        elif key == arcade.key.B:
            self.keys['bomb'] = True
            self.activate_bomb()
        elif key == arcade.key.E:
            self.keys['barrier'] = True
            self.activate_barrier()
        elif key == arcade.key.ESCAPE:
            self.go_to_menu()
        elif key == arcade.key.P:
            self.paused = not self.paused

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT or key == arcade.key.A:
            self.keys['left'] = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.keys['right'] = False
        elif key == arcade.key.SPACE or key == arcade.key.UP or key == arcade.key.W:
            self.keys['space'] = False
            self.super_bullet_charging = False
            self.super_bullet_timer = 0

    def on_mouse_motion(self, x, y, dx, dy):
        self.mouse_x = x
        self.mouse_y = y

        if self.game_over or self.show_main_menu or self.show_stats:
            return
        self.player.x = max(PLAYER_RADIUS, min(SCREEN_WIDTH - PLAYER_RADIUS, x))

    def on_mouse_press(self, x, y, button, modifiers):
        if self.show_main_menu:
            if (SCREEN_WIDTH / 2 - 120 < x < SCREEN_WIDTH / 2 + 120 and
                    SCREEN_HEIGHT / 2 - 40 < y < SCREEN_HEIGHT / 2):
                self.start_game()
            elif (SCREEN_WIDTH / 2 - 120 < x < SCREEN_WIDTH / 2 + 120 and
                  SCREEN_HEIGHT / 2 - 90 < y < SCREEN_HEIGHT / 2 - 50):
                self.show_main_menu = False
                self.show_stats = True
            return

        if self.show_stats:
            if (SCREEN_WIDTH / 2 - 100 < x < SCREEN_WIDTH / 2 + 100 and
                    20 < y < 60):
                self.show_stats = False
                self.show_main_menu = True
            return

        if self.game_over:
            if (SCREEN_WIDTH / 2 - 145 < x < SCREEN_WIDTH / 2 - 15 and
                    SCREEN_HEIGHT / 2 - 100 < y < SCREEN_HEIGHT / 2 - 55):
                self.restart_game()
            elif (SCREEN_WIDTH / 2 + 15 < x < SCREEN_WIDTH / 2 + 145 and
                  SCREEN_HEIGHT / 2 - 100 < y < SCREEN_HEIGHT / 2 - 55):
                self.go_to_menu()
            return

        if button == arcade.MOUSE_BUTTON_LEFT:
            if self._last_click_time and time.time() - self._last_click_time < 0.3:
                self.activate_bomb()
            self._last_click_time = time.time()
            self.is_pointer_down = True
            self.shoot()

    def on_mouse_release(self, x, y, button, modifiers):
        self.is_pointer_down = False
        self.super_bullet_charging = False
        self.super_bullet_timer = 0

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        if self.game_over or self.show_main_menu or self.show_stats:
            return
        self.player.x = max(PLAYER_RADIUS, min(SCREEN_WIDTH - PLAYER_RADIUS, x))

    # ============================================================
    # ДЕЙСТВИЯ МЕНЮ
    # ============================================================

    def start_game(self):
        self.show_main_menu = False
        self.game_started = True
        self.restart_game()

    def restart_game(self):
        self.setup()
        self.game_started = True
        self.game_over = False
        self.victory = False
        self.show_main_menu = False
        self.show_affirmation("🔄 НОВАЯ ИГРА!", "Ты сильнее, чем думаешь")
        self._start_music(1)

    def go_to_menu(self):
        self._stop_music()
        self.setup()
        self.game_started = False
        self.game_over = False
        self.show_main_menu = True

    # ============================================================
    # ТАЧ-УПРАВЛЕНИЕ ДЛЯ МОБИЛЬНЫХ
    # ============================================================

    BTN_BOMB = (SCREEN_WIDTH - 65, 80, 50, 50)
    BTN_BARRIER = (SCREEN_WIDTH - 65, 145, 50, 50)
    BTN_FIRE_LEFT = 10
    BTN_FIRE_RIGHT = 110
    BTN_FIRE_BOTTOM = 10
    BTN_FIRE_SIZE = 100

    def _in_rect(self, x, y, rx, ry, rw, rh) -> bool:
        return rx - rw // 2 < x < rx + rw // 2 and ry - rh // 2 < y < ry + rh // 2

    def _is_fire_area(self, x, y) -> bool:
        return (self.BTN_FIRE_LEFT < x < self.BTN_FIRE_LEFT + self.BTN_FIRE_SIZE and
                self.BTN_FIRE_BOTTOM < y < self.BTN_FIRE_BOTTOM + self.BTN_FIRE_SIZE)

    def _is_bomb_area(self, x, y) -> bool:
        bx, by, bw, bh = self.BTN_BOMB
        return self._in_rect(x, y, bx, by, bw, bh)

    def _is_barrier_area(self, x, y) -> bool:
        bx, by, bw, bh = self.BTN_BARRIER
        return self._in_rect(x, y, bx, by, bw, bh)

    def on_touch_press(self, x, y, touch_id, modifiers):
        if self.show_main_menu:
            self.on_mouse_press(x, y, 1, modifiers)
            return True
        if self.show_stats:
            self.on_mouse_press(x, y, 1, modifiers)
            return True
        if self.game_over:
            self.on_mouse_press(x, y, 1, modifiers)
            return True

        if self._is_bomb_area(x, y):
            self.touch_bomb_id = touch_id
            self.activate_bomb()
            return True
        if self._is_barrier_area(x, y):
            self.touch_barrier_id = touch_id
            self.activate_barrier()
            return True
        if self._is_fire_area(x, y):
            self.touch_fire_id = touch_id
            self.shoot()
            return True

        self.touch_move_id = touch_id
        self.player.x = max(PLAYER_RADIUS, min(SCREEN_WIDTH - PLAYER_RADIUS, x))
        return True

    def on_touch_release(self, x, y, touch_id, modifiers):
        if touch_id == self.touch_bomb_id:
            self.touch_bomb_id = None
        elif touch_id == self.touch_barrier_id:
            self.touch_barrier_id = None
        elif touch_id == self.touch_fire_id:
            self.touch_fire_id = None
        elif touch_id == self.touch_move_id:
            self.touch_move_id = None
        return True

    def on_touch_motion(self, x, y, dx, dy, touch_id, modifiers):
        if touch_id == self.touch_move_id:
            self.player.x = max(PLAYER_RADIUS, min(SCREEN_WIDTH - PLAYER_RADIUS, x))
        return True

    def draw_touch_buttons(self):
        alpha = 80 if self.touch_buttons_visible else 0

        # Кнопка бомбы
        bx, by, bw, bh = self.BTN_BOMB
        is_active = self.powerups_active.get('bomb', False)
        col = (255, 165, 0, alpha + (40 if is_active else 0))
        draw_rect_filled(bx, by, bw, bh, col)
        arcade.draw_lbwh_rectangle_outline(bx - bw // 2, by - bh // 2, bw, bh, (255, 255, 255, int(alpha * 0.3)), 2)
        arcade.draw_text("💥", bx, by, (255, 255, 255), font_size=24, anchor_x='center', anchor_y='center')

        # Кнопка барьера
        bx2, by2, bw2, bh2 = self.BTN_BARRIER
        is_barrier = self.powerups_active.get('barrier', False)
        col2 = (0, 200, 255, alpha + (40 if is_barrier else 0))
        draw_rect_filled(bx2, by2, bw2, bh2, col2)
        arcade.draw_lbwh_rectangle_outline(bx2 - bw2 // 2, by2 - bh2 // 2, bw2, bh2, (255, 255, 255, int(alpha * 0.3)), 2)
        arcade.draw_text("🛡", bx2, by2, (255, 255, 255), font_size=24, anchor_x='center', anchor_y='center')

        # Зона стрельбы (левый нижний угол)
        fx, fy = self.BTN_FIRE_LEFT, self.BTN_FIRE_BOTTOM
        fs = self.BTN_FIRE_SIZE
        arcade.draw_arc_filled(fx + fs // 2, fy + fs // 2, fs, fs, (255, 255, 255, alpha // 3), 0, 360)
        arcade.draw_text("🔥", fx + fs // 2, fy + fs // 2, (255, 255, 255, alpha), font_size=20, anchor_x='center', anchor_y='center')


# ============================================================
# ЗАПУСК
# ============================================================
if __name__ == "__main__":
    game = PsychoBattle()
    arcade.run()