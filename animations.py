import pygame
import math
import random

# EKRAN TİTREME SINIFI
class ScreenShake:
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.time = 0
        
    def shake(self, intensity, duration):
        self.intensity = intensity
        self.duration = duration
        self.time = 0
        
    def update(self, dt):
        if self.duration > 0:
            self.time += dt
            if self.time >= self.duration:
                self.intensity = 0
                self.duration = 0
                
    def get_offset(self):
        if self.duration > 0 and self.intensity > 0:
            progress = self.time / self.duration
            current_intensity = self.intensity * (1 - progress)
            
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, current_intensity)
            
            return (
                math.cos(angle) * distance,
                math.sin(angle) * distance
            )
        return (0, 0)

# ELEKTRİK PARTİKÜL SINIFI
class ElectricParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.uniform(2, 6)
        self.life = random.uniform(0.5, 1.5)
        self.max_life = self.life
        self.speed = random.uniform(3, 8)
        self.angle = random.uniform(0, math.pi * 2)
        self.arc_points = []
        self.generate_arc()
        
    def generate_arc(self):
        self.arc_points = []
        points = random.randint(3, 6)
        for i in range(points):
            self.arc_points.append({
                'x': random.uniform(-10, 10),
                'y': random.uniform(-10, 10)
            })
    
    def update(self, dt):
        self.life -= dt
        self.size *= 0.95
        
    def draw(self, surface):
        if self.life > 0:
            alpha = int(255 * (self.life / self.max_life))
            if len(self.arc_points) > 1:
                points = [(self.x, self.y)]
                for point in self.arc_points:
                    points.append((self.x + point['x'], self.y + point['y']))
                
                for i in range(3):
                    width = int(self.size * (1 - i * 0.3))
                    if width > 0:
                        color = (*self.color, int(alpha * (0.8 - i * 0.2)))
                        if len(points) > 1:
                            pygame.draw.lines(surface, color, False, points, width)

