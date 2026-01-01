import pygame
import random
import math
from settings import *
from utils import draw_text

def draw_glitch_text(surface, text, size, x, y, color, intensity=2):
    """Metne anlik kayma (glitch) efekti verir"""
    if random.random() < 0.1:
        off_x = random.randint(-intensity, intensity)
        off_y = random.randint(-intensity, intensity)
        draw_text(surface, text, size, x + off_x, y + off_y, (255, 0, 100)) # Kirmizi golge
        draw_text(surface, text, size, x - off_x, y - off_y, (0, 255, 255)) # Turkuaz golge
    draw_text(surface, text, size, x, y, color)

def draw_cyber_panel(surface, rect, color, title=""):
    """Siberpunk tasarimli cerceve cizer"""
    pygame.draw.rect(surface, (0, 0, 0, 180), rect)
    pygame.draw.rect(surface, color, rect, 2)
    
    # Koseleri vurgula
    corner_len = 20
    # Sol Ust
    pygame.draw.line(surface, WHITE, (rect.x, rect.y), (rect.x + corner_len, rect.y), 3)
    pygame.draw.line(surface, WHITE, (rect.x, rect.y), (rect.x, rect.y + corner_len), 3)
    # Sag Alt
    pygame.draw.line(surface, WHITE, (rect.right, rect.bottom), (rect.right - corner_len, rect.bottom), 3)
    pygame.draw.line(surface, WHITE, (rect.right, rect.bottom), (rect.right, rect.bottom - corner_len), 3)
    
    if title:
        # Title background
        title_rect = pygame.Rect(rect.x, rect.y - 30, len(title)*15 + 20, 30)
        pygame.draw.rect(surface, color, title_rect)
        draw_text(surface, title, 25, rect.x + 10, rect.y - 25, (0,0,0), center=False)

def draw_button(surface, rect, text, is_hovered, color_theme=BUTTON_COLOR):
    """Etkileşimli buton çizer"""
    color = BUTTON_HOVER_COLOR if is_hovered else color_theme
    border = WHITE if is_hovered else (100, 100, 100)
    
    # Hover animasyonu (hafif büyüme)
    draw_rect = rect.copy()
    if is_hovered:
        draw_rect.inflate_ip(4, 4)
        
    pygame.draw.rect(surface, color, draw_rect)
    pygame.draw.rect(surface, border, draw_rect, 2)
    
    # Dekoratif köşeler
    pygame.draw.line(surface, border, (draw_rect.left, draw_rect.bottom), (draw_rect.left + 10, draw_rect.bottom - 10), 2)
    
    text_col = WHITE if is_hovered else BUTTON_TEXT_COLOR
    draw_text(surface, text, 30, draw_rect.centerx, draw_rect.centery, text_col)

