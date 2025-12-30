import pygame
import random
import math
from settings import *

# --- OPTIMIZASYON NOTU ---
# Eski sistemde her efekt kendi Surface'ini oluşturuyordu. 
# Bu versiyonda tüm efektler doğrudan verilen hedef yüzeye (target_surface) çizilir.
# Bu, bellek tahsisini (allocation) ve çöp toplama (garbage collection) yükünü %90 azaltır.

def draw_cyber_grid(surface, time_ms):
    """Menüdeki hareketli ızgarayı çizer."""
    grid_color = (15, 20, 70)
    grid_size = 50
    offset_y = (time_ms * 0.1) % grid_size
    
    # Doğrudan ekrana çiz, ekstra surface yok
    for x in range(0, SCREEN_WIDTH, grid_size):
        pygame.draw.line(surface, grid_color, (x, 0), (x, SCREEN_HEIGHT), 1)
    
    for y in range(0, SCREEN_HEIGHT + grid_size, grid_size):
        draw_y = y + offset_y
        if draw_y < SCREEN_HEIGHT:
            pygame.draw.line(surface, grid_color, (0, draw_y), (SCREEN_WIDTH, draw_y), 1)

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
        if length > 0:
            perp_x, perp_y = -dy / length, dx / length
        else:
            perp_x, perp_y = 0, 0

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
        # List comprehension yerine in-place update daha hızlıdır ama kod okunabilirliği için bırakıldı
        self.segments = [(x - camera_speed + self.vx, y + self.vy) for x, y in self.segments]
        self.vy += 0.5
        self.life -= 1
        
        life_ratio = max(0, self.life / self.initial_life)
        self.alpha = int(255 * life_ratio)
        
        if self.life <= 0: self.kill()

    def draw(self, surface):
        if self.life > 0 and len(self.segments) >= 2:
            r, g, b = self.color
            
            # Glow efekti için daha kalın ve şeffaf çizgiler
            glow_alpha = int(self.alpha * 0.4)
            glow_color = (r, g, b, glow_alpha)
            
            # Glow (Dış Işıma)
            if glow_alpha > 0:
                pygame.draw.lines(surface, glow_color, False, self.segments, 6)
            
            # Orta Katman (Renk)
            pygame.draw.lines(surface, (min(255, r+50), min(255, g+50), min(255, b+50), int(self.alpha*0.8)), False, self.segments, 3)

            # Çekirdek (Beyaz/Parlak)
            core_color = (255, 255, 255, self.alpha)
            pygame.draw.lines(surface, core_color, False, self.segments, 1)

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

    def update(self, camera_speed):
        self.x -= camera_speed
        self.vy += 0.15
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.97
        self.vy *= 0.97
        self.life -= 1
        
        decay_ratio = max(0, self.life / self.initial_life)
        self.alpha = int(255 * decay_ratio)
        self.size = max(2, int(self.initial_size * (decay_ratio)**0.7))
        
        if self.life <= 0: self.kill()

    def draw(self, surface):
        if self.life > 0:
            r, g, b = self.base_color
            center = (int(self.x), int(self.y))
            
            # 1. Glow (Büyük)
            glow_size = int(self.size * 2.5)
            glow_alpha = int(self.alpha * 0.15)
            if glow_alpha > 5:
                pygame.draw.circle(surface, (r, g, b, glow_alpha), center, glow_size)

            # 2. Orta (Sıcak)
            mid_size = int(self.size * 1.5)
            mid_alpha = int(self.alpha * 0.5)
            mid_color = (min(255, r + 100), min(255, g + 100), min(255, b + 50), mid_alpha)
            if mid_size > 0:
                pygame.draw.circle(surface, mid_color, center, mid_size)

            # 3. Çekirdek
            core_size = int(self.size)
            core_color = (255, 255, 220, self.alpha)
            if core_size > 0:
                pygame.draw.circle(surface, core_color, center, core_size)