# ŞOK DALGASI SINIFI
class Shockwave:
    def __init__(self, x, y, color, speed_multiplier=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 10
        self.max_radius = 250
        self.thickness = 15
        self.life = 1.0
        self.speed = 35.0 * speed_multiplier
        self.particles = []
        
    def update(self, dt):
        self.life -= dt * 0.8
        self.radius += self.speed * dt * 10
        self.thickness = max(1, self.thickness * 0.92)
        
        if self.radius < self.max_radius * 0.8:
            if random.random() < 0.5:
                angle = random.uniform(0, math.pi * 2)
                dist = self.radius
                self.particles.append({
                    'x': self.x + math.cos(angle) * dist,
                    'y': self.y + math.sin(angle) * dist,
                    'size': random.uniform(3, 8),
                    'life': random.uniform(0.5, 1.0),
                    'speed_x': math.cos(angle) * random.uniform(2, 6),
                    'speed_y': math.sin(angle) * random.uniform(2, 6),
                    'angle': angle
                })
        
        for p in self.particles[:]:
            p['life'] -= dt
            p['x'] += p['speed_x']
            p['y'] += p['speed_y']
            p['size'] *= 0.95
            if p['life'] <= 0:
                self.particles.remove(p)
    
    def draw(self, surface):
        if self.life > 0:
            alpha = int(200 * self.life)
            wave_color = (*self.color, alpha)
            
            pygame.draw.circle(surface, wave_color, (int(self.x), int(self.y)), int(self.radius), int(self.thickness))
            
            if self.radius > 20:
                pygame.draw.circle(surface, wave_color, (int(self.x), int(self.y)), int(self.radius - 20), int(self.thickness * 0.5))

            for p in self.particles:
                if p['life'] > 0:
                    part_alpha = int(255 * p['life'])
                    part_color = (255, 255, 255, part_alpha)
                    pygame.draw.circle(surface, part_color,
                                     (int(p['x']), int(p['y'])),
                                     int(p['size']))

# ANA KARAKTER ANİMATÖR SINIFI
class CharacterAnimator:
    def __init__(self):
        self.state = 'idle'
        self.frame = 0
        self.animation_speed = 0.15
        self.time = 0
        self.last_state = 'idle'
        self.state_change_time = 0
        
        # Animasyon parametreleri
        self.squash = 1.0
        self.stretch = 1.0
        self.rotation = 0
        self.scale = 1.0
        self.pulse = 1.0
        self.color_pulse = 1.0
        self.glow_intensity = 0.0
        self.shadow_size = 0.0
        self.energy_pulse = 0.0
        
        # Frame tabanlı animasyonlar
        self.current_frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 3
        
        # Animasyon yoğunluğu
        self.animation_intensity = 2.0
        
        # Ekstra efektler
        self.extra_effects = {
            'sparkle_positions': [],
            'trail_particles': [],
            'aura_alpha': 0,
            'electric_particles': [],
            'shockwaves': [],
            'screen_shake': ScreenShake(),
            'dash_lines': [],
            'impact_particles': [],
            'afterimages': []
        }
        
    def update(self, dt, state, is_grounded, velocity_y, is_dashing=False, is_slamming=False):
        self.time += dt
        self.last_state = self.state
        
        # State belirleme
        if is_dashing:
            self.state = 'dashing'
        elif is_slamming:
            self.state = 'slamming'
        elif not is_grounded:
            if velocity_y < 0:
                self.state = 'jumping'
            else:
                self.state = 'falling'
        else:
            self.state = state
        
        # State değiştiyse sıfırla
        if self.state != self.last_state:
            self.state_change_time = self.time
            self.current_frame_index = 0
            self.frame_timer = 0
            
            if self.state == 'dashing':
                self.extra_effects['electric_particles'] = []
                self.extra_effects['dash_lines'] = []
                self.extra_effects['afterimages'] = []
            elif self.state == 'slamming':
                self.extra_effects['shockwaves'] = []
                self.extra_effects['impact_particles'] = []
        
        # State'e göre animasyon güncelle
        if self.state == 'idle':
            self.update_idle(dt)
        elif self.state == 'running':
            self.update_running(dt)
        elif self.state == 'jumping':
            self.update_jumping(dt, velocity_y)
        elif self.state == 'falling':
            self.update_falling(dt, velocity_y)
        elif self.state == 'dashing':
            self.update_dashing(dt)
        elif self.state == 'slamming':
            self.update_slamming(dt, velocity_y)
            
        # Frame animasyonu
        self.update_frame_animation(dt)
        
        # Ekstra efektler
        self.update_extra_effects(dt)
        
        # Screen shake
        self.extra_effects['screen_shake'].update(dt)
            
    def update_idle(self, dt):
        self.pulse = 1.0
        self.squash = 1.0
        self.stretch = 1.0
        self.rotation = 0
        self.color_pulse = 1.0
        self.glow_intensity = 0.1
        self.scale = 1.0
        self.energy_pulse = 0.0
        self.shadow_size = 0.0
        
    def update_running(self, dt):
        intensity = self.animation_intensity
        run_speed = 12.0 * intensity
        time = self.time * run_speed
        
        self.pulse = 1.0
        self.scale = 1.0
        
        self.squash = 1.0 + 0.3 * intensity * abs(math.sin(time))
        self.stretch = 1.0 - 0.25 * intensity * abs(math.sin(time + 0.5))
        self.rotation = 0.15 * intensity * math.sin(time * 0.4)
        self.color_pulse = 1.0 + 0.15 * intensity * math.sin(time * 1.5)
        self.glow_intensity = 0.4 + 0.3 * math.sin(time * 1.0)
        self.shadow_size = 0.2 * abs(math.sin(time))
        
    def update_jumping(self, dt, velocity_y):
        intensity = self.animation_intensity
        jump_progress = (self.time - self.state_change_time) * 3.0 * intensity
        time = self.time * 4.0
        
        self.pulse = 1.0
        self.scale = 1.0
        
        if jump_progress < 0.8:
            squash_factor = 0.6 + 0.4 * (jump_progress / 0.8)
            stretch_factor = 1.6 - 0.6 * (jump_progress / 0.8)
            self.squash = squash_factor
            self.stretch = stretch_factor
        else:
            self.squash = 1.0 + 0.2 * intensity * math.sin(time * 2.0)
            self.stretch = 1.0 - 0.15 * intensity * math.sin(time * 2.0 + 0.5)
        
        self.rotation = -velocity_y * 0.1 * intensity
        self.color_pulse = 1.0 + 0.5 * intensity * (0.7 + 0.3 * math.sin(time * 3.0))
        self.glow_intensity = 0.5 + 0.4 * math.sin(time * 2.5)
        self.energy_pulse = 0.8 + 0.7 * math.sin(time * 4.0)
        
    def update_falling(self, dt, velocity_y):
        intensity = self.animation_intensity
        time = self.time * 3.0
        
        self.pulse = 1.0
        self.scale = 1.0
        
        self.squash = 1.0 - 0.25 * intensity * math.sin(time * 3.0)
        self.stretch = 1.0 + 0.4 * intensity * math.sin(time * 3.0 + 0.3)
        self.rotation = velocity_y * 0.05 * intensity
        self.color_pulse = 1.0 - 0.3 * intensity * min(1.0, abs(velocity_y) / 35.0)
        self.glow_intensity = 0.3 + 0.2 * math.sin(time * 2.0)
        self.shadow_size = 0.3 * (1.0 + math.sin(time * 2.0))
        
    def update_dashing(self, dt):
        intensity = self.animation_intensity * 1.8 
        dash_speed = 40.0 * intensity
        time = self.time * dash_speed
        
        self.pulse = 1.0 + 0.4 * intensity * math.sin(time * 1.0)
        self.scale = 1.2 + 0.4 * intensity * math.sin(time * 0.5)
        self.squash = 1.0 + 0.5 * intensity * math.sin(time * 0.8 + 0.2)
        self.stretch = 1.8 + 0.6 * intensity * math.sin(time * 0.6 + 0.4)
        
        # HIZ ÇİZGİLERİ
        if random.random() < 0.8:
            if random.random() < 0.5:
                angle = random.uniform(-0.2, 0.2)
            else:
                angle = random.uniform(math.pi - 0.2, math.pi + 0.2)
                
            self.extra_effects['dash_lines'].append({
                'x': random.uniform(-40, 40),
                'y': random.uniform(-30, 30),
                'length': random.uniform(60, 150),
                'width': random.uniform(2, 5),
                'angle': angle,
                'life': 0.3,
                'color': (200, 240, 255, 180)
            })
        
        # DASH PARTİKÜLLERİ
        for _ in range(2):
            self.extra_effects['trail_particles'].append({
                'x': random.uniform(-20, 20),
                'y': random.uniform(-20, 20),
                'size': random.uniform(2, 5),
                'life': 0.8,
                'speed': 0,
                'color': (100, 200, 255)
            })

        # AFTERIMAGE
        if random.random() < 0.7:
            self.extra_effects['afterimages'].append({
                'x': 0,
                'y': 0,
                'scale': self.scale,
                'rotation': self.rotation,
                'color': (100, 180, 255, 100),
                'life': 0.2
            })
        
    def update_slamming(self, dt, velocity_y):
        intensity = self.animation_intensity * 2.5
        slam_speed = 35.0 * intensity
        time = self.time * slam_speed
        
        self.scale = 1.5
        self.squash = 0.5
        self.stretch = 1.5
        self.glow_intensity = 2.0
        
        # ŞOK DALGASI
        state_time = self.time - self.state_change_time
        
        if state_time < 0.2:
            if len(self.extra_effects['shockwaves']) == 0:
                self.extra_effects['shockwaves'].append(Shockwave(0, 0, (255, 100, 50), speed_multiplier=1.2))
                self.extra_effects['screen_shake'].shake(25.0, 0.8)
                
            elif len(self.extra_effects['shockwaves']) == 1 and state_time > 0.05:
                self.extra_effects['shockwaves'].append(Shockwave(0, 0, (255, 200, 100), speed_multiplier=1.0))
                
            elif len(self.extra_effects['shockwaves']) == 2 and state_time > 0.1:
                self.extra_effects['shockwaves'].append(Shockwave(0, 0, (255, 255, 200), speed_multiplier=0.8))

        # ETRAFA SAÇILAN PARTİKÜLLER
        if random.random() < 0.8:
            angle = random.uniform(math.pi, math.pi * 2)
            speed = random.uniform(10, 25)
            self.extra_effects['impact_particles'].append({
                'x': random.uniform(-20, 20),
                'y': 10,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': random.uniform(2, 6),
                'life': random.uniform(0.5, 1.5),
                'color': (255, random.randint(100, 200), 50)
            })
        
    def update_frame_animation(self, dt):
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0
            self.current_frame_index = (self.current_frame_index + 1) % 8
            
    def update_extra_effects(self, dt):
        for sparkle in self.extra_effects['sparkle_positions'][:]:
            sparkle['life'] -= dt * sparkle.get('speed', 1.0)
            if 'size' in sparkle:
                sparkle['size'] *= 0.98
            if sparkle['life'] <= 0:
                self.extra_effects['sparkle_positions'].remove(sparkle)
        
        for particle in self.extra_effects['trail_particles'][:]:
            particle['life'] -= dt * particle.get('speed', 1.0)
            if 'size' in particle:
                particle['size'] *= 0.95
            if particle['life'] <= 0:
                self.extra_effects['trail_particles'].remove(particle)
        
        if self.extra_effects['aura_alpha'] > 0:
            self.extra_effects['aura_alpha'] = max(0, self.extra_effects['aura_alpha'] - 8)
        
        for particle in self.extra_effects['electric_particles'][:]:
            particle.update(dt)
            if particle.life <= 0:
                self.extra_effects['electric_particles'].remove(particle)
        
        for wave in self.extra_effects['shockwaves'][:]:
            wave.update(dt)
            if wave.life <= 0 or wave.radius > wave.max_radius * 1.5:
                self.extra_effects['shockwaves'].remove(wave)
        
        for line in self.extra_effects['dash_lines'][:]:
            line['life'] -= dt
            if 'width' in line:
                line['width'] *= 0.9
            if line['life'] <= 0:
                self.extra_effects['dash_lines'].remove(line)
        
        for particle in self.extra_effects['impact_particles'][:]:
            particle['life'] -= dt
            particle['x'] += particle.get('vx', 0) * dt * 60
            particle['y'] += particle.get('vy', 0) * dt * 60
            particle['vy'] += 0.5
            if 'size' in particle:
                particle['size'] *= 0.93
            if particle['life'] <= 0:
                self.extra_effects['impact_particles'].remove(particle)
        
        for afterimage in self.extra_effects['afterimages'][:]:
            afterimage['life'] -= dt
            if afterimage['life'] <= 0:
                self.extra_effects['afterimages'].remove(afterimage)
            
    def get_draw_params(self):
        return {
            'squash': self.squash,
            'stretch': self.stretch,
            'rotation': self.rotation,
            'scale': self.scale * self.pulse,
            'color_pulse': self.color_pulse,
            'frame_index': self.current_frame_index,
            'animation_intensity': self.animation_intensity,
            'glow_intensity': self.glow_intensity,
            'shadow_size': self.shadow_size,
            'energy_pulse': self.energy_pulse,
            'extra_effects': self.extra_effects.copy(),
            'screen_shake_offset': self.extra_effects['screen_shake'].get_offset()
        }
    
    def get_modified_color(self, base_color):
        r, g, b = base_color
        pulse = self.color_pulse
        energy = self.energy_pulse
        
        r = min(255, int(r * pulse))
        g = min(255, int(g * pulse))
        b = min(255, int(b * pulse))
        
        if self.state == 'dashing':
            r = min(255, int(r + 100 * energy))
            g = min(255, int(g + 80 * energy))
            b = min(255, int(b + 60 * energy))
        elif self.state == 'slamming':
            r = min(255, int(r + 150 * energy))
            g = min(255, int(g + 60 * energy))
            b = max(0, int(b - 40 * energy))
        elif self.state == 'jumping':
            r = min(255, r + int(30 * energy))
            g = min(255, g + int(30 * energy))
            b = min(255, b + int(30 * energy))
        
        glow = self.glow_intensity
        if glow > 0.5:
            r = min(255, int(r * (1.0 + (glow - 0.5) * 2)))
            g = min(255, int(g * (1.0 + (glow - 0.5) * 2)))
            b = min(255, int(b * (1.0 + (glow - 0.5) * 2)))
        
        return (r, g, b)
    
    def set_animation_intensity(self, intensity):
        self.animation_intensity = max(0.8, min(3.0, intensity))
    
    def get_glow_color(self, base_color):
        r, g, b = base_color
        glow = self.glow_intensity
        
        r = min(255, int(r * (1.0 + glow * 1.0)))
        g = min(255, int(g * (1.0 + glow * 1.0)))
        b = min(255, int(b * (1.0 + glow * 1.0)))
        
        alpha = int(200 * glow)
        
        return (r, g, b, alpha)

    def trigger_impact(self, x, y):
        if self.state == 'slamming':
            self.extra_effects['shockwaves'].append(
                Shockwave(x, y, (255, 150, 100))
            )
            self.extra_effects['screen_shake'].shake(20.0, 0.3)


# TRAIL EFFECT SINIFI (main.py'de kullanılıyor)
class TrailEffect:
    def __init__(self, x, y, color, size, life=20):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.alpha = 255
        self.glow_size = size * 3.0
        self.rotation = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(-0.5, 0.5)
        self.pulse_speed = random.uniform(0.2, 0.4)
        self.pulse_offset = random.uniform(0, math.pi * 2)
        self.sparkles = []
        
        for _ in range(random.randint(5, 10)):
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0.3, 1.0) * size
            self.sparkles.append({
                'angle': angle,
                'distance': distance,
                'size': random.uniform(0.3, 0.6) * size,
                'speed': random.uniform(0.8, 2.0),
                'alpha': random.randint(180, 240)
            })
        
    def update(self, camera_speed):
        self.x -= camera_speed
        self.life -= 1
        self.alpha = int(255 * (self.life / self.max_life))
        self.size = max(0, self.size * 0.8)
        self.glow_size = self.size * 3.0
        self.rotation += self.rotation_speed
        
        pulse = 0.2 * math.sin(pygame.time.get_ticks() * 0.001 * self.pulse_speed + self.pulse_offset)
        self.size = max(0, self.size * (1.0 + pulse))
        
        for sparkle in self.sparkles:
            sparkle['angle'] += sparkle['speed'] * 0.08
        
    def draw(self, surface):
        if self.life > 0:
            total_size = int(self.glow_size * 2)
            s = pygame.Surface((total_size, total_size), pygame.SRCALPHA)
            center = (total_size // 2, total_size // 2)
            
            for i in range(6, 0, -1):
                glow_size = self.glow_size * (1.0 - i * 0.12)
                glow_alpha = self.alpha // (i + 2)
                glow_color = (*self.color, glow_alpha)
                pygame.draw.circle(s, glow_color, center, int(glow_size))
            
            main_color = (*self.color, self.alpha)
            pygame.draw.circle(s, main_color, center, int(self.size))
            
            for i in range(3):
                inner_size = self.size * (0.8 - i * 0.2)
                inner_alpha = self.alpha * (0.9 - i * 0.3)
                inner_color = (
                    min(255, self.color[0] + 80 - i * 20),
                    min(255, self.color[1] + 80 - i * 20),
                    min(255, self.color[2] + 80 - i * 20),
                    int(inner_alpha)
                )
                pygame.draw.circle(s, inner_color, center, int(inner_size))
            
            for sparkle in self.sparkles:
                angle = sparkle['angle']
                distance = sparkle['distance'] * self.size
                sparkle_x = center[0] + math.cos(angle) * distance
                sparkle_y = center[1] + math.sin(angle) * distance
                
                sparkle_color = (
                    255, 255, 255,
                    int(sparkle['alpha'] * (self.alpha / 255))
                )
                pygame.draw.circle(s, sparkle_color, 
                                 (int(sparkle_x), int(sparkle_y)), 
                                 int(sparkle['size']))
            
            if abs(self.rotation) > 0.01:
                rotated = pygame.transform.rotate(s, math.degrees(self.rotation))
                rot_rect = rotated.get_rect(center=(int(self.x), int(self.y)))
                surface.blit(rotated, rot_rect)
            else:
                surface.blit(s, (int(self.x - self.glow_size), int(self.y - self.glow_size)))