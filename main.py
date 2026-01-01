import pygame
import sys
import random
import math
import os
from settings import *
from utils import generate_sound_effect, generate_ambient_fallback, load_sound_asset, draw_text, draw_animated_player
from vfx import LightningBolt, FlameSpark, GhostTrail, SpeedLine, Shockwave, EnergyOrb, ParticleExplosion, ScreenFlash
from entities import Platform, Star, CursedEnemy
from ui_system import render_ui
from animations import CharacterAnimator, TrailEffect

# --- 1. SİSTEM VE EKRAN AYARLARI ---
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)

# Global Display Başlangıç
current_w, current_h = SCREEN_WIDTH, SCREEN_HEIGHT
screen = pygame.display.set_mode((current_w, current_h),
                                pygame.SCALED | pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1)
pygame.display.set_caption("Infinite Runner - METEOR DASH + PRO MENU")
clock = pygame.time.Clock()

# --- KALICI YÜZEYLER (Yeniden boyutlandırılabilir olmalı) ---
def create_surfaces(w, h):
    v = pygame.Surface((w, h), pygame.SRCALPHA)
    u = pygame.Surface((w, h), pygame.SRCALPHA)
    return v, u

vfx_surface, ui_surface = create_surfaces(current_w, current_h)

# --- 2. SES AYARLARI ---
FX_VOLUME = 0.7
AMBIENT_CHANNEL = pygame.mixer.Channel(0)
FX_CHANNEL = pygame.mixer.Channel(1)

JUMP_SOUND = load_sound_asset("assets/sfx/jump.wav", lambda: generate_sound_effect(350, 90), FX_VOLUME * 0.9)
DASH_SOUND = load_sound_asset("assets/sfx/dash.wav", lambda: generate_sound_effect(700, 60), FX_VOLUME * 1.1)
SLAM_SOUND = load_sound_asset("assets/sfx/slam.wav", lambda: generate_sound_effect(100, 150, 0.7), FX_VOLUME * 1.5)
EXPLOSION_SOUND = load_sound_asset("assets/sfx/explosion.wav", lambda: generate_sound_effect(50, 300, 0.5), FX_VOLUME * 1.2)
GAME_MUSIC = load_sound_asset("assets/music/game_action_music.ogg", generate_ambient_fallback, 1.0)

# --- OYUN İÇİ SABİTLER (EKSİK OLANLAR EKLENDİ) ---
MAX_VFX_COUNT = 200
MAX_DASH_VFX_PER_FRAME = 5
METEOR_CORE = (255, 255, 200)
METEOR_FIRE = (255, 80, 0)

