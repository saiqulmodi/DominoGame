"""
Domino Wonder Dash - Topple & Pop Mode (topplegame.py)
Physics-based domino chain reaction and acoustic topple simulation.
"""
import math
import time
import pygame

class ToppleTile:
    def __init__(self, x, y, angle=0.0):
        self.x = float(x)
        self.y = float(y)
        self.angle = angle        # path orientation angle (radians)
        self.tilt = 0.0           # 0.0 (upright) -> 1.0 (fully toppled)
        self.toppling = False
        self.toppled = False
        self.w = 16
        self.h = 42

class ToppleMode:
    def __init__(self, game):
        self.g = game
        self.tiles = []
        self.running = False
        self.cleared_at = 0
        self.popped = False
        self.pop_time = 0
        self.target_pos = (700, 350)
        self.reset_default_track()

    def reset_default_track(self):
        """Creates an initial inviting curve of dominoes ready to topple."""
        self.tiles = []
        self.running = False
        self.popped = False
        cx, cy = 180, 360
        r = 160
        for i in range(16):
            a = -math.pi * 0.4 + (i / 15.0) * math.pi * 0.8
            tx = cx + r * math.cos(a) + i * 22
            ty = cy + r * math.sin(a) * 0.6
            ang = a + math.pi / 2
            self.tiles.append(ToppleTile(tx, ty, ang))
        if self.tiles:
            last = self.tiles[-1]
            self.target_pos = (int(last.x + 50 * math.cos(last.angle)), int(last.y + 50 * math.sin(last.angle)))

    def clear(self):
        self.tiles = []
        self.running = False
        self.popped = False

    def add_tile_at(self, x, y):
        """Places a new domino aligned with the last tile placed."""
        if not self.tiles:
            self.tiles.append(ToppleTile(x, y, 0.0))
            return
        last = self.tiles[-1]
        dist = math.hypot(x - last.x, y - last.y)
        if dist >= 26:  # maintain consistent spacing so dominoes hit each other
            ang = math.atan2(y - last.y, x - last.x)
            last.angle = ang
            self.tiles.append(ToppleTile(x, y, ang))
            self.target_pos = (int(x + 50 * math.cos(ang)), int(y + 50 * math.sin(ang)))

    def start_topple(self):
        if self.tiles and not self.running:
            self.running = True
            self.tiles[0].toppling = True
            self.g.sfx.play("click")
            self.g.say("Go dominoes!", "डोमिनो गिरना शुरू!")

    def update(self, dt):
        if not self.running:
            return
        
        all_done = True
        for idx, t in enumerate(self.tiles):
            if t.toppling and not t.toppled:
                all_done = False
                t.tilt = min(1.0, t.tilt + dt * 4.5)
                # When tilted past 35%, trigger the next domino
                if t.tilt > 0.35 and idx + 1 < len(self.tiles):
                    next_t = self.tiles[idx + 1]
                    if not next_t.toppling and not next_t.toppled:
                        next_t.toppling = True
                        try:
                            self.g.sfx.play("pop")
                        except Exception:
                            pass
                if t.tilt >= 1.0:
                    t.toppled = True
            elif not t.toppled:
                all_done = False

        # When the final domino falls, trigger the target celebration pop
        if self.tiles and self.tiles[-1].toppled and not self.popped:
            self.popped = True
            self.pop_time = time.time()
            self.g.sfx.play("cheer")
            self.g.particles.confetti(pygame.Rect(self.target_pos[0] - 60, self.target_pos[1] - 60, 120, 120), n=100)
            self.g.say("Super topple!", "शानदार डोमिनो!")

    def handle_click(self, pos):
        x, y = pos
        # Check UI buttons on top bar
        if y < 70:
            if 20 <= x <= 140:
                self.start_topple()
                return True
            if 150 <= x <= 260:
                self.reset_default_track()
                return True
            if 270 <= x <= 370:
                self.clear()
                return True
            return False

        # If clicked near the first tile, trigger the start
        if self.tiles and not self.running:
            first = self.tiles[0]
            if math.hypot(x - first.x, y - first.y) < 35:
                self.start_topple()
                return True
        
        # Otherwise add a tile
        if not self.running:
            self.add_tile_at(x, y)
            return True
        return False

    def handle_drag(self, pos):
        if not self.running and pos[1] >= 80:
            self.add_tile_at(pos[0], pos[1])

    def draw(self, s, now):
        s.fill((28, 32, 45))
        
        # Grid lines for playground feel
        for gx in range(0, 960, 48):
            pygame.draw.line(s, (35, 40, 56), (gx, 80), (gx, 540), 1)
        for gy in range(80, 540, 48):
            pygame.draw.line(s, (35, 40, 56), (0, gy), (960, gy), 1)

        # Top Control Buttons
        # 1. Topple! button
        topple_col = (60, 180, 90) if not self.running else (100, 110, 120)
        pygame.draw.rect(s, topple_col, (20, 15, 120, 44), border_radius=8)
        pygame.draw.rect(s, (255, 255, 255), (20, 15, 120, 44), 2, border_radius=8)
        txt = self.g.font_at(18).render("▶ TOPPLE!", True, (255, 255, 255))
        s.blit(txt, txt.get_rect(center=(80, 37)))

        # 2. Reset Track
        pygame.draw.rect(s, (70, 120, 200), (150, 15, 110, 44), border_radius=8)
        pygame.draw.rect(s, (255, 255, 255), (150, 15, 110, 44), 2, border_radius=8)
        txt2 = self.g.font_at(16).render("↺ Reset", True, (255, 255, 255))
        s.blit(txt2, txt2.get_rect(center=(205, 37)))

        # 3. Clear Track
        pygame.draw.rect(s, (180, 70, 70), (270, 15, 100, 44), border_radius=8)
        pygame.draw.rect(s, (255, 255, 255), (270, 15, 100, 44), 2, border_radius=8)
        txt3 = self.g.font_at(16).render("✖ Clear", True, (255, 255, 255))
        s.blit(txt3, txt3.get_rect(center=(320, 37)))

        # Instructions banner
        inst = "Drag with finger or mouse to lay dominoes, then tap '▶ TOPPLE!' to launch!"
        itxt = self.g.small_font.render(inst, True, (210, 220, 240))
        s.blit(itxt, (390, 26))

        # Draw Target Balloon / Bell at track endpoint
        tx, ty = self.target_pos
        balloon_c = (255, 75, 75) if not self.popped else (180, 180, 180)
        pygame.draw.circle(s, balloon_c, (tx, ty - 18), 24)
        pygame.draw.polygon(s, balloon_c, [(tx - 6, ty + 6), (tx + 6, ty + 6), (tx, ty + 12)])
        pygame.draw.line(s, (200, 200, 200), (tx, ty + 12), (tx, ty + 36), 2)
        star_txt = self.g.font_at(16).render("★ GOAL", True, (255, 255, 255))
        s.blit(star_txt, star_txt.get_rect(center=(tx, ty - 18)))

        # Render Domino Tiles
        for idx, t in enumerate(self.tiles):
            # Dynamic tilt displacement
            cos_a = math.cos(t.angle)
            sin_a = math.sin(t.angle)
            tilt_shift = t.tilt * 22
            dx = t.x + tilt_shift * cos_a
            dy = t.y + tilt_shift * sin_a

            # Distinctive domino body (ivory face with wooden depth)
            color_theme = (245, 245, 235) if not t.toppled else (200, 200, 195)
            # Create a rotated surface for smooth realistic domino angle
            surf = pygame.Surface((t.w, t.h), pygame.SRCALPHA)
            surf.fill(color_theme)
            pygame.draw.rect(surf, (40, 40, 45), (0, 0, t.w, t.h), 2)
            pygame.draw.line(surf, (80, 80, 85), (2, t.h // 2), (t.w - 3, t.h // 2), 2)
            # Pip dots
            pygame.draw.circle(surf, (30, 30, 35), (t.w // 2, t.h // 4), 3)
            pygame.draw.circle(surf, (30, 30, 35), (t.w // 2, 3 * t.h // 4), 3)

            rot_deg = -math.degrees(t.angle) - (t.tilt * 48)
            rot_surf = pygame.transform.rotate(surf, rot_deg)
            s.blit(rot_surf, rot_surf.get_rect(center=(int(dx), int(dy))))

        # Push Hint on first domino
        if self.tiles and not self.running:
            first = self.tiles[0]
            pulse = abs(math.sin(now * 4)) * 6
            pygame.draw.circle(s, (255, 215, 0), (int(first.x), int(first.y)), int(22 + pulse), 2)
