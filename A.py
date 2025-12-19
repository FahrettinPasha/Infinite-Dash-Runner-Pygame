import pygame
import sys
import random
import math
import struct

# Initialize Pygame
pygame.init()

# --- 1. SETTINGS ---
# Screen dimensions
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Infinite Runner - MAXIMUM VFX (ESC to Exit)")

# Colors
DARK_BLUE = (10, 10, 50)
WHITE = (255, 255, 255)
STAR_COLOR = (200, 200, 200)
NEON_GREEN = (50, 255, 50)
DARK_METAL = (10, 30, 10)

PLAYER_NORMAL = (0, 150, 255)
PLAYER_DASH = (255, 200, 0) # Sarı/Altın (Dash ve Yüksek Enerji Rengi)
PLAYER_COOLDOWN = (50, 50, 50)
PLAYER_SLAM = (255, 0, 0)
PAUSE_OVERLAY_COLOR = (10, 10, 10, 180)

# Game Speed
clock = pygame.time.Clock()
FPS = 60
GAME_STATE = 'START'

# =========================================================
# AUDIO SYSTEM
# =========================================================

# Initialize Mixer
pygame.mixer.pre_init(44100, -16, 2, 512)
try:
    pygame.mixer.init()
except pygame.error as e:
    print(f"Mixer initialization failed: {e}")

SAMPLE_RATE = 44100
MASTER_VOLUME = 1.0
AMBIENT_VOLUME = 1.0
FX_VOLUME = 0.6

# Channels
AMBIENT_CHANNEL = pygame.mixer.Channel(0)
FX_CHANNEL = pygame.mixer.Channel(1)

# --- PATH SETTINGS (CHANGE ONLY THESE PATHS TO ADD YOUR OWN MUSIC) ---
MENU_MUSIC_PATH = "assets/music/menu_theme.ogg"
GAME_MUSIC_PATH = "assets/music/game_action_music.ogg"
GAMEOVER_MUSIC_PATH = "assets/music/game_over.ogg"
JUMP_SFX_PATH = "assets/sfx/jump.wav"
DASH_SFX_PATH = "assets/sfx/dash.wav"
SLAM_SFX_PATH = "assets/sfx/slam.wav"

def generate_sound_effect(freq, duration_ms, decay=1.0):
    num_samples = int(SAMPLE_RATE * duration_ms / 1000)
    max_amp = 32767
    buffer = bytearray()
    for i in range(num_samples):
        t = i / num_samples
        amp_decay = 1 - t
        sample = int(max_amp * amp_decay * decay * math.sin(2 * math.pi * freq * i / SAMPLE_RATE))
        buffer += struct.pack('<hh', sample, sample)
    return pygame.mixer.Sound(buffer=buffer)

def generate_ambient_fallback():
    freq = 80
    duration = 4.0
    total_samples = int(SAMPLE_RATE * duration)
    max_amp = 20000
    buffer = bytearray()
    for i in range(total_samples):
        t = i / total_samples
        fade = min(t * 10, 1, (1 - t) * 10)
        sample = int(max_amp * fade * math.sin(2 * math.pi * freq * i / SAMPLE_RATE))
        buffer += struct.pack('<hh', sample, sample)
    return pygame.mixer.Sound(buffer=buffer)

def load_sound_asset(filepath, fallback_func, volume):
    sound = None
    try:
        sound = pygame.mixer.Sound(filepath)
    except (pygame.error, FileNotFoundError, OSError):
        sound = fallback_func()

    if sound:
        sound.set_volume(volume)
    return sound