def render_main_menu(surface, mouse_pos, buttons):
    """Ana Menüyü Çizer"""
    w, h = surface.get_width(), surface.get_height()
    surface.fill(UI_BG_COLOR)
    
    # Arka plan ızgarası
    for i in range(0, w, 50):
        pygame.draw.line(surface, (255, 255, 255, 10), (i, 0), (i, h))
    for i in range(0, h, 50):
        pygame.draw.line(surface, (255, 255, 255, 10), (0, i), (w, i))

    draw_glitch_text(surface, "NEON RUNNER", 140, w//2, 150, UI_BORDER_COLOR, 5)
    draw_text(surface, "SYSTEM OVERRIDE: v3.1", 30, w//2, 230, (100, 200, 200))
    
    # Menü Kutusu
    menu_rect = pygame.Rect(w//2 - 200, 300, 400, 400)
    draw_cyber_panel(surface, menu_rect, UI_BORDER_COLOR, "MAIN_ACCESS")
    
    active_buttons = {}
    
    # Butonları çiz
    btn_start_rect = pygame.Rect(w//2 - 150, 350, 300, 60)
    is_hover = btn_start_rect.collidepoint(mouse_pos)
    draw_button(surface, btn_start_rect, "INITIALIZE SYSTEM", is_hover)
    active_buttons['start'] = btn_start_rect
    
    btn_settings_rect = pygame.Rect(w//2 - 150, 430, 300, 60)
    is_hover = btn_settings_rect.collidepoint(mouse_pos)
    draw_button(surface, btn_settings_rect, "CONFIGURATION", is_hover)
    active_buttons['settings'] = btn_settings_rect
    
    btn_exit_rect = pygame.Rect(w//2 - 150, 510, 300, 60)
    is_hover = btn_exit_rect.collidepoint(mouse_pos)
    draw_button(surface, btn_exit_rect, "TERMINATE", is_hover, (60, 0, 0))
    active_buttons['exit'] = btn_exit_rect
    
    return active_buttons

def render_settings_menu(surface, mouse_pos, settings_data):
    """Gelişmiş Ayarlar Menüsü"""
    w, h = surface.get_width(), surface.get_height()
    surface.fill(UI_BG_COLOR)
    
    draw_glitch_text(surface, "SYSTEM CONFIG", 80, w//2, 80, UI_BORDER_COLOR)
    
    # Panel boyutunu arttırdık ki daha çok ayar sığsın
    panel_rect = pygame.Rect(w//2 - 350, 150, 700, 550)
    draw_cyber_panel(surface, panel_rect, UI_BORDER_COLOR, "USER_PREFERENCES")
    
    active_buttons = {}
    
    current_y = 200
    spacing = 75
    btn_w = 600
    btn_x = w//2 - btn_w//2

    # 1. DISPLAY MODE (Fullscreen/Windowed)
    mode_text = "MODE: [FULLSCREEN]" if settings_data['fullscreen'] else "MODE: [WINDOWED]"
    mode_color = (0, 100, 0) if settings_data['fullscreen'] else (50, 50, 50)
    btn_mode = pygame.Rect(btn_x, current_y, btn_w, 60)
    draw_button(surface, btn_mode, mode_text, btn_mode.collidepoint(mouse_pos), mode_color)
    active_buttons['toggle_fullscreen'] = btn_mode
    current_y += spacing

    # 2. RESOLUTION
    # settings_data'dan çözünürlük indexini alıp ekrana yazdıracağız
    res_idx = settings_data.get('res_index', 1) # Default 1 (1920x1080)
    res_tuple = AVAILABLE_RESOLUTIONS[res_idx]
    res_text = f"RESOLUTION: < {res_tuple[0]} x {res_tuple[1]} >"
    btn_res = pygame.Rect(btn_x, current_y, btn_w, 60)
    draw_button(surface, btn_res, res_text, btn_res.collidepoint(mouse_pos), (0, 50, 100))
    active_buttons['change_resolution'] = btn_res
    current_y += spacing

    # 3. FPS LIMIT
    fps_val = settings_data.get('fps_limit', 60)
    fps_text = f"MAX FPS: < {fps_val} >"
    btn_fps = pygame.Rect(btn_x, current_y, btn_w, 60)
    draw_button(surface, btn_fps, fps_text, btn_fps.collidepoint(mouse_pos), (100, 50, 0))
    active_buttons['change_fps'] = btn_fps
    current_y += spacing
    
    # 4. VFX QUALITY
    q_text = f"VFX QUALITY: [{settings_data['quality']}]"
    q_color = (0, 0, 100) if settings_data['quality'] == 'HIGH' else (50, 50, 0)
    btn_q = pygame.Rect(btn_x, current_y, btn_w, 60)
    draw_button(surface, btn_q, q_text, btn_q.collidepoint(mouse_pos), q_color)
    active_buttons['toggle_quality'] = btn_q
    current_y += spacing

    # 5. APPLY BUTTON (Özellikle çözünürlük değişimi için)
    btn_apply = pygame.Rect(btn_x + 100, current_y, btn_w - 200, 60)
    draw_button(surface, btn_apply, ">> APPLY SETTINGS <<", btn_apply.collidepoint(mouse_pos), (0, 150, 0))
    active_buttons['apply_changes'] = btn_apply
    current_y += spacing + 20

    # Back Button
    btn_back = pygame.Rect(w//2 - 150, current_y, 300, 60)
    draw_button(surface, btn_back, "< RETURN", btn_back.collidepoint(mouse_pos))
    active_buttons['back'] = btn_back
    
    return active_buttons

def render_loading_screen(surface, progress, logs):
    """Sahte yükleme ekranı"""
    w, h = surface.get_width(), surface.get_height()
    surface.fill((0, 0, 0))
    
    # Merkez Logo
    draw_glitch_text(surface, "SYSTEM LOADING", 60, w//2, h//2 - 100, WHITE, 2)
    
    # Bar Arkaplan
    bar_width = min(800, w - 100)
    bar_height = 20
    bar_x = w//2 - bar_width//2
    bar_y = h//2
    
    pygame.draw.rect(surface, LOADING_BAR_BG, (bar_x, bar_y, bar_width, bar_height))
    
    # Bar Dolumu
    fill_width = int(bar_width * progress)
    pygame.draw.rect(surface, LOADING_BAR_FILL, (bar_x, bar_y, fill_width, bar_height))
    
    # Parlama efekti
    if fill_width > 0:
        pygame.draw.rect(surface, (200, 255, 200), (bar_x + fill_width - 5, bar_y, 5, bar_height))
        
    # Yüzde
    draw_text(surface, f"{int(progress * 100)}%", 30, bar_x + bar_width + 40, bar_y + 10, WHITE)
    
    # Sahte Loglar
    log_y = bar_y + 50
    for i, log in enumerate(logs[-5:]): # Son 5 logu göster
        col = (0, 255, 0) if "DONE" in log or "OK" in log else (150, 200, 255)
        draw_text(surface, f"> {log}", 20, bar_x, log_y + i*25, col, center=False)

def render_ui(surface, state, data, mouse_pos=(0,0)):
    """Ana render yöneticisi"""
    time_ms = data.get('time_ms', pygame.time.get_ticks())
    w, h = surface.get_width(), surface.get_height()
    
    interactive_elements = {}

    if state == 'MENU':
        interactive_elements = render_main_menu(surface, mouse_pos, None)
    
    elif state == 'SETTINGS':
        interactive_elements = render_settings_menu(surface, mouse_pos, data['settings'])
        
    elif state == 'LOADING':
        render_loading_screen(surface, data['progress'], data['logs'])
        
    elif state == 'PAUSED':
        surface.fill(PAUSE_OVERLAY_COLOR)
        panel_rect = pygame.Rect(w//2 - 300, h//2 - 150, 600, 300)
        draw_cyber_panel(surface, panel_rect, (0, 180, 255), "SYSTEM SUSPENDED")
        draw_glitch_text(surface, "PAUSED", 100, w//2, h//2 - 30, WHITE)
        draw_text(surface, "PRESS 'P' TO RESUME", 35, w//2, h//2 + 60, (150, 150, 150))

    elif state == 'GAME_OVER':
        surface.fill((30, 0, 0, 240))
        draw_glitch_text(surface, "CRITICAL FAILURE", 90, w//2, h//2 - 140, (255, 50, 50), 6)
        
        panel_rect = pygame.Rect(w//2 - 250, h//2 - 40, 500, 160)
        draw_cyber_panel(surface, panel_rect, (255, 50, 50), "DIAGNOSTICS")
        
        draw_text(surface, f"SCORE: {int(data['score'])}", 55, w//2, h//2 + 10, WHITE)
        draw_text(surface, f"HIGH SCORE: {data['high_score']}", 35, w//2, h//2 + 70, (0, 255, 255))
        
        if time_ms % 1000 < 500:
            draw_text(surface, "PRESS 'R' TO REBOOT", 45, w//2, h//2 + 180, WHITE)

    elif state == 'PLAYING':
        # HUD
        draw_cyber_panel(surface, pygame.Rect(40, 40, 240, 80), data['theme']["border_color"], "STATUS")
        
        # Dash Bar
        d_fill = 200 * (1 - (data['dash_cd'] / DASH_COOLDOWN))
        pygame.draw.rect(surface, (50, 50, 50), (60, 75, 200, 10))
        pygame.draw.rect(surface, PLAYER_DASH, (60, 75, d_fill, 10))
        draw_text(surface, "DASH", 20, 60, 60, PLAYER_DASH)
        
        # Slam Bar
        s_fill = 200 * (1 - (data['slam_cd'] / 120))
        pygame.draw.rect(surface, (50, 50, 50), (60, 100, 200, 10))
        pygame.draw.rect(surface, PLAYER_SLAM, (60, 100, s_fill, 10))
        draw_text(surface, "SLAM", 20, 60, 85, PLAYER_SLAM)
        
        # Skor
        score_rect = pygame.Rect(w - 260, 40, 220, 60)
        draw_cyber_panel(surface, score_rect, WHITE, "DATA_STREAM")
        draw_text(surface, f"{int(data['score']):08d}", 45, w - 150, 70, WHITE)
    
    return interactive_elements