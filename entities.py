import pygame
import random
from settings import *

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, surface, theme=None): # <--- Buraya theme=None ekledik
        # Varsayılan renkler (eğer tema gelmezse diye eski renkleri koruyoruz)
        fill_c = (10, 30, 10)  # Eski DARK_METAL
        border_c = (50, 255, 50) # Eski NEON_GREEN
        
        # Eğer bir tema yüklendiyse renkleri oradan çek
        if theme:
            fill_c = theme["platform_color"]
            border_c = theme["border_color"]

        # Çizim işlemleri
        pygame.draw.rect(surface, fill_c, self.rect, border_radius=5)
        pygame.draw.rect(surface, border_c, self.rect, 2, border_radius=5)
        # Platformun üstüne o parlak çizgiyi çekelim
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