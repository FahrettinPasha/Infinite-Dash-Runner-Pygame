import pygame

# --- EKRAN AYARLARI ---
# Oyunun mantıksal olarak çalıştığı sabit çözünürlük
# Tüm koordinatlar (platform yerleri, karakter hızı vb.) buna göre hesaplanır.
LOGICAL_WIDTH = 1920
LOGICAL_HEIGHT = 1080

# Başlangıç Pencere Boyutu
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# --- RENDER ÇÖZÜNÜRLÜKLERİ (Görüntü Kalitesi Seçenekleri) ---
# Menüde seçilen çözünürlük artık pencere boyutunu değil, 
# "içerik kalitesini" değiştirecek.
AVAILABLE_RESOLUTIONS = [
    (3840, 2160), # 4K (Ultra Sharp)
    (1920, 1080), # FHD (Native)
    (1280, 720),  # HD (Soft)
    (854, 480),   # 480p (Pixelated/Blurry)
    (640, 360)    # 360p (Retro/Bad Signal)
]

FPS_LIMITS = [30, 60, 120, 144, 240]

# --- RENKLER ---
DARK_BLUE = (10, 10, 50)
WHITE = (255, 255, 255)
STAR_COLOR = (200, 200, 200)
NEON_GREEN = (50, 255, 50)
DARK_METAL = (10, 30, 10)

PLAYER_NORMAL = (0, 150, 255)
PLAYER_DASH = (255, 200, 0)
PLAYER_COOLDOWN = (50, 50, 50)
PLAYER_SLAM = (255, 0, 0)
PAUSE_OVERLAY_COLOR = (10, 10, 10, 180)

# --- UI COLORS ---
UI_BG_COLOR = (5, 5, 10, 230)
UI_BORDER_COLOR = (0, 255, 255)
BUTTON_COLOR = (0, 20, 40)
BUTTON_HOVER_COLOR = (0, 100, 150)
BUTTON_TEXT_COLOR = (200, 255, 255)
LOADING_BAR_BG = (20, 20, 20)
LOADING_BAR_FILL = (0, 255, 128)

# --- DÜŞMAN RENKLERİ ---
CURSED_PURPLE = (120, 0, 120)
CURSED_RED = (200, 0, 0)
GLITCH_BLACK = (20, 0, 20)

# --- OYUN FİZİĞİ ---
GRAVITY = 1
SLAM_GRAVITY = 5
JUMP_POWER = 28
PLAYER_SPEED = 10
MAX_JUMPS = 2

# --- DASH AYARLARI ---
DASH_SPEED = 60
DASH_DURATION = 8
DASH_COOLDOWN = 60

# --- KAMERA VE DÜNYA ---
INITIAL_CAMERA_SPEED = 5
MAX_CAMERA_SPEED = 15
SPEED_INCREMENT_RATE = 0.001
PLATFORM_MIN_WIDTH = 100
PLATFORM_MAX_WIDTH = 300
GAP_MIN = 120
GAP_MAX = 250
VERTICAL_GAP = 180

PLATFORM_HEIGHTS = [
    LOGICAL_HEIGHT - 50,
    LOGICAL_HEIGHT - 50 - VERTICAL_GAP,
    LOGICAL_HEIGHT - 50 - 2 * VERTICAL_GAP,
    LOGICAL_HEIGHT - 50 - 3 * VERTICAL_GAP]

THEMES = [
    {
        "name": "NEON NIGHTS",
        "bg_color": (10, 10, 50),
        "platform_color": (0, 0, 0),
        "border_color": (50, 255, 50),
        "player_color": (0, 255, 255),
        "grid_color": (20, 20, 80)
    },
    {
        "name": "CRIMSON FURY",
        "bg_color": (40, 5, 5),
        "platform_color": (20, 0, 0),
        "border_color": (255, 50, 0),
        "player_color": (255, 200, 0),
        "grid_color": (80, 20, 20)
    },
    {
        "name": "MONOCHROME",
        "bg_color": (10, 10, 10),
        "platform_color": (255, 255, 255),
        "border_color": (100, 100, 100),
        "player_color": (0, 0, 0),
        "player_border": (255, 255, 255),
        "grid_color": (40, 40, 40)
    },
    {
        "name": "TOXIC WASTE",
        "bg_color": (10, 30, 10),
        "platform_color": (0, 20, 0),
        "border_color": (180, 0, 255),
        "player_color": (50, 255, 50),
        "grid_color": (20, 60, 20)
    }
]

PLAYER_SHAPES = ['circle', 'square', 'triangle', 'hexagon']