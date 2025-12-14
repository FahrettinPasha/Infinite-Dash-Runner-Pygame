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
pygame.display.set_caption("Infinite Runner - Futuristic High Speed (ESC to Exit)")

# Colors
DARK_BLUE = (10, 10, 50) 
WHITE = (255, 255, 255)
STAR_COLOR = (200, 200, 200)
NEON_GREEN = (50, 255, 50)
DARK_METAL = (10, 30, 10)

PLAYER_NORMAL = (0, 150, 255)
PLAYER_DASH = (255, 255, 0)
PLAYER_COOLDOWN = (50, 50, 50)
PAUSE_OVERLAY_COLOR = (10, 10, 10, 180) # Siyah, Yarı Saydam (Drawing Overlay için)

# Game Speed
clock = pygame.time.Clock()
FPS = 60
# Yeni Durum Eklendi: 'PAUSED'
GAME_STATE = 'START' 

# =========================================================
# AUDIO SYSTEM
# =========================================================

# Initialize Mixer
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.init()

SAMPLE_RATE = 44100
MASTER_VOLUME = 1.0 
AMBIENT_VOLUME = 1.0 
FX_VOLUME = 0.6

# Channels
AMBIENT_CHANNEL = pygame.mixer.Channel(0) # Music Channel
FX_CHANNEL = pygame.mixer.Channel(1)      # Effect Channel

# --- PATH SETTINGS (CHANGE ONLY THESE PATHS TO ADD YOUR OWN MUSIC) ---
MENU_MUSIC_PATH = "assets/music/menu_theme.ogg"   
GAME_MUSIC_PATH = "assets/music/game_action_music.ogg" 
GAMEOVER_MUSIC_PATH = "assets/music/game_over.ogg"
JUMP_SFX_PATH = "assets/sfx/jump.wav"
DASH_SFX_PATH = "assets/sfx/dash.wav"

# --- FALLBACK SYNTHESIS FUNCTIONS (Used if the file is not found) ---

def generate_sound_effect(freq, duration_ms):
    """Generates a simple sound effect (Fallback)"""
    num_samples = int(SAMPLE_RATE * duration_ms / 1000)
    max_amp = 32767
    buffer = bytearray()
    for i in range(num_samples):
        t = i / num_samples
        amp_decay = 1 - t
        sample = int(
            max_amp * amp_decay * math.sin(2 * math.pi * freq * i / SAMPLE_RATE)
        )
        buffer += struct.pack('<hh', sample, sample)
    return pygame.mixer.Sound(buffer=buffer)


def generate_ambient_fallback():
    """Generates a soft ambient tone (Fallback)"""
    freq = 80
    duration = 4.0
    total_samples = int(SAMPLE_RATE * duration)
    max_amp = 20000
    buffer = bytearray()
    for i in range(total_samples):
        t = i / total_samples
        fade = min(t * 10, 1, (1 - t) * 10) 
        sample = int(
            max_amp * fade * math.sin(2 * math.pi * freq * i / SAMPLE_RATE)
        )
        buffer += struct.pack('<hh', sample, sample)
    return pygame.mixer.Sound(buffer=buffer)

# --- LOADING LOGIC ---

def load_sound_asset(filepath, fallback_func, volume):
    """
    Attempts to load the file. 
    If it FAILS (always fails in this environment), returns the fallback sound.
    """
    sound = None
    
    try:
        sound = pygame.mixer.Sound(filepath)
        print(f"INFO: '{filepath}' successfully loaded from file.")
    except (pygame.error, FileNotFoundError, OSError):
        sound = fallback_func()
        print(f"WARNING: '{filepath}' file not found, synthesized sound used.")
        
    if sound:
        sound.set_volume(volume)
    return sound

# --- INITIALIZE AUDIO ASSETS ---
JUMP_SOUND = load_sound_asset(JUMP_SFX_PATH, lambda: generate_sound_effect(350, 90), FX_VOLUME * MASTER_VOLUME * 0.9)
DASH_SOUND = load_sound_asset(DASH_SFX_PATH, lambda: generate_sound_effect(700, 60), FX_VOLUME * MASTER_VOLUME * 1.1)

# MUSIC LOADING:
GAME_MUSIC = load_sound_asset(GAME_MUSIC_PATH, generate_ambient_fallback, AMBIENT_VOLUME * MASTER_VOLUME)
MENU_MUSIC = load_sound_asset(MENU_MUSIC_PATH, generate_ambient_fallback, AMBIENT_VOLUME * MASTER_VOLUME * 1.2)
GAMEOVER_MUSIC = load_sound_asset(GAMEOVER_MUSIC_PATH, lambda: generate_sound_effect(150, 500), FX_VOLUME * MASTER_VOLUME * 1.5) 

