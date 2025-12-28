import pygame
import sys
import random
import math
from settings import *
from utils import generate_sound_effect, generate_ambient_fallback, load_sound_asset, draw_text, draw_animated_player
from vfx import LightningBolt, FlameSpark, GhostTrail, SpeedLine, Shockwave, EnergyOrb, ParticleExplosion, ScreenFlash
from entities import Platform, Star
from ui_system import render_ui
from animations import CharacterAnimator, TrailEffect

# --- 1. SİSTEM VE EKRAN AYARLARI ---
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 
                                pygame.SCALED | pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE)
pygame.display.set_caption("Infinite Runner - ULTIMATE VFX & CYBER MENU")
clock = pygame.time.Clock()

# --- 2. SES AYARLARI ---
FX_VOLUME = 0.7
AMBIENT_CHANNEL = pygame.mixer.Channel(0)
FX_CHANNEL = pygame.mixer.Channel(1)

JUMP_SOUND = load_sound_asset("assets/sfx/jump.wav", lambda: generate_sound_effect(350, 90), FX_VOLUME * 0.9)
DASH_SOUND = load_sound_asset("assets/sfx/dash.wav", lambda: generate_sound_effect(700, 60), FX_VOLUME * 1.1)
SLAM_SOUND = load_sound_asset("assets/sfx/slam.wav", lambda: generate_sound_effect(100, 150, 0.7), FX_VOLUME * 1.5)
GAME_MUSIC = load_sound_asset("assets/music/game_action_music.ogg", generate_ambient_fallback, 1.0)
MENU_MUSIC = load_sound_asset("assets/music/menu_theme.ogg", generate_ambient_fallback, 1.2)

# --- DASH OPTİMİZASYON AYARLARI ---
DASH_SPEED = 40  # 30'dan 40'a çıkarıldı - DAHA HIZLI
DASH_DURATION = 20  # 15'ten 20'ye çıkarıldı - DAHA UZUN SÜRE
DASH_INVINCIBILITY = True
MAX_VFX_COUNT = 80  # 120'den 80'e düşürüldü - DAHA AZ EFEKT
PERFORMANCE_MODE = True  # Performans modu aktif

# --- OPTİMİZE EDİLMİŞ VFX SINIFLARI ---
class WarpLine(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, color, theme_color=None):
        super().__init__()
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(angle) * 15, math.sin(angle) * 15  # Daha hızlı
        self.color = color
        self.theme_color = theme_color
        self.width = random.randint(2, 4)
        self.length_multiplier = random.uniform(10.0, 18.0)  # Daha uzun
        self.life = 8  # Daha kısa ömür
        self.alpha = 255
        
    def update(self, camera_speed):
        self.x -= camera_speed
        self.x += self.vx * 0.8
        self.y += self.vy * 0.8
        self.life -= 1
        self.alpha = int(255 * (self.life / 8))
        if self.life <= 0: self.kill()
        
    def draw(self, surface):
        if PERFORMANCE_MODE and self.alpha < 100:
            return
            
        draw_color = self.theme_color if self.theme_color else self.color
        alpha_color = (*draw_color, self.alpha)
        
        end_x = self.x - (self.vx * self.length_multiplier * 1.5)  # Daha uzun
        end_y = self.y - (self.vy * self.length_multiplier * 1.5)
        
        # Basit glow efekti - performans için
        pygame.draw.line(surface, (*draw_color, self.alpha//3), 
                       (int(self.x), int(self.y)), 
                       (int(end_x), int(end_y)), self.width + 4)
        pygame.draw.line(surface, alpha_color, 
                        (int(self.x), int(self.y)), 
                        (int(end_x), int(end_y)), self.width)

# --- 3. DURUM DEGISKENLERI ---
CURRENT_THEME = THEMES[0]
CURRENT_SHAPE = 'circle'
GAME_STATE = 'START'
score = 0
high_score = 0
camera_speed = INITIAL_CAMERA_SPEED
player_x, player_y = 150, SCREEN_HEIGHT - 300
y_velocity = 0
is_jumping = is_dashing = is_slamming = False
slam_stall_timer = 0
slam_cooldown = 0
jumps_left = MAX_JUMPS
dash_timer = dash_cooldown_timer = 0
dash_vx = dash_vy = 0
screen_shake = 0
dash_particles_timer = 0
dash_angle = 0
dash_frame_counter = 0
character_state = 'idle'
slam_collision_check_frames = 0

# Animasyon sistemleri
character_animator = CharacterAnimator()
trail_effects = []
last_trail_time = 0
TRAIL_INTERVAL = 3  # 2'den 3'e - daha seyrek

all_platforms = pygame.sprite.Group()
all_vfx = pygame.sprite.Group()
stars = [Star() for _ in range(120)]  # 150'den 120'ye düşürüldü

# --- 4. YARDIMCI FONKSIYONLAR ---
def add_new_platform(start_x=None):
    if start_x is None:
        if len(all_platforms) > 0:
            rightmost = max(all_platforms, key=lambda p: p.rect.right)
            gap = random.randint(GAP_MIN, GAP_MAX)
            start_x = rightmost.rect.right + gap
        else: start_x = SCREEN_WIDTH
    width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)
    y = random.choice(PLATFORM_HEIGHTS)
    all_platforms.add(Platform(start_x, y, width, 50))

