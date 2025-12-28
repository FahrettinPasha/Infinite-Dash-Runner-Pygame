import pygame
import math
import struct
import random
import os
import sys

SAMPLE_RATE = 44100

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def generate_sound_effect(freq, duration_ms, decay=1.0):
    num_samples = int(SAMPLE_RATE * duration_ms / 1000)
    max_amp = 32767
    buffer = bytearray()
    for i in range(num_samples):
        t = i / num_samples
        sample = int(max_amp * (1 - t) * decay * math.sin(2 * math.pi * freq * i / SAMPLE_RATE))
        buffer += struct.pack('<hh', sample, sample)
    return pygame.mixer.Sound(buffer=buffer)

def generate_ambient_fallback():
    return generate_sound_effect(100, 1000)

def load_sound_asset(filepath, fallback_func, volume):
    try:
        s = pygame.mixer.Sound(resource_path(filepath))
    except:
        s = fallback_func()
    s.set_volume(volume)
    return s

def draw_text(surface, text, size, x, y, color=(255, 255, 255), center=True):
    font = pygame.font.Font(None, int(size * 1.5))
    s = font.render(text, True, color)
    r = s.get_rect()
    if center: r.center = (x, y)
    else: r.topleft = (x, y)
    surface.blit(s, r)

def draw_player_shape(surface, shape_type, x, y, size, color, rotation_angle=0, 
                     squash=1.0, stretch=1.0, scale=1.0, frame_index=0):
    """Karakteri seçilen şekle göre çizer - Animasyonlu versiyon"""
    # Güvenlik kontrolleri
    if size <= 0:
        size = 1
    if squash <= 0:
        squash = 0.1
    if stretch <= 0:
        stretch = 0.1
    if scale <= 0:
        scale = 0.1
    
    center = (int(x), int(y))
    anim_size = max(1, size * scale)
    
    # Animasyonlu boyutlar
    width = max(2, anim_size * 2 * squash)
    height = max(2, anim_size * 2 * stretch)
    
    # Renk güvenliği
    r, g, b = color
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))
    safe_color = (r, g, b)
    
    if shape_type == 'circle':
        # Animasyonlu daire/elips
        radius_x = max(1, int(width / 2))
        radius_y = max(1, int(height / 2))
        rect = pygame.Rect(0, 0, radius_x * 2, radius_y * 2)
        rect.center = center
        
        # Ana şekil
        pygame.draw.ellipse(surface, safe_color, rect)
        
        # Detaylar - frame bazlı animasyon
        if frame_index % 4 == 0:
            # Parlak nokta
            pygame.draw.circle(surface, (255, 255, 255), center, max(1, int(anim_size * 0.3)))
        elif frame_index % 4 == 1:
            # Yatay çizgi
            pygame.draw.line(surface, (255, 255, 255), 
                            (center[0] - radius_x//2, center[1]), 
                            (center[0] + radius_x//2, center[1]), 2)
        elif frame_index % 4 == 2:
            # Dikey çizgi
            pygame.draw.line(surface, (255, 255, 255), 
                            (center[0], center[1] - radius_y//2), 
                            (center[0], center[1] + radius_y//2), 2)
        
        # Kontür
        pygame.draw.ellipse(surface, (255, 255, 255), rect, 2)
        
    elif shape_type == 'square':
        # Animasyonlu kare/dikdörtgen
        rect = pygame.Rect(0, 0, max(2, width), max(2, height))
        rect.center = center
        
        # Dönüş uygula
        if abs(rotation_angle) > 0.01:
            # Yüzey oluştur ve döndür (güvenli boyut)
            surf_width = max(2, int(width))
            surf_height = max(2, int(height))
            temp_surf = pygame.Surface((surf_width, surf_height), pygame.SRCALPHA)
            pygame.draw.rect(temp_surf, safe_color, (0, 0, surf_width, surf_height))
            pygame.draw.rect(temp_surf, (255, 255, 255), (0, 0, surf_width, surf_height), 2)
            
            # Detaylar
            if frame_index % 4 == 0:
                pygame.draw.line(temp_surf, (255, 255, 200), 
                               (surf_width//2, 2), (surf_width//2, surf_height-2), 2)
            
            rotated = pygame.transform.rotate(temp_surf, math.degrees(rotation_angle))
            rot_rect = rotated.get_rect(center=center)
            surface.blit(rotated, rot_rect)
        else:
            pygame.draw.rect(surface, safe_color, rect)
            pygame.draw.rect(surface, (255, 255, 255), rect, 2)
            
            # Detaylar
            if frame_index % 4 == 0:
                pygame.draw.line(surface, (255, 255, 200), 
                               (center[0], rect.top + 2), 
                               (center[0], rect.bottom - 2), 2)
                               
    elif shape_type == 'triangle' or shape_type == 'hexagon':
        # Çokgen hesabı - animasyonlu
        points = []
        sides = 3 if shape_type == 'triangle' else 6
        
        # Frame bazlı şekil değişikliği
        shape_variation = 0.1 * math.sin(frame_index * 0.5)
        
        for i in range(sides):
            angle = rotation_angle + (2 * math.pi * i / sides) - math.pi / 2
            # Animasyon: bazı noktaları dışarı, bazılarını içeri çek
            radius_variation = max(0.5, 1.0 + shape_variation * math.sin(i * 1.5))
            px = x + math.cos(angle) * anim_size * radius_variation * squash
            py = y + math.sin(angle) * anim_size * radius_variation * stretch
            points.append((px, py))
        
        pygame.draw.polygon(surface, safe_color, points)
        
        # İç detaylar
        if shape_type == 'triangle':
            # Üçgenin içine küçük üçgen
            inner_points = []
            for i in range(sides):
                angle = rotation_angle + (2 * math.pi * i / sides) - math.pi / 2
                px = x + math.cos(angle) * anim_size * 0.5 * squash
                py = y + math.sin(angle) * anim_size * 0.5 * stretch
                inner_points.append((px, py))
            pygame.draw.polygon(surface, (255, 255, 200), inner_points)
        else:
            # Altıgenin merkezinde daire
            pygame.draw.circle(surface, (255, 255, 200), center, max(1, int(anim_size * 0.3)))
        
        pygame.draw.polygon(surface, (255, 255, 255), points, 2)

def draw_animated_player(surface, shape_type, x, y, size, color, anim_params):
    """Animasyon parametreleri ile karakter çiz"""
    # Renk güvenliği
    if len(color) == 3:
        r, g, b = color
        color_pulse = anim_params.get('color_pulse', 1.0)
        
        # Renk pulsasyonu uygula
        r = max(0, min(255, int(r * color_pulse)))
        g = max(0, min(255, int(g * color_pulse)))
        b = max(0, min(255, int(b * color_pulse)))
        
        modified_color = (r, g, b)
    else:
        modified_color = color
    
    # Animasyon parametrelerini al ve güvenli hale getir
    squash = max(0.1, anim_params.get('squash', 1.0))
    stretch = max(0.1, anim_params.get('stretch', 1.0))
    scale = max(0.1, anim_params.get('scale', 1.0))
    rotation = anim_params.get('rotation', 0)
    frame_index = anim_params.get('frame_index', 0)
    
    draw_player_shape(
        surface, shape_type, x, y, size,
        modified_color,
        rotation,
        squash,
        stretch,
        scale,
        frame_index
    )