class WarpLine(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, color, theme_color=None):
        super().__init__()
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(angle) * 15, math.sin(angle) * 15
        self.color = color
        self.theme_color = theme_color
        self.width = random.randint(2, 4)
        self.length_multiplier = random.uniform(10.0, 18.0)
        self.life = 8
        self.alpha = 255

    def update(self, camera_speed):
        self.x -= camera_speed
        self.x += self.vx * 0.8
        self.y += self.vy * 0.8
        self.life -= 1
        self.alpha = int(255 * (self.life / 8))
        if self.life <= 0:
            self.kill()

    def draw(self, surface):
        draw_color = self.theme_color if self.theme_color else self.color
        if self.alpha > 10:
            end_x = self.x - (self.vx * self.length_multiplier * 1.5)
            end_y = self.y - (self.vy * self.length_multiplier * 1.5)
            pygame.draw.line(surface, (*draw_color, self.alpha // 3),
                            (int(self.x), int(self.y)), (int(end_x), int(end_y)), self.width + 4)
            pygame.draw.line(surface, (*draw_color, self.alpha),
                            (int(self.x), int(self.y)), (int(end_x), int(end_y)), self.width)

# --- 3. DURUM DEĞİŞKENLERİ ---
GAME_STATE = 'MENU' 

# Menu ve Performans Ayarları
# Varsayılan değerler settings.py'deki indexlere göre
game_settings = {
    'fullscreen': True,
    'quality': 'HIGH',
    'res_index': 1, # Varsayılan: 1920x1080 (Listede 2. sırada)
    'fps_limit': 60,
    'fps_index': 1  # Varsayılan: 60 FPS
}
current_fps = 60
active_ui_elements = {}

# Loading Screen
loading_progress = 0.0
loading_logs = []
loading_timer = 0
loading_stage = 0
fake_log_messages = [
    "Initializing Core Systems...",
    "Scanning Hardware Configuration...",
    "Allocating VRAM for Meteor VFX...",
    "Pre-caching Particle Assets...",
    "Compiling Shader Modules...",
    "Synchronizing Audio Engine...",
    "Calibrating Physics...",
    "SYSTEM READY."
]

# Oyun Değişkenleri
CURRENT_THEME = THEMES[0]
CURRENT_SHAPE = 'circle'
score = 0.0
high_score = 0
camera_speed = INITIAL_CAMERA_SPEED
player_x, player_y = 150.0, float(current_h - 300)
y_velocity = 0.0
is_jumping = is_dashing = is_slamming = False
slam_stall_timer = 0
slam_cooldown = 0
jumps_left = MAX_JUMPS
dash_timer = 0
dash_cooldown_timer = 0
dash_vx = dash_vy = 0.0
screen_shake = 0
dash_particles_timer = 0
dash_angle = 0.0
dash_frame_counter = 0
character_state = 'idle'
slam_collision_check_frames = 0
active_damage_waves = [] 

character_animator = CharacterAnimator()
trail_effects = []
last_trail_time = 0
TRAIL_INTERVAL = 3

all_platforms = pygame.sprite.Group()
all_enemies = pygame.sprite.Group()
all_vfx = pygame.sprite.Group()
stars = [Star() for _ in range(120)]

# --- YARDIMCI FONKSİYONLAR ---
def apply_display_settings():
    """Çözünürlük ve ekran modunu uygular"""
    global screen, vfx_surface, ui_surface, current_w, current_h
    
    res = AVAILABLE_RESOLUTIONS[game_settings['res_index']]
    current_w, current_h = res
    
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    if game_settings['fullscreen']:
        flags |= pygame.FULLSCREEN | pygame.SCALED
    
    # Ekranı yeniden oluştur
    screen = pygame.display.set_mode((current_w, current_h), flags, vsync=1)
    
    # Yardımcı yüzeyleri de yeni boyuta göre güncelle
    vfx_surface, ui_surface = create_surfaces(current_w, current_h)
    
    # Yıldızları yeni ekrana göre dağıt
    global stars
    stars = [Star() for _ in range(120)]

def add_new_platform(start_x=None):
    if start_x is None:
        if len(all_platforms) > 0:
            rightmost = max(all_platforms, key=lambda p: p.rect.right)
            gap = random.randint(GAP_MIN, GAP_MAX)
            start_x = rightmost.rect.right + gap
        else:
            start_x = current_w
    width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)
    y = random.choice(PLATFORM_HEIGHTS)
    
    # Platform yüksekliği ekran boyutuna göre ayarlanmalı ama şimdilik sabit
    # Dinamik olması için PLATFORM_HEIGHTS da güncellenmeli ama basitleştirdik
    
    new_plat = Platform(start_x, y, width, 50)
    all_platforms.add(new_plat)
    
    if width > 120 and random.random() < 0.4:
        enemy = CursedEnemy(new_plat)
        all_enemies.add(enemy)

def start_loading_sequence():
    global GAME_STATE, loading_progress, loading_logs, loading_timer, loading_stage
    GAME_STATE = 'LOADING'
    loading_progress = 0.0
    loading_logs = []
    loading_timer = 0
    loading_stage = 0
    
    # Kalite ayarı kontrolü
    global MAX_VFX_COUNT, MAX_DASH_VFX_PER_FRAME
    if game_settings['quality'] == 'LOW':
        MAX_VFX_COUNT = 50
        MAX_DASH_VFX_PER_FRAME = 2
    else:
        MAX_VFX_COUNT = 200
        MAX_DASH_VFX_PER_FRAME = 5