def init_game():
    global player_x, player_y, y_velocity, score, camera_speed, jumps_left
    global is_jumping, is_dashing, is_slamming, dash_timer, dash_cooldown_timer, slam_stall_timer, slam_cooldown
    global CURRENT_THEME, CURRENT_SHAPE, screen_shake, dash_particles_timer, dash_angle, dash_frame_counter
    global character_state, trail_effects, last_trail_time, slam_collision_check_frames
    
    if GAME_MUSIC: AMBIENT_CHANNEL.play(GAME_MUSIC, loops=-1)
    camera_speed = INITIAL_CAMERA_SPEED
    player_x, player_y = 150, SCREEN_HEIGHT - 300
    y_velocity = score = dash_timer = dash_cooldown_timer = screen_shake = slam_stall_timer = slam_cooldown = 0
    is_jumping = is_dashing = is_slamming = False
    jumps_left = MAX_JUMPS
    dash_particles_timer = 0
    dash_angle = 0
    dash_frame_counter = 0
    character_state = 'idle'
    slam_collision_check_frames = 0
    trail_effects.clear()
    last_trail_time = 0
    
    character_animator.__init__()
    
    CURRENT_THEME = random.choice(THEMES)
    CURRENT_SHAPE = random.choice(PLAYER_SHAPES)
    all_platforms.empty()
    all_vfx.empty()
    all_platforms.add(Platform(0, SCREEN_HEIGHT - 50, 400, 50))
    current_right = 400
    while current_right < SCREEN_WIDTH + 200:
        add_new_platform()
        current_right = max(p.rect.right for p in all_platforms)

# --- OPTİMİZE EDİLMİŞ ÇARPIŞMA FONKSİYONLARI ---
def simple_dash_movement():
    """BASİT dash hareketi - performans için"""
    global player_x, player_y, is_dashing, dash_timer
    
    # Dash sırasında platformlardan geç
    player_x += dash_vx
    player_y += dash_vy
    
    dash_timer -= 1
    if dash_timer <= 0:
        is_dashing = False
        # Dash bitişinde küçük bir efek
        if not PERFORMANCE_MODE:
            all_vfx.add(ParticleExplosion(player_x+15, player_y+15, 
                                        CURRENT_THEME["border_color"], 8))

# --- 5. ANA DONGU ---
running = True
last_time = pygame.time.get_ticks()
frame_count = 0