# --- INITIALIZE AUDIO ASSETS ---
JUMP_SOUND = load_sound_asset(JUMP_SFX_PATH, lambda: generate_sound_effect(350, 90), FX_VOLUME * MASTER_VOLUME * 0.9)
DASH_SOUND = load_sound_asset(DASH_SFX_PATH, lambda: generate_sound_effect(700, 60), FX_VOLUME * MASTER_VOLUME * 1.1)
SLAM_SOUND = load_sound_asset(SLAM_SFX_PATH, lambda: generate_sound_effect(100, 150, 0.7), FX_VOLUME * MASTER_VOLUME * 1.2)
GAME_MUSIC = load_sound_asset(GAME_MUSIC_PATH, generate_ambient_fallback, AMBIENT_VOLUME * MASTER_VOLUME)
MENU_MUSIC = load_sound_asset(MENU_MUSIC_PATH, generate_ambient_fallback, AMBIENT_VOLUME * MASTER_VOLUME * 1.2)
GAMEOVER_MUSIC = load_sound_asset(GAMEOVER_MUSIC_PATH, lambda: generate_sound_effect(150, 500), FX_VOLUME * MASTER_VOLUME * 1.5)

# --- SCORE SETTINGS ---
score = 0
score_multiplier = 0.1
sound_feedback_timer = 0

# --- 2. PLAYER SETTINGS & SKILLS ---
player_size = 30
player_x = 150
player_y = SCREEN_HEIGHT - 300
player_speed = 10
jump_power = 28
gravity = 1
y_velocity = 0
is_jumping = False

max_jumps = 2
jumps_left = max_jumps

DASH_SPEED = 60
DASH_DURATION = 8
DASH_COOLDOWN = 60
is_dashing = False
dash_timer = 0
dash_cooldown_timer = 0
dash_vx = 0
dash_vy = 0

SLAM_GRAVITY = 5
is_slamming = False

# --- 3. WORLD SETTINGS ---
INITIAL_CAMERA_SPEED = 5
MAX_CAMERA_SPEED = 15
SPEED_INCREMENT_RATE = 0.001
CAMERA_SPEED = INITIAL_CAMERA_SPEED
PLATFORM_MIN_WIDTH = 100
PLATFORM_MAX_WIDTH = 300

GAP_MIN = 120
GAP_MAX = 250
VERTICAL_GAP = 180

PLATFORM_HEIGHTS = [
    SCREEN_HEIGHT - 50,
    SCREEN_HEIGHT - 50 - VERTICAL_GAP,
    SCREEN_HEIGHT - 50 - 2 * VERTICAL_GAP,
    SCREEN_HEIGHT - 50 - 3 * VERTICAL_GAP
]

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface):
        pygame.draw.rect(surface, DARK_METAL, self.rect, border_radius=5)
        pygame.draw.rect(surface, NEON_GREEN, self.rect, 2, border_radius=5)
        pygame.draw.line(surface, NEON_GREEN, (self.rect.left, self.rect.top), (self.rect.right, self.rect.top), 3)

    def update(self):
        self.rect.x -= CAMERA_SPEED
        if self.rect.right < 0:
            self.kill()

# --- BACKGROUND STARS ---
class Star:
    def __init__(self):
        self.x = random.randrange(0, SCREEN_WIDTH)
        self.y = random.randrange(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 1.5)

    def update(self):
        self.x -= self.speed * CAMERA_SPEED / 3
        if self.x < 0:
            self.x = SCREEN_WIDTH
            self.y = random.randrange(0, SCREEN_HEIGHT)

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 1)
        pygame.draw.circle(surface, STAR_COLOR, (int(self.x), int(self.y)), self.size, 1)

stars = [Star() for _ in range(150)]
all_platforms = pygame.sprite.Group()

# =========================================================
# GELİŞTİRİLMİŞ EFEKT SINIFLARI (Hata Düzeltmeleri Dahil)
# =========================================================

