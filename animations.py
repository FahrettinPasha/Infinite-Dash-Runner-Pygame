# animations.py
import math
import random
import copy
import pygame

# ---------- AYARLAR ----------
AFTERIMAGE_POOL_SIZE = 6
MAX_TRAIL_PARTICLES = 120
MAX_IMPACT_PARTICLES = 300

def clamp(v, a, b):
    return max(a, min(b, v))

def damp(current, target, smoothing, dt):
    if smoothing <= 0 or dt <= 0:
        return target
    factor = 1.0 - math.exp(-smoothing * dt)
    return current + (target - current) * factor

# ---------- HAFİF VFX VERİ YAPILARI ----------
class ElectricParticle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.uniform(2.0, 6.0)
        self.life = random.uniform(0.45, 1.0)
        self.max_life = self.life
        self.speed = random.uniform(20.0, 90.0)
        self.angle = random.uniform(0, math.pi * 2)
        self.arc_points = []
        self._generate_arc()

    def _generate_arc(self):
        self.arc_points = []
        pts = random.randint(3, 6)
        for _ in range(pts):
            self.arc_points.append({
                'x': random.uniform(-18, 18),
                'y': random.uniform(-8, 8)
            })

    def update(self, dt):
        self.life -= dt
        self.size *= (1.0 - 0.9 * dt)
        self.x += math.cos(self.angle) * self.speed * dt * 0.22
        self.y += math.sin(self.angle) * self.speed * dt * 0.22

    def draw(self, surface, ox=0, oy=0):
        if self.life <= 0:
            return
        alpha = int(255 * clamp(self.life / self.max_life, 0.0, 1.0))
        if len(self.arc_points) > 0:
            points = [(int(self.x + ox), int(self.y + oy))]
            for p in self.arc_points:
                points.append((int(self.x + p['x'] + ox), int(self.y + p['y'] + oy)))
            
            for i in range(3):
                width = max(1, int(self.size * (1.0 - i * 0.35)))
                col = (*self.color, int(alpha * (0.9 - i * 0.3)))
                if len(points) > 1:
                    pygame.draw.lines(surface, col, False, points, width)

class ShockwaveLite:
    def __init__(self, x, y, color, speed_multiplier=1.0):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 10.0
        self.max_radius = 420.0
        self.thickness = 18.0
        self.life = 1.0
        self.speed = 28.0 * speed_multiplier
        self.particles = []

    def update(self, dt):
        self.life -= dt * 0.9
        self.radius += self.speed * dt * 12.0
        self.thickness = max(1.0, self.thickness * (1.0 - 0.9 * dt))
        if self.radius < self.max_radius * 0.85 and random.random() < 0.35:
            angle = random.uniform(0, math.pi * 2)
            dist = self.radius
            self.particles.append({
                'x': self.x + math.cos(angle) * dist,
                'y': self.y + math.sin(angle) * dist,
                'size': random.uniform(3, 7),
                'life': random.uniform(0.4, 0.9),
                'speed_x': math.cos(angle) * random.uniform(20, 60),
                'speed_y': math.sin(angle) * random.uniform(20, 60),
            })
        for p in self.particles[:]:
            p['life'] -= dt
            p['x'] += p['speed_x'] * dt
            p['y'] += p['speed_y'] * dt
            p['size'] *= (1.0 - 1.2 * dt)
            if p['life'] <= 0:
                self.particles.remove(p)

    def draw(self, surface, ox=0, oy=0):
        if self.life <= 0:
            return
        alpha = int(200 * clamp(self.life, 0.0, 1.0))
        center = (int(self.x + ox), int(self.y + oy))
        
        if alpha > 0:
             pygame.draw.circle(surface, (*self.color, alpha), center, int(self.radius), int(max(1, self.thickness)))

        for p in self.particles:
            if p['life'] > 0:
                part_alpha = int(255 * clamp(p['life'], 0.0, 1.0))
                pygame.draw.circle(surface, (255, 255, 255, part_alpha), (int(p['x'] + ox), int(p['y'] + oy)), int(max(1, p['size'])))