while running:
    current_time = pygame.time.get_ticks()
    dt = (current_time - last_time) / 1000.0
    last_time = current_time
    time_ms = current_time
    frame_count += 1
    
    # PERFORMANS: Her 30 frame'de bir VFX temizle
    if frame_count % 30 == 0 and len(all_vfx) > MAX_VFX_COUNT // 2:
        sprites = list(all_vfx.sprites())
        for sprite in sprites[:20]:
            if hasattr(sprite, 'life') and sprite.life < 5:
                sprite.kill()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT: running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: running = False
            
            if event.key == pygame.K_p:
                if GAME_STATE == 'PLAYING':
                    GAME_STATE = 'PAUSED'
                    AMBIENT_CHANNEL.pause()
                elif GAME_STATE == 'PAUSED':
                    GAME_STATE = 'PLAYING'
                    AMBIENT_CHANNEL.unpause()

            if GAME_STATE == 'START' and event.key == pygame.K_RETURN:
                init_game(); GAME_STATE = 'PLAYING'
            elif GAME_STATE == 'GAME_OVER' and event.key == pygame.K_r:
                init_game(); GAME_STATE = 'PLAYING'
            
            if GAME_STATE == 'PLAYING':
                px, py = player_x + 15, player_y + 15 
                if event.key == pygame.K_w and jumps_left > 0 and not is_dashing:
                    jumps_left -= 1
                    is_jumping = True; is_slamming = False; y_velocity = -JUMP_POWER
                    character_state = 'jumping'
                    
                    # Zıplama efektleri (MINIMAL)
                    if JUMP_SOUND: FX_CHANNEL.play(JUMP_SOUND)
                    if not PERFORMANCE_MODE:
                        all_vfx.add(ParticleExplosion(px, py, CURRENT_THEME["player_color"], 6))
                        for _ in range(2):
                            all_vfx.add(EnergyOrb(px + random.randint(-10, 10), 
                                                py + random.randint(-10, 10),
                                                CURRENT_THEME["border_color"], 4, 15))
                
                if event.key == pygame.K_s and is_jumping and not is_dashing and not is_slamming and slam_cooldown == 0:
                    is_slamming = True
                    slam_stall_timer = 15  # 18'den 15'e
                    slam_cooldown = 120 
                    y_velocity = 0
                    character_state = 'slamming'
                    slam_collision_check_frames = 0
                    
                    # Slam başlangıç efektleri (MINIMAL)
                    if SLAM_SOUND: FX_CHANNEL.play(SLAM_SOUND)
                    if not PERFORMANCE_MODE:
                        all_vfx.add(ScreenFlash(PLAYER_SLAM, 80, 8))
                        all_vfx.add(Shockwave(px, py, PLAYER_SLAM, max_radius=150, rings=3))
                        for _ in range(3):
                            all_vfx.add(LightningBolt(px, py, 
                                                    px + random.randint(-60, 60),
                                                    py + random.randint(-60, 60),
                                                    PLAYER_SLAM, 12))
                
                if event.key == pygame.K_SPACE and dash_cooldown_timer == 0 and not is_dashing:
                    is_dashing = True
                    dash_timer = DASH_DURATION
                    dash_cooldown_timer = DASH_COOLDOWN
                    screen_shake = 8  # 15'ten 8'e
                    dash_particles_timer = 0
                    dash_frame_counter = 0
                    character_state = 'dashing'
                    
                    # MINIMAL Dash başlangıç efektleri
                    if DASH_SOUND: FX_CHANNEL.play(DASH_SOUND)
                    if not PERFORMANCE_MODE:
                        all_vfx.add(ScreenFlash(CURRENT_THEME["border_color"], 60, 6))
                        all_vfx.add(Shockwave(px, py, CURRENT_THEME["border_color"], 
                                            max_radius=100, rings=2))
                    
                    # SADECE 2 şimşek
                    for _ in range(2):
                        end_x = px + random.randint(-60, 60)
                        end_y = py + random.randint(-60, 60)
                        all_vfx.add(LightningBolt(px, py, end_x, end_y, 
                                                CURRENT_THEME["border_color"], 10))
                    
                    keys = pygame.key.get_pressed()
                    dx = (keys[pygame.K_d] - keys[pygame.K_a]); dy = (keys[pygame.K_s] - keys[pygame.K_w])
                    if dx == 0 and dy == 0: dx = 1
                    mag = math.sqrt(dx*dx + dy*dy)
                    dash_vx, dash_vy = (dx/mag)*DASH_SPEED, (dy/mag)*DASH_SPEED
                    is_jumping = True; y_velocity = 0
                    
                    dash_angle = math.atan2(dash_vy, dash_vx)

    if GAME_STATE == 'PLAYING':
        camera_speed = min(MAX_CAMERA_SPEED, camera_speed + SPEED_INCREMENT_RATE)
        score += 0.1 * camera_speed
        
        # FIX: Old Y'yi burada saklıyoruz, collision için kritik
        old_x, old_y = player_x, player_y
        
        keys = pygame.key.get_pressed()
        horizontal_move = keys[pygame.K_d] - keys[pygame.K_a]
        if horizontal_move != 0 and not is_dashing and not is_slamming:
            character_state = 'running'
        elif not is_jumping and not is_dashing and not is_slamming:
            character_state = 'idle'
        
        is_grounded = not is_jumping and not is_slamming and not is_dashing
        character_animator.update(dt, character_state, is_grounded, y_velocity, is_dashing, is_slamming)
        
        # Trail efektleri (SEYREK)
        last_trail_time += 1
        if last_trail_time >= TRAIL_INTERVAL and (is_dashing or is_slamming):
            last_trail_time = 0
            trail_color = CURRENT_THEME["player_color"]
            if is_dashing:
                trail_color = CURRENT_THEME["border_color"]
                trail_size = random.randint(6, 10)
            elif is_slamming:
                trail_color = PLAYER_SLAM
                trail_size = random.randint(8, 12)
            
            trail_effects.append(TrailEffect(
                player_x + 15, player_y + 15,
                trail_color,
                trail_size,
                life=12
            ))
        
        if is_dashing:
            px, py = player_x + 15, player_y + 15
            dash_frame_counter += 1
            
            # Dash sırasında ÇOK AZ efekt
            if dash_frame_counter % 4 == 0 and not PERFORMANCE_MODE:  # Her 4 frame'de bir
                all_vfx.add(GhostTrail(px, py, CURRENT_THEME["border_color"], life=8, size=10))
            
            # WarpLine'lar SEYREK
            if dash_particles_timer > 0:
                dash_particles_timer -= 1
            else:
                dash_particles_timer = 6  # Çok seyrek
                
                # Sadece 1 WarpLine
                offset_x = random.randint(-5, 5)
                offset_y = random.randint(-5, 5)
                all_vfx.add(WarpLine(px + offset_x, py + offset_y, 
                                   dash_angle + random.uniform(-0.15, 0.15),
                                   CURRENT_THEME["border_color"],
                                   CURRENT_THEME["border_color"]))
            
            # SpeedLine SEYREK
            if dash_frame_counter % 8 == 0 and not PERFORMANCE_MODE:
                speed_line_angle = dash_angle + math.pi + random.uniform(-0.2, 0.2)
                all_vfx.add(SpeedLine(px, py, speed_line_angle, 
                                     random.uniform(6, 10), 
                                     CURRENT_THEME["border_color"]))
            
            # BASİT dash hareketi
            simple_dash_movement()
            
            # Kamera hareketini de ekle
            player_x -= camera_speed
            
            # Dash bitti mi?
            if dash_timer <= 0: 
                is_dashing = False
                y_velocity = 0
                character_state = 'idle'
            
        elif is_slamming and slam_stall_timer > 0:
            slam_stall_timer -= 1
            slam_collision_check_frames += 1
            
            # Havada asılı kalmada AZ efekt
            if not PERFORMANCE_MODE and slam_stall_timer % 3 == 0:
                for _ in range(2):
                    angle = random.uniform(0, math.pi * 2)
                    dist = random.randint(20, 40)
                    ex = player_x + 15 + math.cos(angle) * dist
                    ey = player_y + 15 + math.sin(angle) * dist
                    
                    spark = FlameSpark(ex, ey, angle + math.pi, 
                                     dist/10, PLAYER_SLAM, life=15, size=random.randint(4, 6))
                    all_vfx.add(spark)
            
            # Titreşim efekti (hafif)
            vibration = random.randint(-1, 1) if slam_stall_timer > 7 else 0
            player_x += vibration
            
            if slam_stall_timer == 7 and not PERFORMANCE_MODE:
                all_vfx.add(ParticleExplosion(player_x+15, player_y+15, PLAYER_SLAM, 15))
                for _ in range(2):
                    ring = Shockwave(player_x+15, player_y+15, (255, 180, 80))
                    ring.radius = 20
                    ring.max_radius = 120
                    all_vfx.add(ring)
            
            if slam_stall_timer == 0: 
                y_velocity = 30
                screen_shake = 12
                
                if not PERFORMANCE_MODE:
                    all_vfx.add(ParticleExplosion(player_x+15, player_y+15, PLAYER_SLAM, 12))
                    for _ in range(6):
                        angle = random.uniform(-math.pi/3, math.pi/3) + math.pi
                        speed = random.uniform(8, 18)
                        spark = FlameSpark(player_x+15, player_y+15, 
                                          angle, speed, PLAYER_SLAM, life=15, size=random.randint(3, 5))
                        all_vfx.add(spark)
        else:
            # Normal hareket
            player_x -= camera_speed
            if keys[pygame.K_a]: player_x -= PLAYER_SPEED
            if keys[pygame.K_d]: player_x += PLAYER_SPEED
            player_y += y_velocity
            
            if is_slamming:
                y_velocity += SLAM_GRAVITY * 1.8
            else:
                y_velocity += GRAVITY

        if dash_cooldown_timer > 0: dash_cooldown_timer -= 1
        if slam_cooldown > 0: slam_cooldown -= 1
        if screen_shake > 0: screen_shake -= 1
        
        # --- FIX: ÇARPIŞMA KONTROLÜ (GÜNCELLENDİ) ---
        if not is_dashing or not DASH_INVINCIBILITY:
            player_rect = pygame.Rect(player_x, player_y, 30, 30)
            
            # Platform çarpışma kontrolü
            for p in all_platforms:
                if player_rect.colliderect(p.rect):
                    # DÜZELTME BURADA:
                    # Eski kod sadece "if rect.top < p.rect.top" diyordu. Hızlı düşüşte karakter içine girince bu çalışmıyordu.
                    # Yeni mantık: Eğer aşağı düşüyorsak (y_velocity > 0) ve
                    # önceki pozisyonumuz platformun merkezinin üzerindeyse (tünelleme kontrolü)
                    # veya karakterin altı platformun tepesindeyse, bunu iniş olarak kabul et.
                    if y_velocity > 0 and (old_y + 30) <= p.rect.bottom:
                        player_y = p.rect.top - 30
                        
                        if is_slamming:
                            # Slam çarpışma - MINIMAL
                            y_velocity = -15
                            screen_shake = 30
                            
                            if not PERFORMANCE_MODE:
                                for i in range(2):
                                    wave = Shockwave(player_x+15, p.rect.top, (255, 180, 80))
                                    wave.radius = 30 + i*30
                                    wave.max_radius = 180 + i*60
                                    all_vfx.add(wave)
                                
                                all_vfx.add(ScreenFlash(PLAYER_SLAM, 100, 10))
                                all_vfx.add(ParticleExplosion(player_x+15, p.rect.top, PLAYER_SLAM, 25))
                            
                            is_slamming = False
                            is_jumping = True
                            jumps_left = MAX_JUMPS - 1
                            character_state = 'jumping'
                        else:
                            y_velocity = 0
                            is_jumping = False
                            is_slamming = False
                            jumps_left = MAX_JUMPS
                            character_state = 'idle'
                            
                            if not PERFORMANCE_MODE:
                                all_vfx.add(ParticleExplosion(player_x+15, player_y+30, 
                                                            CURRENT_THEME["player_color"], 8))
                        break

        # Güncellemeler
        all_platforms.update(camera_speed)
        for s in stars: s.update(camera_speed)
        all_vfx.update(camera_speed)
        
        for trail in trail_effects[:]:
            trail.update(camera_speed)
            if trail.life <= 0:
                trail_effects.remove(trail)
        
        # VFX SINIRI
        if len(all_vfx) > MAX_VFX_COUNT:
            sprites = list(all_vfx.sprites())
            for sprite in sprites[:30]:
                sprite.kill()
        
        # Yeni platform ekle
        if len(all_platforms) > 0 and max(p.rect.right for p in all_platforms) < SCREEN_WIDTH + 100: 
            add_new_platform()

        # Oyun bitti mi?
        if player_x < -50 or player_y > SCREEN_HEIGHT + 100:
            GAME_STATE = 'GAME_OVER'
            high_score = max(high_score, int(score))
            AMBIENT_CHANNEL.stop()

    # --- CIZIM ---
    render_offset = (random.randint(-screen_shake, screen_shake), 
                    random.randint(-screen_shake, screen_shake)) if screen_shake > 0 else (0,0)
    
    # Arkaplan
    screen.fill(CURRENT_THEME["bg_color"])
    for s in stars: s.draw(screen)
    
    # Geçici yüzey
    temp_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    
    # Platformlar
    for p in all_platforms: 
        p.draw(temp_surf, CURRENT_THEME)
    
    # VFX efektleri
    for v in all_vfx: 
        if hasattr(v, 'draw'): 
            v.draw(temp_surf)
    
    # Trail efektleri
    for trail in trail_effects:
        trail.draw(temp_surf)

    # Karakter
    if GAME_STATE in ('PLAYING', 'START', 'PAUSED', 'GAME_OVER') and GAME_STATE != 'GAME_OVER':
        p_color = CURRENT_THEME["player_color"]
        if is_dashing: 
            p_color = CURRENT_THEME["border_color"]
        elif is_slamming: 
            p_color = PLAYER_SLAM
        
        anim_params = character_animator.get_draw_params()
        modified_color = character_animator.get_modified_color(p_color)
        
        draw_animated_player(
            temp_surf, CURRENT_SHAPE, 
            player_x + 15, player_y + 15, 15,
            modified_color, anim_params
        )

    # Ekrana çiz
    screen.blit(temp_surf, render_offset)

    # --- UI ---
    ui_data = {
        'theme': CURRENT_THEME,
        'score': score,
        'high_score': high_score,
        'dash_cd': dash_cooldown_timer,
        'slam_cd': slam_cooldown,
        'time_ms': time_ms
    }
    
    render_ui(screen, GAME_STATE, ui_data)
    
    pygame.display.flip()
    clock.tick(FPS)
    
pygame.quit() 