class LightningBolt(pygame.sprite.Sprite):
    """Şimşek/Enerji Hattı Efekti."""
    def __init__(self, start_x, start_y, end_x, end_y, color, life=10, displace=10):
        super().__init__()
        self.color = color
        self.life = life
        self.initial_life = life
        self.alpha = 255
        self.segments = []
        self.vx = 0
        self.vy = 0
        self.create_bolt(start_x, start_y, end_x, end_y, displace)

    def create_bolt(self, x1, y1, x2, y2, displace):
        self.segments.append((x1, y1))
        dx, dy = x2 - x1, y2 - y1
        length = math.sqrt(dx**2 + dy**2)
        num_points = max(2, int(length / 10))

        if length < 0.01:
            self.segments.append((x2, y2))
            return

        perp_x = -dy / length
        perp_y = dx / length

        for i in range(1, num_points):
            t = i / num_points
            mid_x = x1 + t * dx
            mid_y = y1 + t * dy
            offset_factor = 1 - abs(t - 0.5) * 2
            offset = random.uniform(-displace, displace) * offset_factor
            jagged_x = mid_x + offset * perp_x
            jagged_y = mid_y + offset * perp_y
            self.segments.append((jagged_x, jagged_y))

        self.segments.append((x2, y2))


    def update(self):
        self.segments = [
            (x - CAMERA_SPEED + self.vx, y + self.vy)
            for x, y in self.segments
        ]
        self.vy += gravity * 0.1
        self.life -= 1

        # Hata Düzeltme: life değerini 0'ın altına düşürme
        life_ratio = max(0, self.life / self.initial_life)
        self.alpha = int(255 * life_ratio)

        if self.life <= 0:
            self.kill()

    def draw(self, surface):
        if self.life > 0 and len(self.segments) >= 2:
            r, g, b = self.color

            min_x = min(x for x, y in self.segments)
            max_x = max(x for x, y in self.segments)
            min_y = min(y for x, y in self.segments)
            max_y = max(y for x, y in self.segments)

            padding = 10
            width = max(10, int(max_x - min_x) + 2 * padding)
            height = max(10, int(max_y - min_y) + 2 * padding)

            temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))

            offset_points = [(x - min_x + padding, y - min_y + padding) for x, y in self.segments]

            # 1. Parlaklık/Glow (Yarı Saydam, Kalın Hat)
            glow_color = (r, g, b, int(self.alpha * 0.7))
            for i in range(len(offset_points) - 1):
                pygame.draw.line(temp_surface, glow_color, offset_points[i], offset_points[i+1], 6)

            # 2. Çekirdek/Core (Tam Saydam, İnce Hat)
            core_color = (r, g, b, self.alpha)
            for i in range(len(offset_points) - 1):
                pygame.draw.line(temp_surface, core_color, offset_points[i], offset_points[i+1], 2)

            screen.blit(temp_surface, (min_x - padding, min_y - padding))

class FlameSpark(pygame.sprite.Sprite):
    """Yüksek hızlı, kısa ömürlü, alev/kıvılcım gibi görünen parçacıklar."""
    def __init__(self, x, y, angle, speed, base_color, life=30, size=5):
        super().__init__()
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.base_color = base_color
        self.life = life
        self.initial_life = life
        self.initial_size = size
        self.size = size
        self.alpha = 255

    def update(self):
        self.x -= CAMERA_SPEED
        self.vy += gravity * 0.1

        self.x += self.vx
        self.y += self.vy

        self.vx *= 0.95
        self.vy *= 0.95

        self.life -= 1

        # Hata Düzeltme: Karmaşık sayı oluşumunu engellemek için oranı 0'da sınırla
        decay_ratio = max(0, self.life / self.initial_life)

        self.alpha = int(255 * decay_ratio)

        # Boyutu zamanla küçült (alev/kıvılcım sönmesi)
        self.size = max(1, int(self.initial_size * (decay_ratio)**0.5))

        if self.life <= 0:
            self.kill()

    def draw(self, surface):
        if self.life > 0:
            r, g, b = self.base_color

            draw_size = self.size * 4
            temp_surface = pygame.Surface((draw_size, draw_size), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))
            center = (draw_size // 2, draw_size // 2)

            # 1. Glow (Büyük, yarı saydam - Dış alev/duman)
            glow_size = self.size * 1.5
            glow_alpha = int(self.alpha * 0.2)
            glow_color = (r, g, b, glow_alpha)
            if glow_size > 0:
                pygame.draw.circle(temp_surface, glow_color, center, glow_size)

            # 2. Core (Orta, yarı saydam - Sıcak bölge)
            core_size = self.size * 1.0
            core_alpha = int(self.alpha * 0.6)
            core_color = (min(255, r + 50), min(255, g + 50), min(255, b + 50), core_alpha)
            if core_size > 0:
                pygame.draw.circle(temp_surface, core_color, center, core_size)

            # 3. Inner Core (Küçük, tam beyaz/sarı - En sıcak nokta)
            inner_size = self.size * 0.5
            inner_color = (255, 255, 200, self.alpha)
            if inner_size > 0:
                pygame.draw.circle(temp_surface, inner_color, center, inner_size)

            surface.blit(temp_surface, (int(self.x - draw_size / 2), int(self.y - draw_size / 2)))

all_vfx = pygame.sprite.Group()

# --- 4. PLATFORM GENERATION ---
def add_new_platform(start_x=None):
    if start_x is None:
        if len(all_platforms) > 0:
            rightmost_platform = max(all_platforms, key=lambda p: p.rect.right)
            gap = random.randint(GAP_MIN, GAP_MAX)
            start_x = rightmost_platform.rect.right + gap
        else:
            start_x = SCREEN_WIDTH

    width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)
    y = random.choice(PLATFORM_HEIGHTS)

    platform = Platform(start_x, y, width, 50)
    all_platforms.add(platform)

