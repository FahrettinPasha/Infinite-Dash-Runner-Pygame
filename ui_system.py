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
    # Her karede yüzey oluşturmak yerine doğrudan çiziyoruz
    # Yarı saydam arka plan için:
    # Pygame'de doğrudan rect çizimi alpha desteklemez (Surface hariç).
    # Bu yüzden küçük bir hile ile shape blending kullanabiliriz veya performans için solid renk kullanabiliriz.
    # Ancak UI kalitesi için burada bir kez küçük surface oluşturmak kabul edilebilir,
    # ya da main loop'ta oluşturulan ortak ui_layer'ı kullanırız.
    
    # Burada doğrudan 'surface' parametresine çiziyoruz. Bu surface alpha destekli olmalı.
    
    # Arkaplan (Yarı saydam siyah)
    pygame.draw.rect(surface, (0, 0, 0, 180), rect)
    
    # Çerçeve
    pygame.draw.rect(surface, color, rect, 2)
    
    # Koseleri vurgula
    corner_len = 20
    # Sol Ust
    pygame.draw.line(surface, WHITE, (rect.x, rect.y), (rect.x + corner_len, rect.y), 4)
    pygame.draw.line(surface, WHITE, (rect.x, rect.y), (rect.x, rect.y + corner_len), 4)
    # Sag Alt
    pygame.draw.line(surface, WHITE, (rect.right, rect.bottom), (rect.right - corner_len, rect.bottom), 4)
    pygame.draw.line(surface, WHITE, (rect.right, rect.bottom), (rect.right, rect.bottom - corner_len), 4)
    
    if title:
        draw_text(surface, title, 25, rect.x + 10, rect.y - 30, color)

def render_ui(surface, state, data):
    """Tum oyun arayuzunu duruma gore cizer"""
    # OPTİMİZASYON: Her frame'de yeni surface oluşturma!
    # Main.py'den gelen 'surface' zaten temizlenmiş bir katman olmalı.
    
    time_ms = data.get('time_ms', pygame.time.get_ticks())
    
    if state == 'START':
        # Yarı saydam siyah arka plan
        surface.fill((0, 0, 0, 230))
        
        # Tarama cizgileri (Optimize: Ekranın tamamını doldurmak yerine sadece görünür olanları çiz)
        # Ama burada draw.line çok maliyetli değil.
        for i in range(0, SCREEN_HEIGHT, 4): 
            pygame.draw.line(surface, (255, 255, 255, 5), (0, i), (SCREEN_WIDTH, i))
        
        draw_glitch_text(surface, "NEON RUNNER v2.5", 130, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 120, data['theme']["border_color"], 4)
        
        # Hareketli cerceve
        rect_w = 400 + math.sin(time_ms*0.01)*10
        pygame.draw.rect(surface, WHITE, (SCREEN_WIDTH//2 - rect_w//2, SCREEN_HEIGHT//2 + 20, rect_w, 60), 2)
        draw_text(surface, "PRESS ENTER TO INITIALIZE", 40, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 50, WHITE)
        
        # Bilgi Satirlari
        draw_text(surface, "> STATUS: SYSTEM READY", 25, 50, SCREEN_HEIGHT - 80, (0, 255, 100))
        draw_text(surface, "> LOG: UI_MODULES_STABLE", 25, 50, SCREEN_HEIGHT - 50, (0, 255, 100))

    elif state == 'PAUSED':
        surface.fill((0, 0, 15, 180))
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 300, SCREEN_HEIGHT//2 - 150, 600, 300)
        draw_cyber_panel(surface, panel_rect, (0, 180, 255), "SYSTEM SUSPENDED")
        draw_glitch_text(surface, "PAUSED", 100, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 30, WHITE)
        draw_text(surface, "PRESS 'P' TO RESUME EXECUTION", 35, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 60, (150, 150, 150))

    elif state == 'GAME_OVER':
        surface.fill((30, 0, 0, 240))
        for _ in range(5):
            y_pos = random.randint(0, SCREEN_HEIGHT)
            pygame.draw.line(surface, (255, 0, 0, 100), (0, y_pos), (SCREEN_WIDTH, y_pos), 1)
            
        draw_glitch_text(surface, "CRITICAL SYSTEM FAILURE", 90, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 140, (255, 50, 50), 6)
        
        panel_rect = pygame.Rect(SCREEN_WIDTH//2 - 250, SCREEN_HEIGHT//2 - 40, 500, 160)
        draw_cyber_panel(surface, panel_rect, (255, 50, 50), "DIAGNOSTICS")
        
        draw_text(surface, f"SCORE: {int(data['score'])}", 55, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 10, WHITE)
        draw_text(surface, f"HIGH SCORE: {data['high_score']}", 35, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 70, (0, 255, 255))
        
        if time_ms % 1000 < 500:
            draw_text(surface, "PRESS 'R' TO REBOOT", 45, SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 180, WHITE)

    elif state == 'PLAYING':
        # HUD Tasarimi - Doğrudan surface üzerine çiziliyor
        draw_cyber_panel(surface, pygame.Rect(40, 40, 240, 80), data['theme']["border_color"], "PLAYER_STATS")
        
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
        score_rect = pygame.Rect(SCREEN_WIDTH - 260, 40, 220, 60)
        draw_cyber_panel(surface, score_rect, WHITE, "DATA_STREAM")
        draw_text(surface, f"{int(data['score']):08d}", 45, SCREEN_WIDTH - 150, 70, WHITE)