# --- SCORE SETTINGS ---
score = 0
score_multiplier = 0.1 
sound_feedback_timer = 0

# --- 2. PLAYER SETTINGS ---
player_size = 30
player_x = 150 
player_y = SCREEN_HEIGHT - 300 
player_speed = 10 
jump_power = 28  
gravity = 1
y_velocity = 0
is_jumping = False

# --- DASH SETTINGS ---
DASH_SPEED = 60         
DASH_DURATION = 8       
DASH_COOLDOWN = 60      

is_dashing = False      
dash_timer = 0          
dash_cooldown_timer = 0 
dash_vx = 0             
dash_vy = 0             

# --- 3. WORLD SETTINGS ---
INITIAL_CAMERA_SPEED = 5 
MAX_CAMERA_SPEED = 15    
SPEED_INCREMENT_RATE = 0.001 
CAMERA_SPEED = INITIAL_CAMERA_SPEED 
PLATFORM_MIN_WIDTH = 100
PLATFORM_MAX_WIDTH = 300

# Difficulty & Platform Heights
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
        # Platform drawing details
        pygame.draw.rect(surface, DARK_METAL, self.rect, border_radius=5)
        pygame.draw.rect(surface, NEON_GREEN, self.rect, 2, border_radius=5)
        pygame.draw.line(surface, NEON_GREEN, (self.rect.left, self.rect.top), (self.rect.right, self.rect.top), 3)

    def update(self):
        # Platform moves only when not paused
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
        # Stars move only when not paused
        self.x -= self.speed * CAMERA_SPEED / 3 
        if self.x < 0:
            self.x = SCREEN_WIDTH
            self.y = random.randrange(0, SCREEN_HEIGHT)
            
    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 1)
        pygame.draw.circle(surface, STAR_COLOR, (int(self.x), int(self.y)), self.size, 1)

stars = [Star() for _ in range(150)] 

