import pygame

# Ekran Ayarları (Varsayılan Başlangıç)
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

# --- YENİ EKLENEN AYAR SEÇENEKLERİ ---
AVAILABLE_RESOLUTIONS = [
    (3840, 2160), # 4K
    (1920, 1080), # FHD
    (1280, 720),  # HD
    (854, 480)    # 480p
]

FPS_LIMITS = [30, 60, 120, 144, 240]

# Renkler
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

# --- YENİ DÜŞMAN RENKLERİ ---
CURSED_PURPLE = (120, 0, 120)  # Lanetli Mor
CURSED_RED = (200, 0, 0)       # Göz Rengi
GLITCH_BLACK = (20, 0, 20)     # Karartı

# Oyun Fiziği
GRAVITY = 1
SLAM_GRAVITY = 5
JUMP_POWER = 28
PLAYER_SPEED = 10
MAX_JUMPS = 2

# Dash Ayarları
DASH_SPEED = 60
DASH_DURATION = 8
DASH_COOLDOWN = 60

# Kamera ve Dünya
INITIAL_CAMERA_SPEED = 5
MAX_CAMERA_SPEED = 15
SPEED_INCREMENT_RATE = 0.001
PLATFORM_MIN_WIDTH = 100
PLATFORM_MAX_WIDTH = 300
GAP_MIN = 120
GAP_MAX = 250
VERTICAL_GAP = 180

PLATFORM_HEIGHTS = [
    SCREEN_HEIGHT - 50,
    SCREEN_HEIGHT - 50 - VERTICAL_GAP,
    SCREEN_HEIGHT - 50 - 2 * VERTICAL_GAP,
    SCREEN_HEIGHT - 50 - 3 * VERTICAL_GAP]
THEMES = [
    {
        "name": "NEON NIGHTS",
        "bg_color": (10, 10, 50),        # Koyu Mavi Arkaplan
        "platform_color": (0, 0, 0),     # Siyah Platform İçi
        "border_color": (50, 255, 50),   # Neon Yeşil Çizgiler
        "player_color": (0, 255, 255),   # Camgöbeği Karakter
        "grid_color": (20, 20, 80)
    },
    {
        "name": "CRIMSON FURY",
        "bg_color": (40, 5, 5),          # Koyu Kırmızı Arkaplan
        "platform_color": (20, 0, 0),
        "border_color": (255, 50, 0),    # Turuncu/Kırmızı Çizgiler
        "player_color": (255, 200, 0),   # Sarı Karakter
        "grid_color": (80, 20, 20)
    },
    {
        "name": "MONOCHROME",
        "bg_color": (10, 10, 10),        # Siyah Arkaplan
        "platform_color": (255, 255, 255), # Beyaz Platform
        "border_color": (100, 100, 100), # Gri Çizgiler
        "player_color": (0, 0, 0),       # Siyah Karakter (Ters renk)
        "player_border": (255, 255, 255),
        "grid_color": (40, 40, 40)
    },
    {
        "name": "TOXIC WASTE",
        "bg_color": (10, 30, 10),        # Koyu Yeşil Arkaplan
        "platform_color": (0, 20, 0),
        "border_color": (180, 0, 255),   # Mor Çizgiler (Joker teması gibi)
        "player_color": (50, 255, 50),   # Yeşil Karakter
        "grid_color": (20, 60, 20)
    }
]

# Karakter şekilleri
PLAYER_SHAPES = ['circle', 'square', 'triangle', 'hexagon']