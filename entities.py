import pygame
import random
import math
from settings import *

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, theme=None):
        # Varsayılan renkler
        fill_c = (10, 30, 10)
        border_c = (50, 255, 50)
        
        if theme:
            fill_c = theme["platform_color"]
            border_c = theme["border_color"]

        pygame.draw.rect(surface, fill_c, self.rect, border_radius=5)
        pygame.draw.rect(surface, border_c, self.rect, 2, border_radius=5)
        pygame.draw.line(surface, border_c, (self.rect.left, self.rect.top), (self.rect.right, self.rect.top), 3)
        
    def update(self, camera_speed):
        self.rect.x -= camera_speed
        if self.rect.right < 0:
            self.kill()

class Star:
    def __init__(self):
        self.x = random.randrange(0, SCREEN_WIDTH)
        self.y = random.randrange(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 1.5)

    def update(self, camera_speed):
        self.x -= self.speed * camera_speed / 3
        if self.x < 0:
            self.x = SCREEN_WIDTH
            self.y = random.randrange(0, SCREEN_HEIGHT)

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), 1)
        pygame.draw.circle(surface, STAR_COLOR, (int(self.x), int(self.y)), self.size, 1)

class CursedEnemy(pygame.sprite.Sprite):
    """Platform üzerinde gezinen, glitch efekti olan lanetli düşman"""
    def __init__(self, platform):
        super().__init__()
        self.platform = platform
        self.width = 40
        self.height = 40
        
        # Platformun üzerinde rastgele bir noktada başlat, ama düşmesin
        safe_x = random.randint(platform.rect.left, max(platform.rect.left, platform.rect.right - self.width))
        self.rect = pygame.Rect(safe_x, platform.rect.top - self.height, self.width, self.height)
        
        self.speed = 3
        self.direction = random.choice([-1, 1])
        self.timer = 0
        
    def update(self, camera_speed):
        # 1. Platformla beraber kayma
        self.rect.x -= camera_speed
        
        # 2. Platform üzerinde devriye gezme
        self.rect.x += self.speed * self.direction
        
        # Sınırlardan dönme mantığı
        if self.rect.right > self.platform.rect.right:
            self.direction = -1
            self.rect.right = self.platform.rect.right
        elif self.rect.left < self.platform.rect.left:
            self.direction = 1
            self.rect.left = self.platform.rect.left
            
        # Ekrandan çıkarsa sil
        if self.rect.right < 0:
            self.kill()
            
        self.timer += 1

    def draw(self, surface):
        # Glitch Efekti: Sürekli titreyen ve boyutu değişen çizim
        jitter_x = random.randint(-3, 3)
        jitter_y = random.randint(-3, 3)
        
        draw_rect = pygame.Rect(self.rect.x + jitter_x, self.rect.y + jitter_y, self.rect.width, self.rect.height)
        
        # Ana Gövde (Lanetli Mor)
        pygame.draw.rect(surface, CURSED_PURPLE, draw_rect)
        
        # İç parazit (Siyah çizgiler)
        for _ in range(3):
            lx = random.randint(draw_rect.left, draw_rect.right)
            pygame.draw.line(surface, GLITCH_BLACK, (lx, draw_rect.top), (lx, draw_rect.bottom), 2)
            
        # Gözler (Kırmızı ve korkutucu)
        eye_offset = math.sin(self.timer * 0.2) * 2
        pygame.draw.rect(surface, CURSED_RED, (draw_rect.x + 8, draw_rect.y + 10 + eye_offset, 8, 8))
        pygame.draw.rect(surface, CURSED_RED, (draw_rect.x + 24, draw_rect.y + 10 - eye_offset, 8, 8))
        
        # Etrafa yayılan 'Corruption' (Bozulma) partikülleri
        if random.random() < 0.3:
            px = draw_rect.x + random.randint(-10, self.width + 10)
            py = draw_rect.y + random.randint(-10, self.height + 10)
            pygame.draw.rect(surface, CURSED_PURPLE, (px, py, 4, 4))