class ScreenShakeLite:
    def __init__(self):
        self.intensity = 0.0
        self.duration = 0.0
        self.time = 0.0

    def shake(self, intensity, duration):
        self.intensity = max(self.intensity, intensity)
        self.duration = max(self.duration, duration)
        self.time = 0.0

    def update(self, dt):
        if self.duration > 0:
            self.time += dt
            if self.time >= self.duration:
                self.intensity = 0.0
                self.duration = 0.0
                self.time = 0.0

    def get_offset(self):
        if self.duration > 0 and self.intensity > 0:
            progress = clamp(self.time / self.duration, 0.0, 1.0)
            current_intensity = self.intensity * (1.0 - progress)
            angle = random.uniform(0, math.pi * 2)
            distance = random.uniform(0, current_intensity)
            return (math.cos(angle) * distance, math.sin(angle) * distance)
        return (0, 0)

# ---------- CHARACTER ANIMATOR ----------
class CharacterAnimator:
    def __init__(self):
        # state
        self.state = 'idle'
        self.last_state = 'idle'
        self.time = 0.0
        self.state_change_time = 0.0

        # transforms
        self.squash = 1.0
        self.stretch = 1.0
        self.rotation = 0.0
        self.scale = 1.0
        self.pulse = 1.0
        self.color_pulse = 1.0
        self.glow_intensity = 0.0
        self.shadow_size = 0.0
        self.energy_pulse = 0.0

        # frame anim
        self.current_frame_index = 0
        self.frame_timer = 0.0
        self.frame_delay = 0.06

        # intensity and extra effects
        self.animation_intensity = 1.6
        self.extra_effects = {
            'sparkle_positions': [],
            'trail_particles': [],
            'aura_alpha': 0,
            'electric_particles': [],
            'shockwaves': [],
            'screen_shake': ScreenShakeLite(),
            'dash_lines': [],
            'impact_particles': [],
            'afterimages': [],
            'hit_pause': 0.0,
            '_impact_bursted': False
        }

        # smoothing targets for stable dash
        self._target_scale = 1.0
        self._target_rotation = 0.0
        self._target_squash = 1.0
        self._target_stretch = 1.0

        self._smooth_scale = 14.0
        self._smooth_rotation = 12.0
        self._smooth_shape = 12.0

        self._max_dash_scale = 1.35
        self._min_dash_scale = 0.95
        self._max_rotation_deg = 6.0

        # afterimage pool
        self._afterimage_pool = [None] * AFTERIMAGE_POOL_SIZE

    def update(self, dt, state, is_grounded, velocity_y, is_dashing=False, is_slamming=False):
        self.time += dt
        self.last_state = self.state

        if is_dashing:
            self.state = 'dashing'
        elif is_slamming:
            self.state = 'slamming'
        elif not is_grounded:
            self.state = 'jumping' if velocity_y < 0 else 'falling'
        else:
            self.state = state

        if self.state != self.last_state:
            self.state_change_time = self.time
            self.current_frame_index = 0
            self.frame_timer = 0.0
            if self.state == 'dashing':
                self.extra_effects['electric_particles'] = []
                self.extra_effects['dash_lines'] = []
                self.extra_effects['afterimages'] = []
                self._afterimage_pool = [None] * AFTERIMAGE_POOL_SIZE
            if self.state == 'slamming':
                self.extra_effects['shockwaves'] = []
                self.extra_effects['impact_particles'] = []
                self.extra_effects['_impact_bursted'] = False

        # state updates
        if self.state == 'idle':
            self._update_idle(dt)
        elif self.state == 'running':
            self._update_running(dt)
        elif self.state == 'jumping':
            self._update_jumping(dt, velocity_y)
        elif self.state == 'falling':
            self._update_falling(dt, velocity_y)
        elif self.state == 'dashing':
            self._update_dashing(dt)
        elif self.state == 'slamming':
            self._update_slamming(dt, velocity_y)

        self._update_frame_animation(dt)
        self._update_extra_effects(dt)
        self.extra_effects['screen_shake'].update(dt)

    # basic states
    def _update_idle(self, dt):
        self.pulse = damp(self.pulse, 1.0, 6.0, dt)
        self.squash = damp(self.squash, 1.0, 6.0, dt)
        self.stretch = damp(self.stretch, 1.0, 6.0, dt)
        self.rotation = damp(self.rotation, 0.0, 8.0, dt)
        self.color_pulse = damp(self.color_pulse, 1.0, 6.0, dt)
        self.glow_intensity = damp(self.glow_intensity, 0.12, 4.0, dt)
        self.scale = damp(self.scale, 1.0, 8.0, dt)
        self.energy_pulse = damp(self.energy_pulse, 0.0, 6.0, dt)
        self.shadow_size = damp(self.shadow_size, 0.0, 6.0, dt)

    def _update_running(self, dt):
        intensity = self.animation_intensity
        run_speed = 8.0 * intensity
        t = self.time * run_speed
        self.squash = 1.0 + 0.12 * intensity * abs(math.sin(t))
        self.stretch = 1.0 - 0.08 * intensity * abs(math.sin(t + 0.5))
        self.rotation = 0.08 * intensity * math.sin(t * 0.4)
        self.color_pulse = 1.0 + 0.08 * intensity * math.sin(t * 1.5)
        self.glow_intensity = 0.28 + 0.15 * math.sin(t * 1.0)
        self.shadow_size = 0.12 * abs(math.sin(t))

    def _update_jumping(self, dt, velocity_y):
        intensity = self.animation_intensity
        jump_progress = (self.time - self.state_change_time) * 3.0 * intensity
        t = self.time * 4.0
        if jump_progress < 0.8:
            self.squash = 0.6 + 0.4 * (jump_progress / 0.8)
            self.stretch = 1.6 - 0.6 * (jump_progress / 0.8)
        else:
            self.squash = 1.0 + 0.08 * intensity * math.sin(t * 2.0)
            self.stretch = 1.0 - 0.06 * intensity * math.sin(t * 2.0 + 0.5)
        self.rotation = -velocity_y * 0.05 * intensity
        self.color_pulse = 1.0 + 0.35 * intensity * (0.7 + 0.3 * math.sin(t * 3.0))
        self.glow_intensity = 0.4 + 0.25 * math.sin(t * 2.5)
        self.energy_pulse = 0.6 + 0.5 * math.sin(t * 4.0)

    def _update_falling(self, dt, velocity_y):
        intensity = self.animation_intensity
        t = self.time * 3.0
        self.squash = 1.0 - 0.12 * intensity * math.sin(t * 3.0)
        self.stretch = 1.0 + 0.18 * intensity * math.sin(t * 3.0 + 0.3)
        self.rotation = velocity_y * 0.03 * intensity
        self.color_pulse = 1.0 - 0.2 * intensity * min(1.0, abs(velocity_y) / 35.0)
        self.glow_intensity = 0.24 + 0.14 * math.sin(t * 2.0)
        self.shadow_size = 0.22 * (1.0 + math.sin(t * 2.0))

    def _update_dashing(self, dt):
        intensity = max(0.7, self.animation_intensity * 1.2)
        t = self.time * 5.0

        target_pulse = 1.0 + 0.06 * intensity * math.sin(t * 1.0)
        target_scale = 1.06 + 0.06 * intensity * math.sin(t * 0.5)
        target_scale = clamp(target_scale, self._min_dash_scale, self._max_dash_scale)

        target_squash = 1.0 + 0.06 * intensity * math.sin(t * 0.8 + 0.2)
        target_stretch = 1.08 + 0.06 * intensity * math.sin(t * 0.6 + 0.4)

        target_rotation = 0.03 * intensity * math.sin(t * 0.4)
        max_rot_rad = math.radians(self._max_rotation_deg)
        target_rotation = clamp(target_rotation, -max_rot_rad, max_rot_rad)

        self._target_scale = target_scale * target_pulse
        self._target_squash = target_squash
        self._target_stretch = target_stretch
        self._target_rotation = target_rotation

        self.scale = damp(self.scale, self._target_scale, self._smooth_scale * 1.4, dt)
        self.squash = damp(self.squash, self._target_squash, self._smooth_shape * 1.4, dt)
        self.stretch = damp(self.stretch, self._target_stretch, self._smooth_shape * 1.4, dt)
        self.rotation = damp(self.rotation, self._target_rotation, self._smooth_rotation * 1.4, dt)
        self.pulse = damp(self.pulse, 1.0 + 0.03 * intensity, 6.0, dt)
        self.glow_intensity = damp(self.glow_intensity, 0.4 * intensity, 6.0, dt)

        if random.random() < 0.30:
            for i in range(len(self._afterimage_pool)):
                if self._afterimage_pool[i] is None:
                    self._afterimage_pool[i] = {
                        'x': 0, 'y': 0,
                        'scale': self.scale * (0.98 + random.uniform(-0.01, 0.01)),
                        'rotation': self.rotation + random.uniform(-0.01, 0.01),
                        'color': (140, 200, 255, 100),
                        'life': 0.10 + random.uniform(-0.02, 0.02)
                    }
                    break

        ai_list = []
        for slot in self._afterimage_pool:
            if slot is not None:
                ai_list.append(slot.copy())
        self.extra_effects['afterimages'] = ai_list

        electric_cap = 6
        spawn_chance = 0.22
        if random.random() < spawn_chance and len(self.extra_effects['electric_particles']) < electric_cap:
            for _ in range(random.randint(1, 2)):
                ex = ElectricParticle(random.uniform(-7, 7), random.uniform(-7, 7), (160, 230, 255))
                ex.speed *= random.uniform(0.85, 1.2)
                ex.life *= random.uniform(0.85, 1.0)
                self.extra_effects['electric_particles'].append(ex)

        if random.random() < 0.10 and len(self.extra_effects['impact_particles']) < (MAX_IMPACT_PARTICLES // 3):
            burst_count = random.randint(1, 2)
            for _ in range(burst_count):
                angle = random.uniform(-0.5, 0.5) + math.pi
                speed = random.uniform(10, 20)
                self.extra_effects['impact_particles'].append({
                    'x': random.uniform(-4, 4),
                    'y': random.uniform(-4, 4),
                    'vx': math.cos(angle) * speed,
                    'vy': math.sin(angle) * speed * -0.5,
                    'size': random.uniform(2, 4),
                    'life': random.uniform(0.16, 0.36),
                    'color': (160, 220, 255)
                })

        if random.random() < 0.05:
            self.extra_effects['screen_shake'].shake(2.5 * intensity, 0.05)

        if random.random() < 0.18 and len(self.extra_effects['dash_lines']) < 4:
            angle = random.choice([random.uniform(-0.08, 0.08), random.uniform(math.pi-0.08, math.pi+0.08)])
            self.extra_effects['dash_lines'].append({
                'x': random.uniform(-24, 24),
                'y': random.uniform(-12, 12),
                'length': random.uniform(80, 140),
                'width': random.uniform(1, 2),
                'angle': angle,
                'life': 0.12 + random.uniform(-0.02, 0.02),
                'color': (200, 245, 255, 180)
            })

        for i, slot in enumerate(self._afterimage_pool):
            if slot is not None:
                slot['life'] -= dt
                if slot['life'] <= 0:
                    self._afterimage_pool[i] = None

    def _update_slamming(self, dt, velocity_y):
        intensity = self.animation_intensity * 2.0
        self.scale = damp(self.scale, 1.45, 8.0, dt)
        self.squash = damp(self.squash, 0.52, 8.0, dt)
        self.stretch = damp(self.stretch, 1.55, 8.0, dt)
        self.glow_intensity = damp(self.glow_intensity, 1.6, 8.0, dt)
        state_time = self.time - self.state_change_time

        if 0.0 <= state_time < 0.05:
            self.extra_effects['hit_pause'] = 0.05

        if state_time < 0.32:
            if len(self.extra_effects['shockwaves']) == 0:
                self.extra_effects['shockwaves'].append(ShockwaveLite(0, 0, (255, 120, 60), speed_multiplier=1.45))
                self.extra_effects['screen_shake'].shake(20.0, 0.8)
            elif len(self.extra_effects['shockwaves']) == 1 and state_time > 0.06:
                self.extra_effects['shockwaves'].append(ShockwaveLite(0, 0, (255, 200, 120), speed_multiplier=1.05))
            elif len(self.extra_effects['shockwaves']) == 2 and state_time > 0.12:
                self.extra_effects['shockwaves'].append(ShockwaveLite(0, 0, (255, 255, 200), speed_multiplier=0.85))
            elif len(self.extra_effects['shockwaves']) == 3 and state_time > 0.18:
                self.extra_effects['shockwaves'].append(ShockwaveLite(0, 0, (255, 240, 200), speed_multiplier=0.5))

        if 0.0 <= state_time < 0.06 and not self.extra_effects.get('_impact_bursted', False):
            self.extra_effects['_impact_bursted'] = True
            burst_count = 10 + int(5 * intensity)
            for _ in range(burst_count):
                if len(self.extra_effects['impact_particles']) < (MAX_IMPACT_PARTICLES // 2):
                    angle = random.uniform(0, math.pi * 2)
                    speed = random.uniform(8, 26) * (0.8 + random.random() * 0.5)
                    self.extra_effects['impact_particles'].append({
                        'x': random.uniform(-12, 12),
                        'y': 6 + random.uniform(-3, 3),
                        'vx': math.cos(angle) * speed,
                        'vy': -abs(math.sin(angle) * speed),
                        'size': random.uniform(3, 6),
                        'life': random.uniform(0.4, 0.9),
                        'color': (255, random.randint(140, 200), 90)
                    })

        if 0.0 <= state_time < 0.12:
            self.extra_effects['aura_alpha'] = clamp(int(160 * intensity), 0, 255)

        if state_time > 0.28:
            self.scale = damp(self.scale, 1.0, 6.0, dt)
            self.glow_intensity = damp(self.glow_intensity, 0.2, 6.0, dt)

    def _update_frame_animation(self, dt):
        self.frame_timer += dt
        if self.frame_timer >= self.frame_delay:
            self.frame_timer = 0.0
            self.current_frame_index = (self.current_frame_index + 1) % 8

    def _update_extra_effects(self, dt):
        for s in self.extra_effects['sparkle_positions'][:]:
            s['life'] -= dt * s.get('speed', 1.0)
            if 'size' in s:
                s['size'] *= (1.0 - 0.98 * dt)
            if s['life'] <= 0:
                self.extra_effects['sparkle_positions'].remove(s)

        for p in self.extra_effects['trail_particles'][:]:
            p['life'] -= dt * (1.0 + p.get('speed', 0.0))
            if 'size' in p:
                p['size'] *= (1.0 - 0.95 * dt)
            if p['life'] <= 0:
                self.extra_effects['trail_particles'].remove(p)

        if self.extra_effects.get('aura_alpha', 0) > 0:
            self.extra_effects['aura_alpha'] = max(0, self.extra_effects['aura_alpha'] - int(800 * dt))

        for ep in self.extra_effects['electric_particles'][:]:
            ep.update(dt)
            if ep.life <= 0:
                self.extra_effects['electric_particles'].remove(ep)

        for w in self.extra_effects['shockwaves'][:]:
            w.update(dt)
            if w.life <= 0 or w.radius > w.max_radius * 1.5:
                self.extra_effects['shockwaves'].remove(w)

        for line in self.extra_effects['dash_lines'][:]:
            line['life'] -= dt
            line['width'] *= (1.0 - 1.8 * dt)
            if line['life'] <= 0:
                self.extra_effects['dash_lines'].remove(line)

        for ip in self.extra_effects['impact_particles'][:]:
            ip['life'] -= dt
            ip['x'] += ip.get('vx', 0) * dt
            ip['y'] += ip.get('vy', 0) * dt
            ip['vy'] += 120.0 * dt
            if 'size' in ip:
                ip['size'] *= (1.0 - 0.93 * dt)
            if ip['life'] <= 0:
                self.extra_effects['impact_particles'].remove(ip)

        for ai in self.extra_effects['afterimages'][:]:
            ai['life'] -= dt
            if ai['life'] <= 0:
                try:
                    self.extra_effects['afterimages'].remove(ai)
                except ValueError:
                    pass

        if self.extra_effects.get('hit_pause', 0.0) > 0.0:
            self.extra_effects['hit_pause'] = max(0.0, self.extra_effects['hit_pause'] - dt)

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
            'extra_effects': copy.deepcopy(self.extra_effects),
            'screen_shake_offset': self.extra_effects['screen_shake'].get_offset(),
            'state': self.state
        }

    def get_modified_color(self, base_color):
        r, g, b = base_color
        pulse = self.color_pulse
        energy = self.energy_pulse
        r = min(255, int(r * pulse))
        g = min(255, int(g * pulse))
        b = min(255, int(b * pulse))
        if self.state == 'dashing':
            r = min(255, int(r + 60 * energy))
            g = min(255, int(g + 45 * energy))
            b = min(255, int(b + 30 * energy))
        elif self.state == 'slamming':
            r = min(255, int(r + 120 * energy))
            g = min(255, int(g + 45 * energy))
            b = max(0, int(b - 25 * energy))
        glow = self.glow_intensity
        if glow > 0.5:
            r = min(255, int(r * (1.0 + (glow - 0.5) * 1.4)))
            g = min(255, int(g * (1.0 + (glow - 0.5) * 1.4)))
            b = min(255, int(b * (1.0 + (glow - 0.5) * 1.4)))
        return (r, g, b)

    def get_glow_color(self, base_color):
        r, g, b = base_color
        glow = self.glow_intensity
        r = min(255, int(r * (1.0 + glow * 1.0)))
        g = min(255, int(g * (1.0 + glow * 1.0)))
        b = min(255, int(b * (1.0 + glow * 1.0)))
        alpha = int(200 * clamp(glow, 0.0, 1.0))
        return (r, g, b, alpha)

    def trigger_impact(self, x, y):
        self.extra_effects['shockwaves'].append(ShockwaveLite(x, y, (255, 150, 100)))
        self.extra_effects['screen_shake'].shake(18.0, 0.28)

# ---------- TRAIL EFFECT ----------
class TrailEffect:
    def __init__(self, x, y, color, size, life=12):
        self.x = x
        self.y = y
        self.color = color
        self.size = size
        self.life = life
        self.max_life = life
        self.alpha = 255
        self.glow_size = size * 2.5
        self.rotation = random.uniform(0, math.pi * 2)
        self.rotation_speed = random.uniform(-0.5, 0.5)
        self.sparkles = []
        for _ in range(random.randint(2, 5)):
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(0.2, 1.0) * size
            self.sparkles.append({
                'angle': angle,
                'distance': dist,
                'size': random.uniform(0.3, 0.6) * size,
                'speed': random.uniform(0.8, 2.0),
                'alpha': random.randint(120, 200)
            })

    def update(self, camera_speed, dt=None):
        if dt is None:
            self.x -= camera_speed * 0.016
            self.life -= 1
        else:
            self.x -= camera_speed * dt
            self.life -= dt * 12.0

        self.alpha = int(255 * clamp(self.life / max(1, self.max_life), 0.0, 1.0))
        self.size = max(0.1, self.size * 0.96)
        self.glow_size = self.size * 2.5
        self.rotation += self.rotation_speed * 0.5
        for s in self.sparkles:
            s['angle'] += s['speed'] * 0.02

    def draw(self, surface):
        if self.life <= 0:
            return
        life_ratio = clamp(self.life / max(1, self.max_life), 0.0, 1.0)
        
        center = (int(self.x), int(self.y))
        
        # Glow
        for i in range(3, 0, -1):
            glow_size = int(self.glow_size * (i / 3.0))
            glow_alpha = int(80 * life_ratio * (i / 3.0))
            if glow_size > 0:
                pygame.draw.circle(surface, (*self.color, glow_alpha), center, glow_size)
        
        # Main body
        main_alpha = int(200 * life_ratio)
        pygame.draw.circle(surface, (*self.color, main_alpha), center, int(max(1, self.size)))
        
        # Sparkles
        for sp in self.sparkles:
            angle = sp['angle']
            dist = sp['distance'] * self.size
            sx = center[0] + math.cos(angle) * dist
            sy = center[1] + math.sin(angle) * dist
            sparkle_alpha = int(sp['alpha'] * life_ratio)
            pygame.draw.circle(surface, (255, 255, 255, sparkle_alpha), (int(sx), int(sy)), int(max(1, sp['size'])))