def init_game():
    global player_x, player_y, y_velocity, score, camera_speed, jumps_left
    global is_jumping, is_dashing, is_slamming, dash_timer, dash_cooldown_timer, slam_stall_timer, slam_cooldown
    global CURRENT_THEME, CURRENT_SHAPE, screen_shake, dash_particles_timer, dash_angle, dash_frame_counter
    global character_state, trail_effects, last_trail_time, slam_collision_check_frames, active_damage_waves

    if GAME_MUSIC:
        AMBIENT_CHANNEL.play(GAME_MUSIC, loops=-1)
    camera_speed = INITIAL_CAMERA_SPEED
    player_x, player_y = 150.0, float(current_h - 300)
    y_velocity = score = dash_timer = dash_cooldown_timer = screen_shake = slam_stall_timer = slam_cooldown = 0
    is_jumping = is_dashing = is_slamming = False
    jumps_left = MAX_JUMPS
    dash_particles_timer = 0
    dash_angle = 0.0
    dash_frame_counter = 0
    character_state = 'idle'
    slam_collision_check_frames = 0
    trail_effects.clear()
    active_damage_waves.clear()
    last_trail_time = 0

    character_animator.__init__()

    CURRENT_THEME = random.choice(THEMES)
    CURRENT_SHAPE = random.choice(PLAYER_SHAPES)
    all_platforms.empty()
    all_enemies.empty()
    all_vfx.empty()
    
    start_plat = Platform(0, current_h - 50, 400, 50)
    all_platforms.add(start_plat)
    current_right = 400
    while current_right < current_w + 200:
        add_new_platform()
        current_right = max(p.rect.right for p in all_platforms)

def simple_dash_movement():
    global player_x, player_y, is_dashing, dash_timer
    player_x += dash_vx
    player_y += dash_vy
    dash_timer -= 1
    if dash_timer <= 0:
        is_dashing = False
        all_vfx.add(ParticleExplosion(player_x + 15, player_y + 15, CURRENT_THEME["border_color"], 8))

# --- 5. ANA DÖNGÜ ---
running = True
last_time = pygame.time.get_ticks()
frame_count = 0