# --- 5. GAME START / RESET ---
def init_game():
    global player_x, player_y, y_velocity, is_jumping, score
    global is_dashing, dash_timer, dash_cooldown_timer, dash_vx, dash_vy
    global CAMERA_SPEED, jumps_left, is_slamming

    AMBIENT_CHANNEL.stop()
    if GAME_MUSIC:
        AMBIENT_CHANNEL.set_volume(AMBIENT_VOLUME * MASTER_VOLUME)
        AMBIENT_CHANNEL.play(GAME_MUSIC, loops=-1)

    CAMERA_SPEED = INITIAL_CAMERA_SPEED

    player_x = 150
    player_y = SCREEN_HEIGHT - 300
    y_velocity = 0
    is_jumping = False
    is_slamming = False
    jumps_left = max_jumps
    score = 0

    is_dashing = False
    dash_timer = 0
    dash_cooldown_timer = 0
    dash_vx = 0
    dash_vy = 0

    all_platforms.empty()
    all_vfx.empty()

    first_plat = Platform(0, SCREEN_HEIGHT - 50, 400, 50)
    all_platforms.add(first_plat)

    current_right_edge = 400
    while current_right_edge < SCREEN_WIDTH + 200:
        add_new_platform()
        current_right_edge = max(p.rect.right for p in all_platforms)


