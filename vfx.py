import pygame
import random
import math
from settings import *

def draw_cyber_grid(surface, time_ms):
    """Menüdeki hareketli ızgarayı çizer."""
    grid_color = (15, 20, 70)
    grid_size = 50
    offset_y = (time_ms * 0.1) % grid_size
    
    # Dikey çizgiler
    for x in range(0, SCREEN_WIDTH, grid_size):
        pygame.draw.line(surface, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
    
    # Yatay (hareketli) çizgiler
    for y in range(0, SCREEN_HEIGHT + grid_size, grid_size):
        pygame.draw.line(surface, grid_color, (0, y + offset_y), (SCREEN_WIDTH, y + offset_y), 1)

class LightningBolt(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, end_x, end_y, color, life=15, displace=15):
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
        
        if length < 0.01:
            self.segments.append((x2, y2))
            return

        num_points = max(3, int(length / 8))
        perp_x, perp_y = -dy / length, dx / length

        for i in range(1, num_points):
            t = i / num_points
            mid_x, mid_y = x1 + t * dx, y1 + t * dy
            offset_factor = 1 - abs(t - 0.5) * 2
            offset = random.uniform(-displace, displace) * offset_factor
            jagged_x = mid_x + offset * perp_x
            jagged_y = mid_y + offset * perp_y
            self.segments.append((jagged_x, jagged_y))

        self.segments.append((x2, y2))

    def update(self, camera_speed):
        self.segments = [(x - camera_speed + self.vx, y + self.vy) for x, y in self.segments]
        self.vy += 0.5
        self.life -= 1
        
        life_ratio = max(0, self.life / self.initial_life)
        self.alpha = int(255 * life_ratio)
        
        if self.life <= 0: self.kill()

    def draw(self, surface):
        if self.life > 0 and len(self.segments) >= 2:
            r, g, b = self.color

            min_x = min(x for x, y in self.segments)
            max_x = max(x for x, y in self.segments)
            min_y = min(y for x, y in self.segments)
            max_y = max(y for x, y in self.segments)

            padding = 15
            width = max(15, int(max_x - min_x) + 2 * padding)
            height = max(15, int(max_y - min_y) + 2 * padding)

            temp_surface = pygame.Surface((width, height), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))

            offset_points = [(x - min_x + padding, y - min_y + padding) for x, y in self.segments]

            # 1. Dış Glow (Çok yarı saydam, kalın)
            glow_alpha = int(self.alpha * 0.4)
            for glow_size in [10, 8, 6]:
                glow_color = (r, g, b, glow_alpha // (glow_size // 2))
                if len(offset_points) >= 2:
                    pygame.draw.lines(temp_surface, glow_color, False, offset_points, glow_size)

            # 2. Orta Katman
            mid_alpha = int(self.alpha * 0.7)
            mid_color = (min(255, r+50), min(255, g+50), min(255, b+50), mid_alpha)
            if len(offset_points) >= 2:
                pygame.draw.lines(temp_surface, mid_color, False, offset_points, 5)

            # 3. Çekirdek (Parlak, ince)
            core_color = (255, 255, 255, self.alpha)
            if len(offset_points) >= 2:
                pygame.draw.lines(temp_surface, core_color, False, offset_points, 2)

            # 4. Titreşim efekti
            if random.random() < 0.3:
                offset_points_jitter = [(x + random.randint(-2, 2), y + random.randint(-2, 2)) 
                                      for x, y in offset_points]
                pygame.draw.lines(temp_surface, (255, 255, 255, self.alpha//2), 
                                False, offset_points_jitter, 1)

            surface.blit(temp_surface, (min_x - padding, min_y - padding))

class FlameSpark(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, base_color, life=40, size=8):
        super().__init__()
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        self.base_color = base_color
        self.life = life
        self.initial_life = life
        self.initial_size = size
        self.size = size
        self.alpha = 255
        self.rotation = random.uniform(0, math.pi*2)
        self.rotation_speed = random.uniform(-0.1, 0.1)

    def update(self, camera_speed):
        self.x -= camera_speed
        self.vy += 0.15
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.97
        self.vy *= 0.97
        self.life -= 1
        self.rotation += self.rotation_speed
        
        decay_ratio = max(0, self.life / self.initial_life)
        self.alpha = int(255 * decay_ratio)
        self.size = max(2, int(self.initial_size * (decay_ratio)**0.7))
        
        if self.life <= 0: self.kill()

    def draw(self, surface):
        if self.life > 0:
            r, g, b = self.base_color
            time_alive = self.initial_life - self.life
            
            draw_size = self.size * 6
            temp_surface = pygame.Surface((draw_size, draw_size), pygame.SRCALPHA)
            temp_surface.fill((0, 0, 0, 0))
            center = (draw_size // 2, draw_size // 2)

            # 1. Dış Glow (Büyük, yarı saydam)
            glow_size = self.size * 2.5
            glow_alpha = int(self.alpha * 0.15)
            
            # Renk geçişli glow
            for i in range(3):
                current_glow_size = glow_size * (1 - i * 0.2)
                current_alpha = glow_alpha * (0.8 - i * 0.2)
                glow_color = (r, g, b, int(current_alpha))
                if current_glow_size > 0:
                    pygame.draw.circle(temp_surface, glow_color, center, int(current_glow_size))

            # 2. Orta katman (Sıcak bölge)
            mid_size = self.size * 1.5
            mid_alpha = int(self.alpha * 0.5)
            mid_color = (min(255, r + 100), min(255, g + 100), min(255, b + 50), mid_alpha)
            if mid_size > 0:
                pygame.draw.circle(temp_surface, mid_color, center, int(mid_size))

            # 3. Çekirdek (Parlak)
            core_size = self.size
            core_color = (255, 255, 220, self.alpha)
            if core_size > 0:
                pygame.draw.circle(temp_surface, core_color, center, int(core_size))

            # 4. İç çekirdek (Beyaz sıcak nokta)
            inner_size = self.size * 0.5
            inner_color = (255, 255, 255, self.alpha)
            if inner_size > 0:
                pygame.draw.circle(temp_surface, inner_color, center, int(inner_size))

            # 5. Titreşim efekti
            if random.random() < 0.2:
                jitter_x = center[0] + random.randint(-2, 2)
                jitter_y = center[1] + random.randint(-2, 2)
                pygame.draw.circle(temp_surface, (255, 255, 255, self.alpha//2), 
                                 (jitter_x, jitter_y), int(inner_size * 1.5))

            surface.blit(temp_surface, (int(self.x - draw_size / 2), int(self.y - draw_size / 2)))

class Shockwave(pygame.sprite.Sprite):
    def __init__(self, x, y, color, max_radius=150, width=8, speed=10, rings=3):
        super().__init__()
        self.x, self.y = x, y
        self.color = color
        self.radius = 5
        self.max_radius = max_radius
        self.width = width
        self.speed = speed
        self.alpha = 255
        self.rings = rings
        self.ring_data = []  # Her halka için ayrı veri
        for i in range(rings):
            self.ring_data.append({
                'radius': 5 + i * 10,
                'alpha': 255,
                'width': max(2, width - i * 2)
            })

    def update(self, camera_speed):
        self.x -= camera_speed
        
        for i, ring in enumerate(self.ring_data):
            ring['radius'] += self.speed * (1 - i * 0.1)
            progress = ring['radius'] / self.max_radius
            ring['alpha'] = int(255 * (1 - progress))
            
            if ring['radius'] >= self.max_radius:
                ring['alpha'] = 0
        
        # Tüm halkalar bitti mi?
        if all(ring['alpha'] <= 0 for ring in self.ring_data):
            self.kill()

    def draw(self, surface):
        for ring in self.ring_data:
            if ring['alpha'] > 0:
                # Ana halka
                s = pygame.Surface((ring['radius'] * 2, ring['radius'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*self.color, ring['alpha']), 
                                 (int(ring['radius']), int(ring['radius'])), 
                                 int(ring['radius']), ring['width'])
                
                # İç glow
                inner_color = (min(255, self.color[0] + 50), 
                             min(255, self.color[1] + 50), 
                             min(255, self.color[2] + 50), 
                             ring['alpha'] // 2)
                pygame.draw.circle(s, inner_color, 
                                 (int(ring['radius']), int(ring['radius'])), 
                                 int(ring['radius'] - ring['width']//2), ring['width']//2)
                
                surface.blit(s, (int(self.x - ring['radius']), int(self.y - ring['radius'])))

class SpeedLine(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, color):
        super().__init__()
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(angle) * speed, math.sin(angle) * speed
        self.color = color
        self.length = random.randint(60, 120)
        self.width = random.randint(2, 4)
        self.life = 20
        self.initial_life = 20
        self.alpha = 180
        self.tail_length = random.uniform(1.5, 2.5)

    def update(self, camera_speed):
        self.x -= camera_speed
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        
        life_ratio = self.life / self.initial_life
        self.alpha = int(180 * life_ratio)
        self.width = max(1, int(self.width * life_ratio))
        
        if self.life <= 0: self.kill()

    def draw(self, surface):
        if self.alpha > 0:
            # Ana çizgi
            end_x = self.x - (self.vx * self.tail_length)
            end_y = self.y - (self.vy * self.tail_length)
            
            # Glow efekti
            glow_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            for i in range(3, 0, -1):
                glow_width = self.width + i * 2
                glow_alpha = self.alpha // (i * 2)
                pygame.draw.line(glow_surf, (*self.color, glow_alpha), 
                               (int(self.x), int(self.y)), 
                               (int(end_x), int(end_y)), glow_width)
            surface.blit(glow_surf, (0, 0))
            
            # Parlak çekirdek
            pygame.draw.line(surface, (*self.color, self.alpha), 
                           (int(self.x), int(self.y)), 
                           (int(end_x), int(end_y)), self.width)

class GhostTrail(pygame.sprite.Sprite):
    def __init__(self, x, y, color, life=25, size=15):
        super().__init__()
        self.x, self.y = x, y
        self.color = color
        self.life = life
        self.initial_life = life
        self.size = size
        self.alpha = 120
        self.rotation = random.uniform(0, math.pi*2)
        self.rotation_speed = random.uniform(-0.05, 0.05)

    def update(self, camera_speed):
        self.x -= camera_speed
        self.life -= 1
        self.rotation += self.rotation_speed
        
        life_ratio = self.life / self.initial_life
        self.alpha = int(120 * life_ratio)
        self.size = max(5, int(self.size * life_ratio))
        
        if self.life <= 0: self.kill()

    def draw(self, surface):
        if self.life > 0:
            # Dış glow
            glow_size = self.size * 1.5
            glow_surf = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.color, self.alpha//3), 
                             (glow_size, glow_size), glow_size)
            
            # Ana daire
            pygame.draw.circle(glow_surf, (*self.color, self.alpha), 
                             (glow_size, glow_size), self.size)
            
            # İç çekirdek
            inner_color = (min(255, self.color[0] + 50), 
                         min(255, self.color[1] + 50), 
                         min(255, self.color[2] + 50), 
                         self.alpha)
            pygame.draw.circle(glow_surf, inner_color, 
                             (glow_size, glow_size), self.size//2)
            
            # Döndürülmüş yüzey
            rotated = pygame.transform.rotate(glow_surf, math.degrees(self.rotation))
            rot_rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(rotated, rot_rect)

# --- YENİ EFEKT SINIFLARI ---
class EnergyOrb(pygame.sprite.Sprite):
    """Enerji topu efekti"""
    def __init__(self, x, y, color, size=10, life=30):
        super().__init__()
        self.x, self.y = x, y
        self.color = color
        self.size = size
        self.initial_size = size
        self.life = life
        self.initial_life = life
        self.alpha = 255
        self.rotation = 0
        self.pulse_speed = random.uniform(0.1, 0.3)
        self.pulse_offset = random.uniform(0, math.pi*2)

    def update(self, camera_speed):
        self.x -= camera_speed
        self.life -= 1
        self.rotation += 0.1
        
        life_ratio = self.life / self.initial_life
        self.alpha = int(255 * life_ratio)
        pulse = 0.2 * math.sin(pygame.time.get_ticks() * 0.001 * self.pulse_speed + self.pulse_offset)
        self.size = max(3, int(self.initial_size * life_ratio * (1 + pulse)))
        
        if self.life <= 0: self.kill()

    def draw(self, surface):
        if self.life > 0:
            # Dış halka
            ring_size = self.size * 2
            ring_surf = pygame.Surface((ring_size * 2, ring_size * 2), pygame.SRCALPHA)
            
            # Çoklu halkalar
            for i in range(3):
                current_radius = ring_size - i * 4
                current_alpha = self.alpha // (i + 2)
                pygame.draw.circle(ring_surf, (*self.color, current_alpha), 
                                 (ring_size, ring_size), current_radius, 2)
            
            # Enerji topu
            orb_size = self.size
            for i in range(3):
                current_orb_size = orb_size * (1 - i * 0.3)
                current_alpha = self.alpha * (0.8 - i * 0.2)
                color_variant = (min(255, self.color[0] + i*30), 
                               min(255, self.color[1] + i*30), 
                               min(255, self.color[2] + i*30))
                pygame.draw.circle(ring_surf, (*color_variant, int(current_alpha)), 
                                 (ring_size, ring_size), int(current_orb_size))
            
            # Döndür
            rotated = pygame.transform.rotate(ring_surf, self.rotation)
            rot_rect = rotated.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(rotated, rot_rect)

class ParticleExplosion(pygame.sprite.Sprite):
    """Partikül patlaması efekti"""
    def __init__(self, x, y, color, count=20, size_range=(3, 8), life_range=(20, 40)):
        super().__init__()
        self.particles = []
        for _ in range(count):
            angle = random.uniform(0, math.pi*2)
            speed = random.uniform(2, 8)
            size = random.uniform(size_range[0], size_range[1])
            life = random.randint(life_range[0], life_range[1])
            self.particles.append({
                'x': x, 'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'initial_size': size,
                'life': life,
                'initial_life': life,
                'color': color,
                'rotation': random.uniform(0, math.pi*2),
                'rotation_speed': random.uniform(-0.1, 0.1)
            })
        self.alive = True

    def update(self, camera_speed):
        if not self.alive:
            return
            
        alive_particles = 0
        for p in self.particles:
            p['x'] -= camera_speed
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.1
            p['vx'] *= 0.98
            p['vy'] *= 0.98
            p['life'] -= 1
            p['rotation'] += p['rotation_speed']
            
            if p['life'] > 0:
                alive_particles += 1
        
        if alive_particles == 0:
            self.kill()
            self.alive = False

    def draw(self, surface):
        for p in self.particles:
            if p['life'] > 0:
                life_ratio = p['life'] / p['initial_life']
                alpha = int(255 * life_ratio)
                size = p['size'] * life_ratio
                
                # Partikül yüzeyi
                part_surf = pygame.Surface((int(size*2), int(size*2)), pygame.SRCALPHA)
                
                # Glow
                pygame.draw.circle(part_surf, (*p['color'], alpha//3), 
                                 (int(size), int(size)), int(size*1.5))
                
                # Ana partikül
                pygame.draw.circle(part_surf, (*p['color'], alpha), 
                                 (int(size), int(size)), int(size))
                
                # İç çekirdek
                inner_color = (min(255, p['color'][0] + 50), 
                             min(255, p['color'][1] + 50), 
                             min(255, p['color'][2] + 50), 
                             alpha)
                pygame.draw.circle(part_surf, inner_color, 
                                 (int(size), int(size)), int(size//2))
                
                # Döndür
                rotated = pygame.transform.rotate(part_surf, math.degrees(p['rotation']))
                rot_rect = rotated.get_rect(center=(int(p['x']), int(p['y'])))
                surface.blit(rotated, rot_rect)

class ScreenFlash(pygame.sprite.Sprite):
    """Ekran flash efekti"""
    def __init__(self, color, intensity=100, duration=10):
        super().__init__()
        self.color = color
        self.intensity = intensity
        self.duration = duration
        self.life = duration
        self.alpha = intensity

    def update(self, camera_speed):
        self.life -= 1
        self.alpha = int(self.intensity * (self.life / self.duration))
        if self.life <= 0:
            self.kill()

    def draw(self, surface):
        if self.alpha > 0:
            flash_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surf.fill((*self.color, self.alpha))
            surface.blit(flash_surf, (0, 0))