all_platforms = pygame.sprite.Group()

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
    global is_dashing, dash_timer, dash_cooldown_timer, dash_vx, dash_vy, CAMERA_SPEED
    
    # --- START MUSIC (Game Music) ---
    AMBIENT_CHANNEL.stop()
    if GAME_MUSIC:
        AMBIENT_CHANNEL.set_volume(AMBIENT_VOLUME * MASTER_VOLUME) 
        AMBIENT_CHANNEL.play(GAME_MUSIC, loops=-1) 
    
    CAMERA_SPEED = INITIAL_CAMERA_SPEED
    
    player_x = 150
    player_y = SCREEN_HEIGHT - 300
    y_velocity = 0
    is_jumping = False
    score = 0
    
    is_dashing = False
    dash_timer = 0
    dash_cooldown_timer = 0
    dash_vx = 0
    dash_vy = 0
    
    all_platforms.empty()
    
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
                    AMBIENT_CHANNEL.pause() # Duraklatıldığında müziği de durdur
                elif GAME_STATE == 'PAUSED':
                    GAME_STATE = 'PLAYING'
                    AMBIENT_CHANNEL.unpause() # Devam ettiğinde müziği başlat
            # ---------------------------

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
        
        # --- DASH MECHANIC ---
        if keys[pygame.K_SPACE] and dash_cooldown_timer == 0 and not is_dashing:
            is_dashing = True
            dash_timer = DASH_DURATION
            dash_cooldown_timer = DASH_COOLDOWN
            
            if DASH_SOUND:
                FX_CHANNEL.play(DASH_SOUND)
            
            sound_feedback_timer = 30 

            input_x = 0
            input_y = 0
            
            # Check for WASD direction
            if keys[pygame.K_w]: input_y = -1  
            if keys[pygame.K_s]: input_y = 1   
            if keys[pygame.K_a]: input_x = -1  
            if keys[pygame.K_d]: input_x = 1   
            
            if input_x == 0 and input_y == 0:
                input_x = 1 # Default: Dash Right
            
            current_dash_speed = DASH_SPEED
            # Normalize diagonal speed
            if input_x != 0 and input_y != 0:
                current_dash_speed = DASH_SPEED * 0.707 
            
            dash_vx = input_x * current_dash_speed
            dash_vy = input_y * current_dash_speed
        
        # --- MOVEMENT LOGIC ---
        if is_dashing:
            player_x += dash_vx
            player_y += dash_vy
            
            dash_timer -= 1
            if dash_timer <= 0:
                is_dashing = False 
                y_velocity = 0     
        else:
            # Automatic horizontal movement (against camera speed)
            player_x -= CAMERA_SPEED 

            # Horizontal player control
            if keys[pygame.K_a]:
                player_x -= player_speed
            if keys[pygame.K_d]:
                player_x += player_speed
            
            # Jump
            if keys[pygame.K_w] and not is_jumping:
                is_jumping = True
                y_velocity = -jump_power
                if JUMP_SOUND:
                    FX_CHANNEL.play(JUMP_SOUND)
                sound_feedback_timer = 30 
            
            # Apply gravity
            if is_jumping or y_velocity != 0:
                player_y += y_velocity
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
                # Check for collision from above
                if player_rect.bottom - y_velocity <= platform.rect.top + 15:
                    player_y = platform.rect.top - player_size
                    y_velocity = 0
                    is_jumping = False
                    on_platform = True
                    break
        
        # If not standing on a platform and not dashing, start falling
        if not on_platform and y_velocity == 0 and not is_jumping and not is_dashing:
            is_jumping = True

        # --- WORLD UPDATE ---
        all_platforms.update()
        for star in stars:
            star.update()

        # Platform generation check
        if len(all_platforms) > 0:
            rightmost_edge = max(p.rect.right for p in all_platforms)
            if rightmost_edge < SCREEN_WIDTH + 100:
                add_new_platform()
        else:
            add_new_platform(SCREEN_WIDTH)

        # --- DEATH CONDITION ---
        if player_x < 0 or player_y > SCREEN_HEIGHT:
            GAME_STATE = 'GAME_OVER'

    # --- DRAWING ---
    screen.fill(DARK_BLUE)
    
    # Draw all elements regardless of state (so pause screen shows the game world)
    for star in stars:
        star.draw(screen)

    for platform in all_platforms:
        platform.draw(screen)
    
    # Draw player if in PLAYING or PAUSED state
    if GAME_STATE in ('PLAYING', 'PAUSED'):
        player_rect = pygame.Rect(player_x, player_y, player_size, player_size)
        
        if is_dashing and GAME_STATE == 'PLAYING': # Only show dash color if actively dashing and playing
            player_color = PLAYER_DASH
        elif dash_cooldown_timer > 0:
            player_color = PLAYER_COOLDOWN
        else:
            player_color = PLAYER_NORMAL
            
        pygame.draw.circle(screen, player_color, player_rect.center, player_size // 2)
        pygame.draw.circle(screen, WHITE, player_rect.center, player_size // 2, 2)
    
    # --- UI (User Interface) ---
    if GAME_STATE == 'PLAYING':
        draw_text(screen, f"SCORE: {int(score)}", 40, SCREEN_WIDTH // 2, 20, WHITE, center=True)

        if dash_cooldown_timer > 0:
             draw_text(screen, f"DASH CHARGING ({dash_cooldown_timer/60:.1f})", 32, SCREEN_WIDTH // 2, 80, PLAYER_COOLDOWN)
        else:
             draw_text(screen, "DASH READY! (SPACE)", 32, SCREEN_WIDTH // 2, 80, PLAYER_NORMAL)
        
        # Display pause hint
        draw_text(screen, "[P] to Pause", 32, SCREEN_WIDTH - 150, 40, WHITE)

    # --- PAUSED SCREEN ---
    elif GAME_STATE == 'PAUSED':
        # Create a semi-transparent surface for the overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY_COLOR) 
        screen.blit(overlay, (0, 0))

        draw_text(screen, "PAUSED", 120, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, NEON_GREEN)
        draw_text(screen, "Press [P] to Resume", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, WHITE)
        draw_text(screen, f"Current Score: {int(score)}", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150, STAR_COLOR)

    elif GAME_STATE == 'START':
        draw_text(screen, "MUSIC-FOCUSED DASH RUNNER", 80, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150, (0, 255, 150))
        draw_text(screen, "Change PATH variables in code to add your own music.", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, WHITE)
        draw_text(screen, "PRESS RETURN (ENTER) TO START", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150, PLAYER_NORMAL)

        
    elif GAME_STATE == 'GAME_OVER':
        draw_text(screen, "GAME OVER", 100, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100, (255, 50, 50))
        draw_text(screen, f"FINAL SCORE: {int(score)}", 50, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50, WHITE)
        draw_text(screen, "Press [R] to Restart", 40, SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 150, WHITE)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()