# Custom Function: Drawing Text
def draw_text(surface, text, size, x, y, color=WHITE, center=True):
    scaled_size = int(size * 1.5)
    font = pygame.font.Font(None, scaled_size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    if center:
        text_rect.center = (x, y)
    else:
        text_rect.topleft = (x, y)
    surface.blit(text_surface, text_rect)

# --- 6. GAME LOOP ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False

            # --- PAUSE TOGGLE (P key) ---
            if event.key == pygame.K_p and GAME_STATE in ('PLAYING', 'PAUSED'):
                if GAME_STATE == 'PLAYING':
                    GAME_STATE = 'PAUSED'
                    AMBIENT_CHANNEL.pause()
                elif GAME_STATE == 'PAUSED':
                    GAME_STATE = 'PLAYING'
                    AMBIENT_CHANNEL.unpause()

            if GAME_STATE == 'PLAYING':
                center_x = player_x + player_size // 2
                center_y = player_y + player_size // 2
                # --- DOUBLE JUMP (W key) ---
                if event.key == pygame.K_w and jumps_left > 0 and not is_dashing and not is_slamming:
                    jumps_left -= 1
                    is_jumping = True
                    y_velocity = -jump_power
                    if JUMP_SOUND:
                        FX_CHANNEL.play(JUMP_SOUND)

                    # Değişkenleri burada tanımlıyoruz ki aşağıdaki tüm efektler kullansın
                    center_x = player_x + player_size // 2
                    center_y = player_y + player_size // 2

                    # === ABARTILI JUMP EFEKTİ ===
                    spark_color = PLAYER_NORMAL if jumps_left > 0 else PLAYER_DASH

                    for _ in range(20):
                        angle = random.uniform(0.6 * math.pi, 1.4 * math.pi)
                        speed = random.uniform(6, 14)
                        particle = FlameSpark(
                            center_x, center_y,
                            angle, speed,
                            spark_color,
                            life=35,
                            size=random.randint(6, 9))
                        all_vfx.add(particle)

                    # LIGHTNING = BONUS (Hatanın olduğu kısım artık çalışacak)
                    for _ in range(8):
                        angle = random.uniform(0.6 * math.pi, 1.4 * math.pi)
                        length = random.uniform(50, 90)
                        # center_x ve center_y yukarıda tanımlandığı için hata vermeyecek
                        end_x = center_x + math.cos(angle) * length
                        end_y = center_y + math.sin(angle) * length
                        bolt = LightningBolt(
                                center_x, center_y,
                                end_x, end_y,
                                WHITE,
                                life=18,
                                displace=22)
                        all_vfx.add(bolt)

                    # =============================================================
                sound_feedback_timer = 30

                # --- SLAM (S key while jumping) ---
                if event.key == pygame.K_s and is_jumping and not is_dashing and not is_slamming:
                    is_slamming = True
                    y_velocity = 0
                    if SLAM_SOUND:
                        FX_CHANNEL.play(SLAM_SOUND)

                # --- DASH MECHANIC (SPACE key) ---
                if event.key == pygame.K_SPACE and dash_cooldown_timer == 0 and not is_dashing:
                    is_dashing = True
                    dash_timer = DASH_DURATION
                    dash_cooldown_timer = DASH_COOLDOWN

                    if DASH_SOUND:
                        FX_CHANNEL.play(DASH_SOUND)

                    sound_feedback_timer = 30

                    keys_state = pygame.key.get_pressed()
                    input_x = 0
                    input_y = 0

                    if keys_state[pygame.K_a]: input_x = -1
                    if keys_state[pygame.K_d]: input_x = 1
                    if keys_state[pygame.K_w]: input_y = -1
                    if keys_state[pygame.K_s]: input_y = 1

                    if input_x == 0 and input_y == 0:
                        input_x = 1

                    magnitude = math.sqrt(input_x**2 + input_y**2)

                    if magnitude > 0:
                        dash_vx = (input_x / magnitude) * DASH_SPEED
                        dash_vy = (input_y / magnitude) * DASH_SPEED
                    else:
                        dash_vx = DASH_SPEED
                        dash_vy = 0

                    is_jumping = True
                    y_velocity = 0

                    # === ABARTILI DASH BAŞLANGIÇ PATLAMA EFEKTİ ===
                    center_x = player_x + player_size // 2
                    center_y = player_y + player_size // 2

                    num_burst = 50
                    for i in range(num_burst):
                        angle = math.atan2(-dash_vy, -dash_vx) + random.uniform(-math.pi / 2, math.pi / 2)
                        speed = random.uniform(10, 25)

                        if i % 3 == 0:
                            end_x = center_x + math.cos(angle) * 40
                            end_y = center_y + math.sin(angle) * 40
                            vfx = LightningBolt(center_x, center_y, end_x, end_y, WHITE, life=15, displace=20)
                        else:
                            vfx = FlameSpark(center_x, center_y, angle, speed, PLAYER_DASH, life=35, size=random.randint(5, 8))

                        all_vfx.add(vfx)
                    # ==================================


        if GAME_STATE == 'START':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    init_game()
                    GAME_STATE = 'PLAYING'

        elif GAME_STATE == 'GAME_OVER':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    init_game()
                    GAME_STATE = 'PLAYING'

    # --- STATE TRANSITIONS AND MUSIC CONTROL ---

    if GAME_STATE == 'START':
        if MENU_MUSIC and (not AMBIENT_CHANNEL.get_busy() or AMBIENT_CHANNEL.get_sound() != MENU_MUSIC):
            AMBIENT_CHANNEL.set_volume(AMBIENT_VOLUME * MASTER_VOLUME)
            AMBIENT_CHANNEL.play(MENU_MUSIC, loops=-1)

    elif GAME_STATE == 'GAME_OVER':
        if GAMEOVER_MUSIC and AMBIENT_CHANNEL.get_sound() != GAMEOVER_MUSIC:
            AMBIENT_CHANNEL.stop()
            AMBIENT_CHANNEL.set_volume(FX_VOLUME * MASTER_VOLUME * 1.5)
            AMBIENT_CHANNEL.play(GAMEOVER_MUSIC, loops=0)
            sound_feedback_timer = 0

    # --- GAME LOGIC (Only runs in PLAYING state) ---
    if GAME_STATE == 'PLAYING':
        CAMERA_SPEED = min(MAX_CAMERA_SPEED, CAMERA_SPEED + SPEED_INCREMENT_RATE)

        keys = pygame.key.get_pressed()
        score += score_multiplier * CAMERA_SPEED

        # --- YENİ METEOR DASH TRAIL EFEKTİ (Işık Saçan Kuyruk) ---
        if is_dashing:
            center_x = player_x + player_size // 2
            center_y = player_y + player_size // 2

            # Dash yönünün tersi açısını hesapla (kuyruk geriye doğru uzayacak)
            dash_angle_opp = math.atan2(-dash_vy, -dash_vx)

            # 1. High-Speed, Long-Life Sparks (Ateşli Kuyruk)
            for _ in range(6):
                # Açıyı daralt (kuyruk düz ve akışkan olsun)
                angle = dash_angle_opp + random.uniform(-0.15, 0.15)
                # Hızı artır (uzun kuyruk hissi)
                speed = random.uniform(10, 15)

                particle = FlameSpark(
                    center_x, center_y, angle, speed,
                    PLAYER_DASH,
                    life=25, # Daha uzun ömür
                    size=random.randint(4, 7)
                )
                all_vfx.add(particle)

            # 2. Lightning Field (Yoğun, Çizgisel Enerji Alanı)
            for _ in range(4):
                # Açıyı biraz daha genişlet (hafif dalgalanma)
                angle = dash_angle_opp + random.uniform(-0.3, 0.3)

                # Bolt'u oyuncunun gerisine doğru uzat
                trail_length = random.uniform(40, 70)
                end_x = center_x + math.cos(angle) * trail_length
                end_y = center_y + math.sin(angle) * trail_length

                bolt = LightningBolt(
                    center_x, center_y, end_x, end_y,
                    WHITE, # Beyaz/Sarımsı ışık
                    life=8, # Orta ömür
                    displace=5 # Daha az dağınık (streaky)
                )
                all_vfx.add(bolt)

            # 3. Core Pulse (Oyuncunun kendisinden anlık parlama/çekirdek)
            if dash_timer % 2 == 0:
                core_pulse = FlameSpark(
                    center_x, center_y, 0, 0,
                    (255, 255, 255),
                    life=5, # Çok kısa ömür
                    size=12
                )
                all_vfx.add(core_pulse)

            # --- MOVEMENT LOGIC (Dash) ---
            player_x += dash_vx
            player_y += dash_vy

            dash_timer -= 1
            if dash_timer <= 0:
                is_dashing = False
                if dash_vy < 0:
                    y_velocity = dash_vy * 0.5
                else:
                    y_velocity = 0
                is_slamming = False
        else:
            # Normal hareket
            player_x -= CAMERA_SPEED

            if keys[pygame.K_a]:
                player_x -= player_speed
            if keys[pygame.K_d]:
                player_x += player_speed

            # Yerçekimi / Slam
            if is_jumping or y_velocity != 0 or is_slamming:
                player_y += y_velocity

                if is_slamming:
                    y_velocity += SLAM_GRAVITY
                    y_velocity = min(y_velocity, jump_power * 2)
                else:
                    y_velocity += gravity

        if dash_cooldown_timer > 0:
            dash_cooldown_timer -= 1

        if sound_feedback_timer > 0:
            sound_feedback_timer -= 1

        # --- COLLISION CHECK (Platform) ---
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        on_platform = False

        for platform in all_platforms:
            if player_rect.colliderect(platform.rect) and y_velocity >= 0:
                # Sadece üstten çarpışma kontrolü
                if player_rect.bottom - y_velocity <= platform.rect.top + 15:

                    # PLATFORM TEMAS EFEKTİ KALDIRILDI

                    player_y = platform.rect.top - player_size
                    y_velocity = 0
                    is_jumping = False
                    is_slamming = False
                    on_platform = True
                    jumps_left = max_jumps

                    break

        if not on_platform and y_velocity == 0 and not is_jumping and not is_dashing and not is_slamming:
            is_jumping = True

        # --- WORLD UPDATE ---
        all_platforms.update()
        for star in stars:
            star.update()

        all_vfx.update()

        # Platform generation check
        if len(all_platforms) > 0:
            rightmost_edge = max(p.rect.right for p in all_platforms)
            if rightmost_edge < SCREEN_WIDTH + 100:
                add_new_platform()
        else:
            add_new_platform(SCREEN_WIDTH)

        # --- DEATH CONDITION ---
        if player_x < 0 or player_y > SCREEN_HEIGHT + 100:
            GAME_STATE = 'GAME_OVER'

    # --- DRAWING ---
    screen.fill(DARK_BLUE)

    for star in stars:
        star.draw(screen)

    for platform in all_platforms:
        platform.draw(screen)

    # *** Şimşek/Alev Efektlerini Çiz ***
    for vfx in all_vfx:
        vfx.draw(screen)

    # Draw player
    if GAME_STATE in ('PLAYING', 'PAUSED'):
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)

        if is_dashing and GAME_STATE == 'PLAYING':
            player_color = PLAYER_DASH
        elif is_slamming and GAME_STATE == 'PLAYING':
            player_color = PLAYER_SLAM
        elif dash_cooldown_timer > 0:
            player_color = PLAYER_COOLDOWN
        elif jumps_left == 0 and GAME_STATE == 'PLAYING':
            player_color = PLAYER_DASH
        else:
            player_color = PLAYER_NORMAL

        pygame.draw.circle(screen, player_color, player_rect.center, player_size // 2)
        pygame.draw.circle(screen, WHITE, player_rect.center, player_size // 2, 2)

    # --- UI (User Interface) ---
    if GAME_STATE == 'PLAYING':
        draw_text(screen, f"SCORE: {int(score)}", 40, SCREEN_WIDTH // 2, 20, WHITE, center=True)

        # Dash UI
        if dash_cooldown_timer > 0:
             draw_text(screen, f"DASH ({dash_cooldown_timer/60:.1f}s)", 32, SCREEN_WIDTH // 2, 80, PLAYER_COOLDOWN)
        else:
             draw_text(screen, "DASH READY! (SPACE + WASD)", 32, SCREEN_WIDTH // 2, 80, PLAYER_DASH)

        draw_text(screen, "[W] Jump / Double Jump", 28, 120, 40, WHITE, center=False)
        draw_text(screen, "[S] Slam (Yere Çakıl)", 28, 120, 80, WHITE, center=False)

        draw_text(screen, "[P] Pause | [ESC] Exit", 28, SCREEN_WIDTH - 200, 40, WHITE)

    # --- PAUSED SCREEN ---
    elif GAME_STATE == 'PAUSED':
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY_COLOR)
        screen.blit(overlay, (0, 0))

        draw_text(screen, "PAUSED", 120, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, NEON_GREEN)
        draw_text(screen, "Press [P] to Resume", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, WHITE)
        draw_text(screen, f"Current Score: {int(score)}", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150, STAR_COLOR)

    elif GAME_STATE == 'START':
        draw_text(screen, "MUSIC-FOCUSED DASH RUNNER", 80, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150, (0, 255, 150))
        draw_text(screen, "Change PATH variables in code to add your own music.", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
        draw_text(screen, "CONTROLS: [W] Jump/Double Jump, [SPACE + WASD] 8 Yönlü Dash, [S] Slam", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, NEON_GREEN)
        draw_text(screen, "PRESS RETURN (ENTER) TO START", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150, PLAYER_NORMAL)


    elif GAME_STATE == 'GAME_OVER':
        draw_text(screen, "GAME OVER", 100, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, (255, 50, 50))
        draw_text(screen, f"FINAL SCORE: {int(score)}", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, WHITE)
        draw_text(screen, "Press [R] to Restart", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150, WHITE)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