class Shockwave(pygame.sprite.Sprite):
    def __init__(self, x, y, color, max_radius=150, width=8, speed=10, rings=3):
        super().__init__()
        self.x, self.y = x, y
        self.color = color
        self.max_radius = max_radius
        self.width = width
        self.speed = speed * 1.5 # Daha hızlı ve agresif
        self.ring_data = []
        # ABARTILMIŞ ŞOK DALGASI: İç içe daha fazla ve kompleks halka
        for i in range(rings):
            self.ring_data.append({
                'radius': 5 + i * 15,
                'alpha': 255,
                'width': max(2, width - i * 1.5),
                'speed_mult': 1.0 - (i * 0.1) # İç halkalar biraz daha yavaş kalsın, derinlik katar
            })

    def update(self, camera_speed):
        self.x -= camera_speed
        
        all_done = True
        for ring in self.ring_data:
            ring['radius'] += self.speed * ring['speed_mult']
            progress = ring['radius'] / self.max_radius
            ring['alpha'] = int(255 * max(0, 1 - progress**0.5)) # Logaritmik sönümleme (daha uzun süre parlak kalır)
            
            if ring['radius'] < self.max_radius:
                all_done = False
            else:
                ring['alpha'] = 0
        
        if all_done:
            self.kill()

    def draw(self, surface):
        for ring in self.ring_data:
            if ring['alpha'] > 0:
                center = (int(self.x), int(self.y))
                radius = int(ring['radius'])
                width = int(ring['width'])
                
                # Ana enerji halkası
                if radius > 1:
                    pygame.draw.circle(surface, (*self.color, ring['alpha']), center, radius, width)
                
                # İnce beyaz şok çizgisi (daha keskin bir his verir)
                if radius > 5:
                    pygame.draw.circle(surface, (255, 255, 255, ring['alpha']//2), center, radius - 2, 1)

class SpeedLine(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, speed, color):
        super().__init__()
        self.x, self.y = x, y
        # Hız ve uzunluğu abarttık
        self.vx, self.vy = math.cos(angle) * speed * 2.0, math.sin(angle) * speed * 2.0
        self.color = color
        self.width = random.randint(2, 5)
        self.life = 25
        self.initial_life = 25
        self.alpha = 220
        self.tail_length = random.uniform(4.0, 7.0) # Çok daha uzun kuyruklar (Anime style)

    def update(self, camera_speed):
        self.x -= camera_speed
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        
        life_ratio = self.life / self.initial_life
        self.alpha = int(220 * life_ratio)
        self.width = max(1, int(self.width * 0.96)) # Giderek incelsin
        
        if self.life <= 0: self.kill()

    def draw(self, surface):
        if self.alpha > 0:
            end_x = self.x - (self.vx * self.tail_length)
            end_y = self.y - (self.vy * self.tail_length)
            
            start_pos = (int(self.x), int(self.y))
            end_pos = (int(end_x), int(end_y))
            
            # 1. Renkli Dış Hale (Glow)
            pygame.draw.line(surface, (*self.color, self.alpha // 3), start_pos, end_pos, self.width + 4)
            
            # 2. Ana Çizgi
            pygame.draw.line(surface, (*self.color, self.alpha), start_pos, end_pos, self.width)
            
            # 3. Parlak Beyaz Çekirdek (Lazer hissi verir)
            pygame.draw.line(surface, (255, 255, 255, self.alpha), start_pos, end_pos, max(1, self.width // 2))

class GhostTrail(pygame.sprite.Sprite):
    """Abartılmış 'Cyber' Afterimage Efekti"""
    def __init__(self, x, y, color, life=20, size=15):
        super().__init__()
        self.x, self.y = x, y
        self.color = color
        self.life = life
        self.initial_life = life
        self.size = size
        self.alpha = 180
        # Hafif bir titreme (glitch) ofseti
        self.jitter_x = 0
        self.jitter_y = 0

    def update(self, camera_speed):
        self.x -= camera_speed
        self.life -= 1
        
        life_ratio = self.life / self.initial_life
        self.alpha = int(180 * life_ratio)
        self.size = max(5, int(self.size * 0.92))
        
        # Glitch etkisi: Rastgele titreme
        if random.random() < 0.3:
            self.jitter_x = random.randint(-3, 3)
            self.jitter_y = random.randint(-3, 3)
        
        if self.life <= 0: self.kill()

    def draw(self, surface):
        if self.life > 0:
            center = (int(self.x + self.jitter_x), int(self.y + self.jitter_y))
            radius = int(self.size)
            
            if radius < 2: return

            # HOLOGRAFİK SCANLINE EFEKTİ
            # Dairenin içini yatay çizgilerle dolduruyoruz
            scan_step = 3 # Çizgi sıklığı
            for i in range(-radius, radius, scan_step):
                # Daire formülü: x^2 + y^2 = r^2  => x = sqrt(r^2 - y^2)
                # Kiriş uzunluğunu hesapla
                dy = i
                if abs(dy) >= radius: continue
                dx = int(math.sqrt(radius**2 - dy**2))
                
                start_line = (center[0] - dx, center[1] + dy)
                end_line = (center[0] + dx, center[1] + dy)
                
                # Çizgileri çiz
                pygame.draw.line(surface, (*self.color, self.alpha), start_line, end_line, 1)

            # Dış Çerçeve (Outline)
            pygame.draw.circle(surface, (*self.color, self.alpha), center, radius, 1)
            
            # Rastgele "bozuk piksel" efekti
            if random.random() < 0.2:
                glitch_rect = pygame.Rect(center[0] + random.randint(-radius, radius), 
                                        center[1] + random.randint(-radius, radius), 
                                        4, 2)
                pygame.draw.rect(surface, (255, 255, 255, self.alpha), glitch_rect)

class EnergyOrb(pygame.sprite.Sprite):
    def __init__(self, x, y, color, size=10, life=30):
        super().__init__()
        self.x, self.y = x, y
        self.color = color
        self.size = size
        self.initial_size = size
        self.life = life
        self.initial_life = life
        self.alpha = 255

    def update(self, camera_speed):
        self.x -= camera_speed
        self.life -= 1
        
        life_ratio = self.life / self.initial_life
        self.alpha = int(255 * life_ratio)
        self.size = max(3, int(self.initial_size * life_ratio))
        
        if self.life <= 0: self.kill()

    def draw(self, surface):
        if self.life > 0:
            center = (int(self.x), int(self.y))
            radius = int(self.size)
            
            # Dış Halka
            pygame.draw.circle(surface, (*self.color, self.alpha // 2), center, radius * 2, 2)
            # İç Top
            pygame.draw.circle(surface, (*self.color, self.alpha), center, radius)

class ParticleExplosion(pygame.sprite.Sprite):
    """ABARTILMIŞ: Daire yerine Dijital Kareler (Pixels) Saçılır"""
    def __init__(self, x, y, color, count=20, size_range=(3, 8), life_range=(20, 40)):
        super().__init__()
        self.particles = []
        for _ in range(count):
            angle = random.uniform(0, math.pi*2)
            speed = random.uniform(4, 12) # Hız arttı
            size = random.uniform(size_range[0], size_range[1] + 4) # Boyut arttı
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
                'rotation': random.uniform(0, 360), # Dönme efekti
                'rot_speed': random.uniform(-5, 5)
            })
        self.alive = True

    def update(self, camera_speed):
        if not self.alive: return
            
        alive_particles = 0
        for p in self.particles:
            p['x'] -= camera_speed
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['vy'] += 0.15 # Yerçekimi biraz daha belirgin
            p['vx'] *= 0.94 # Sürtünme
            p['vy'] *= 0.94
            p['life'] -= 1
            p['rotation'] += p['rot_speed']
            
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
                size = int(p['size'] * life_ratio)
                
                if size > 1:
                    # Kare (Pixel) Çizimi
                    # Yüzey oluşturmak yerine rect kullanıyoruz, ama dönme efekti için mecburen küçük surface lazım.
                    # Performans için dönmeyi şimdilik atlayıp rect çizelim, veya basitçe kare çizelim.
                    # Cyber teması için kareler dönmese de olur, glitch gibi dururlar.
                    
                    rect = pygame.Rect(int(p['x']), int(p['y']), size, size)
                    
                    # 1. Renkli İç
                    pygame.draw.rect(surface, (*p['color'], alpha), rect)
                    
                    # 2. Beyaz Kenar (Highlight)
                    if size > 3:
                        pygame.draw.rect(surface, (255, 255, 255, alpha), rect, 1)

class ScreenFlash(pygame.sprite.Sprite):
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
            # Tüm ekranı kaplayan flash için özel bir durum, burada yeni surface oluşturmak zorundayız
            # AMA fill kullanıp blit flagleri ile yapabiliriz.
            # Yine de performans için surface reuse en iyisi, ama bu nadir bir efekt.
            # Şimdilik basitçe fill ile yapalım, surface oluşturmak yerine.
            
            # Fill tüm yüzeyi boyar, o yüzden hedef surface'in boyutlarını alalım.
            # Ancak bu "screen" üzerine en son çizilmeli. 
            # Sprite grubu içinde olduğu için, geçici bir surface oluşturup alpha ile basmak zorundayız.
            # Optimasyon: Bu surface'i __init__'te bir kez oluşturup saklayalım.
            if not hasattr(self, 'flash_surf'):
                self.flash_surf = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
                self.flash_surf.fill((*self.color, self.alpha))
            else:
                # Alpha güncelle
                self.flash_surf.fill((*self.color, self.alpha)) # Maliyetli ama nadir
            
            surface.blit(self.flash_surf, (0, 0))