while running:
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_time) / 1000.0
    last_time = current_time
    time_ms = current_time
    frame_count += 1
    
    mouse_pos = pygame.mouse.get_pos()

    # VFX Temizliği
    if frame_count % 30 == 0:
        if len(all_vfx) > MAX_VFX_COUNT:
             sprites = list(all_vfx.sprites())
             for sprite in sprites[:20]:
                 sprite.kill()

    # --- EVENT HANDLING ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # UI Tıklama Kontrolleri
            if GAME_STATE == 'MENU':
                if 'start' in active_ui_elements and active_ui_elements['start'].collidepoint(mouse_pos):
                    start_loading_sequence()
                elif 'settings' in active_ui_elements and active_ui_elements['settings'].collidepoint(mouse_pos):
                    GAME_STATE = 'SETTINGS'
                elif 'exit' in active_ui_elements and active_ui_elements['exit'].collidepoint(mouse_pos):
                    running = False
            
            elif GAME_STATE == 'SETTINGS':
                # 1. Fullscreen Toggle (Sadece değişkeni değiştirir, Apply ile uygulanır)
                if 'toggle_fullscreen' in active_ui_elements and active_ui_elements['toggle_fullscreen'].collidepoint(mouse_pos):
                    game_settings['fullscreen'] = not game_settings['fullscreen']
                
                # 2. Kalite Toggle (Anında etki eder)
                elif 'toggle_quality' in active_ui_elements and active_ui_elements['toggle_quality'].collidepoint(mouse_pos):
                    game_settings['quality'] = 'LOW' if game_settings['quality'] == 'HIGH' else 'HIGH'
                
                # 3. Çözünürlük Değiştirme (Döngüsel)
                elif 'change_resolution' in active_ui_elements and active_ui_elements['change_resolution'].collidepoint(mouse_pos):
                    game_settings['res_index'] = (game_settings['res_index'] + 1) % len(AVAILABLE_RESOLUTIONS)
                
                # 4. FPS Değiştirme (Anında etki eder)
                elif 'change_fps' in active_ui_elements and active_ui_elements['change_fps'].collidepoint(mouse_pos):
                    game_settings['fps_index'] = (game_settings['fps_index'] + 1) % len(FPS_LIMITS)
                    game_settings['fps_limit'] = FPS_LIMITS[game_settings['fps_index']]
                    current_fps = game_settings['fps_limit']
                
                # 5. Ayarları Uygula Butonu
                elif 'apply_changes' in active_ui_elements and active_ui_elements['apply_changes'].collidepoint(mouse_pos):
                    apply_display_settings()
                
                # 6. Geri Dön
                elif 'back' in active_ui_elements and active_ui_elements['back'].collidepoint(mouse_pos):
                    GAME_STATE = 'MENU'

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if GAME_STATE == 'PLAYING':
                    GAME_STATE = 'MENU' 
                    AMBIENT_CHANNEL.stop()
                elif GAME_STATE in ['MENU', 'SETTINGS']:
                    running = False

            if event.key == pygame.K_p:
                if GAME_STATE == 'PLAYING':
                    GAME_STATE = 'PAUSED'
                    AMBIENT_CHANNEL.pause()
                elif GAME_STATE == 'PAUSED':
                    GAME_STATE = 'PLAYING'
                    AMBIENT_CHANNEL.unpause()

            if GAME_STATE == 'GAME_OVER' and event.key == pygame.K_r:
                init_game(); GAME_STATE = 'PLAYING'

            # OYUN KONTROLLERİ
            if GAME_STATE == 'PLAYING':
                px, py = int(player_x + 15), int(player_y + 15)
                if event.key == pygame.K_w and jumps_left > 0 and not is_dashing:
                    jumps_left -= 1
                    is_jumping = True; is_slamming = False; y_velocity = -JUMP_POWER
                    character_state = 'jumping'
                    if JUMP_SOUND: FX_CHANNEL.play(JUMP_SOUND)
                    all_vfx.add(ParticleExplosion(px, py, CURRENT_THEME["player_color"], 6))
                    for _ in range(2):
                        all_vfx.add(EnergyOrb(px + random.randint(-10, 10),
                                                py + random.randint(-10, 10),
                                                CURRENT_THEME["border_color"], 4, 15))

                if event.key == pygame.K_s and is_jumping and not is_dashing and not is_slamming and slam_cooldown == 0:
                    is_slamming = True
                    slam_stall_timer = 15
                    slam_cooldown = 120
                    y_velocity = 0
                    character_state = 'slamming'
                    slam_collision_check_frames = 0
                    if SLAM_SOUND: FX_CHANNEL.play(SLAM_SOUND)
                    all_vfx.add(ScreenFlash(PLAYER_SLAM, 80, 8))
                    all_vfx.add(Shockwave(px, py, PLAYER_SLAM, max_radius=200, rings=3, speed=25))
                    
                    for _ in range(3):
                        all_vfx.add(LightningBolt(px, py,
                                                    px + random.randint(-60, 60),
                                                    py + random.randint(-60, 60),
                                                    PLAYER_SLAM, 12))

                if event.key == pygame.K_SPACE and dash_cooldown_timer == 0 and not is_dashing:
                    is_dashing = True
                    dash_timer = DASH_DURATION
                    dash_cooldown_timer = DASH_COOLDOWN
                    screen_shake = 8
                    dash_particles_timer = 0
                    dash_frame_counter = 0
                    character_state = 'dashing'
                    if DASH_SOUND: FX_CHANNEL.play(DASH_SOUND)
                    all_vfx.add(ScreenFlash(METEOR_CORE, 80, 6))
                    all_vfx.add(Shockwave(px, py, METEOR_FIRE, max_radius=120, rings=2, speed=15))
                    
                    keys = pygame.key.get_pressed()
                    dx = (keys[pygame.K_d] - keys[pygame.K_a]); dy = (keys[pygame.K_s] - keys[pygame.K_w])
                    if dx == 0 and dy == 0: dx = 1
                    mag = math.sqrt(dx*dx + dy*dy)
                    dash_vx, dash_vy = (dx/mag)*DASH_SPEED, (dy/mag)*DASH_SPEED
                    is_jumping = True; y_velocity = 0
                    dash_angle = math.atan2(dash_vy, dash_vx)

    # --- OYUN LOJİĞİ & GÜNCELLEMELER ---
    if GAME_STATE == 'LOADING':
        # Yükleme Simülasyonu
        loading_timer += 1
        if loading_timer % random.randint(20, 45) == 0 and loading_stage < len(fake_log_messages):
            loading_logs.append(fake_log_messages[loading_stage])
            loading_stage += 1
            loading_progress = min(0.95, loading_stage / len(fake_log_messages))
            
        if loading_stage >= len(fake_log_messages):
            loading_progress += 0.01 
            if loading_progress >= 1.0:
                init_game()
                GAME_STATE = 'PLAYING'

    elif GAME_STATE == 'PLAYING':
        camera_speed = min(MAX_CAMERA_SPEED, camera_speed + SPEED_INCREMENT_RATE)
        score += 0.1 * camera_speed

        old_x, old_y = player_x, player_y

        keys = pygame.key.get_pressed()
        horizontal_move = keys[pygame.K_d] - keys[pygame.K_a]
        if horizontal_move != 0 and not is_dashing and not is_slamming:
            character_state = 'running'
        elif not is_jumping and not is_dashing and not is_slamming:
            character_state = 'idle'

        is_grounded = not is_jumping and not is_slamming and not is_dashing
        character_animator.update(dt, character_state, is_grounded, y_velocity, is_dashing, is_slamming)

        last_trail_time += 1
        if last_trail_time >= TRAIL_INTERVAL and (is_dashing or is_slamming):
            last_trail_time = 0
            trail_color = CURRENT_THEME["player_color"]
            if is_dashing:
                trail_color = METEOR_FIRE
                trail_size = random.randint(8, 14)
            elif is_slamming:
                trail_color = PLAYER_SLAM
                trail_size = random.randint(8, 12)
            
            trail_effects.append(TrailEffect(player_x + 15, player_y + 15, trail_color, trail_size, life=12))

        # Hasar Dalgaları
        for wave in active_damage_waves[:]:
            wave['r'] += wave['speed']
            wave['x'] -= camera_speed
            for enemy in all_enemies:
                dist = math.sqrt((enemy.rect.centerx - wave['x'])**2 + (enemy.rect.centery - wave['y'])**2)
                if dist < wave['r'] + 20 and dist > wave['r'] - 40:
                    enemy.kill()
                    score += 500
                    all_vfx.add(ParticleExplosion(enemy.rect.centerx, enemy.rect.centery, CURSED_PURPLE, 20))
                    all_vfx.add(ScreenFlash(CURSED_PURPLE, 30, 2))
            if wave['r'] > wave['max_r']:
                active_damage_waves.remove(wave)

        # --- DASH MANTIĞI (KORUNAN BÖLÜM) ---
        if is_dashing:
            px, py = int(player_x + 15), int(player_y + 15)
            dash_frame_counter += 1
            
            for _ in range(4): # 4 adet meteor parçacığı
                inv_angle = dash_angle + math.pi + random.uniform(-0.5, 0.5)
                spark_speed = random.uniform(5, 15)
                color = random.choice([(255, 50, 0), (255, 150, 0), (255, 255, 100)])
                all_vfx.add(FlameSpark(px, py, inv_angle, spark_speed, color, life=20, size=random.randint(4, 8)))

            if dash_frame_counter % 5 == 0:
                all_vfx.add(Shockwave(px, py, (255, 200, 100), max_radius=70, width=2, speed=10))

            # AoE Hasarı
            meteor_hit_radius = 120
            enemy_hits_aoe = [e for e in all_enemies if math.sqrt((e.rect.centerx - px)**2 + (e.rect.centery - py)**2) < meteor_hit_radius]
            
            for enemy in enemy_hits_aoe:
                enemy.kill()
                score += 500
                screen_shake = 10
                if EXPLOSION_SOUND: FX_CHANNEL.play(EXPLOSION_SOUND)
                all_vfx.add(ParticleExplosion(enemy.rect.centerx, enemy.rect.centery, METEOR_FIRE, 25))
                all_vfx.add(Shockwave(enemy.rect.centerx, enemy.rect.centery, (255, 100, 0), max_radius=90, width=4))

            if dash_particles_timer > 0:
                dash_particles_timer -= 1
            else:
                dash_particles_timer = 4
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                all_vfx.add(WarpLine(px + offset_x, py + offset_y, dash_angle + random.uniform(-0.15, 0.15), METEOR_CORE, METEOR_FIRE))

            simple_dash_movement()
            player_x -= camera_speed

            if dash_timer <= 0:
                is_dashing = False
                y_velocity = 0
                character_state = 'idle'

        # --- SLAM MANTIĞI (KORUNAN BÖLÜM) ---
        elif is_slamming and slam_stall_timer > 0:
            slam_stall_timer -= 1
            slam_collision_check_frames += 1
            if slam_stall_timer % 3 == 0:
                for _ in range(2):
                    angle = random.uniform(0, math.pi * 2)
                    dist = random.randint(20, 40)
                    ex = player_x + 15 + math.cos(angle) * dist
                    ey = player_y + 15 + math.sin(angle) * dist
                    all_vfx.add(FlameSpark(ex, ey, angle + math.pi, dist/10, PLAYER_SLAM, life=15))

            vibration = random.randint(-1, 1) if slam_stall_timer > 7 else 0
            player_x += vibration
            if slam_stall_timer == 0:
                y_velocity = 30
                screen_shake = 12
                all_vfx.add(ParticleExplosion(player_x+15, player_y+15, PLAYER_SLAM, 12))

        else:
            player_x -= camera_speed
            if keys[pygame.K_a]: player_x -= PLAYER_SPEED
            if keys[pygame.K_d]: player_x += PLAYER_SPEED
            player_y += y_velocity
            if is_slamming: y_velocity += SLAM_GRAVITY * 1.8
            else: y_velocity += GRAVITY

        if dash_cooldown_timer > 0: dash_cooldown_timer -= 1
        if slam_cooldown > 0: slam_cooldown -= 1
        if screen_shake > 0: screen_shake -= 1

        PLAYER_W, PLAYER_H = 30, 30
        player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_W, PLAYER_H)
        
        # Çarpışmalar
        dummy_player = type('',(object,),{'rect':player_rect})()
        enemy_hits = pygame.sprite.spritecollide(dummy_player, all_enemies, False)
        
        for enemy in enemy_hits:
            if is_dashing or is_slamming:
                enemy.kill()
                score += 500
                screen_shake = 15
                if EXPLOSION_SOUND: FX_CHANNEL.play(EXPLOSION_SOUND)
                all_vfx.add(ParticleExplosion(enemy.rect.centerx, enemy.rect.centery, CURSED_PURPLE, 20))
                all_vfx.add(Shockwave(enemy.rect.centerx, enemy.rect.centery, GLITCH_BLACK, max_radius=80, width=5))
                pygame.time.delay(30) 
            else:
                GAME_STATE = 'GAME_OVER'
                high_score = max(high_score, int(score))
                AMBIENT_CHANNEL.stop()
                all_vfx.add(ParticleExplosion(player_x, player_y, CURSED_RED, 30))
        
        move_rect = pygame.Rect(int(player_x), int(min(old_y, player_y)), PLAYER_W, int(abs(player_y - old_y)) + PLAYER_H)
        collided_platforms = pygame.sprite.spritecollide(type('',(object,),{'rect':move_rect})(), all_platforms, False)
        
        for p in collided_platforms:
            platform_top = p.rect.top
            if (old_y + PLAYER_H <= platform_top + 15) and (player_y + PLAYER_H >= platform_top):
                player_y = platform_top - PLAYER_H
                if is_slamming:
                    y_velocity = -15
                    screen_shake = 30
                    active_damage_waves.append({'x': player_x + 15, 'y': platform_top, 'r': 10, 'max_r': 250, 'speed': 25})
                    for i in range(2):
                        wave = Shockwave(player_x+15, p.rect.top, (255, 180, 80), speed=25)
                        wave.radius = 30 + i*30; wave.max_radius = 200 + i*60
                        all_vfx.add(wave)
                    all_vfx.add(ParticleExplosion(player_x+15, p.rect.top, PLAYER_SLAM, 25))
                    is_slamming = False
                    is_jumping = True
                    jumps_left = MAX_JUMPS - 1
                    character_state = 'jumping'
                else:
                    y_velocity = 0
                    is_jumping = is_slamming = False
                    jumps_left = MAX_JUMPS
                    character_state = 'idle'
                    all_vfx.add(ParticleExplosion(player_x+15, player_y+30, CURRENT_THEME["player_color"], 8))
                break

        all_platforms.update(camera_speed)
        all_enemies.update(camera_speed)
        for s in stars: s.update(camera_speed)
        all_vfx.update(camera_speed)
        for trail in trail_effects[:]:
            try: trail.update(camera_speed, dt)
            except: trail.update(camera_speed)
            if trail.life <= 0: trail_effects.remove(trail)

        if len(all_platforms) > 0 and max(p.rect.right for p in all_platforms) < current_w + 100:
            add_new_platform()
        if player_x < -50 or player_y > current_h + 100:
            GAME_STATE = 'GAME_OVER'
            high_score = max(high_score, int(score))
            AMBIENT_CHANNEL.stop()

    # --- ÇİZİM ---
    if GAME_STATE in ['MENU', 'SETTINGS', 'LOADING']:
        screen.fill(DARK_BLUE)
        for s in stars:
            s.draw(screen)
            s.update(0.5)
        
        ui_data = {
            'settings': game_settings, 
            'progress': loading_progress,
            'logs': loading_logs,
            'time_ms': time_ms
        }
        active_ui_elements = render_ui(ui_surface, GAME_STATE, ui_data, mouse_pos)
        screen.blit(ui_surface, (0,0))
        
    else:
        # Oyun İçi Çizim
        anim_params = character_animator.get_draw_params()
        anim_offset = anim_params.get('screen_shake_offset', (0,0))
        global_offset = (random.randint(-screen_shake, screen_shake), random.randint(-screen_shake, screen_shake)) if screen_shake > 0 else (0,0)
        render_offset = (global_offset[0] + int(anim_offset[0]), global_offset[1] + int(anim_offset[1]))

        screen.fill(CURRENT_THEME["bg_color"])
        for s in stars: s.draw(screen)
        vfx_surface.fill((0, 0, 0, 0))
        
        for p in all_platforms: p.draw(screen, CURRENT_THEME)
        for e in all_enemies: e.draw(screen)
        for v in all_vfx: v.draw(vfx_surface)
        for trail in trail_effects: trail.draw(vfx_surface)

        if GAME_STATE in ('PLAYING', 'PAUSED', 'GAME_OVER') and GAME_STATE != 'GAME_OVER':
            p_color = CURRENT_THEME["player_color"]
            if is_dashing: p_color = METEOR_CORE
            elif is_slamming: p_color = PLAYER_SLAM
            modified_color = character_animator.get_modified_color(p_color)
            
            draw_animated_player(
                screen, CURRENT_SHAPE,
                int(player_x + 15) + render_offset[0], int(player_y + 15) + render_offset[1], 15,
                modified_color, anim_params
            )

        screen.blit(vfx_surface, render_offset)
        
        ui_surface.fill((0, 0, 0, 0))
        ui_data = {
            'theme': CURRENT_THEME, 'score': score, 'high_score': high_score,
            'dash_cd': dash_cooldown_timer, 'slam_cd': slam_cooldown, 'time_ms': time_ms
        }
        render_ui(ui_surface, GAME_STATE, ui_data)
        screen.blit(ui_surface, (0,0))

    pygame.display.flip()
    clock.tick(current_fps) # Dinamik FPS kullanımı

pygame.quit()
sys.exit()