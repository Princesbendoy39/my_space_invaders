import pygame
import random
import math

class Bullet:
    def __init__(self, x, y, dx=0):
        self.x = x
        self.y = y
        self.dx = dx
        self.speed = 7.5  # Pinabagal para medyo slo-mo at lutang ang dating
        self.is_active = True
        self.particles = []
        self.energy_offset = random.random() * 10

    def update(self):
        self.x += self.dx
        self.y -= self.speed
        self.energy_offset += 0.2

        # Makulay at kumikinang na colorful particles sa paligid (Green, Blue, Purple, at White)
        for _ in range(4):
            self.particles.append([
                self.x + random.randint(-7, 7),
                self.y + random.randint(5, 25),
                random.randint(1, 4),
                random.choice([
                   
                    (255, 255, 255)   # Pure White Sparkle
                ]),
                255
            ])

        for p in self.particles:
            p[1] += 1.5  # Mas mabagal din ang galaw ng particles pababa
            p[4] -= 15   # Mas dahan-dahan ang pagka-fade para matagal makita

        self.particles = [p for p in self.particles if p[4] > 0]

        if self.y < -40:
            self.is_active = False

    def get_rect(self):
        return pygame.Rect(
            int(self.x - 4),
            int(self.y),
            8,
            24
        )

    def draw(self, screen):
        # 1. Colorful trailing particles
        for p in self.particles:
            s = pygame.Surface((10, 10), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p[3], p[4]), (5, 5), p[2])
            screen.blit(s, (int(p[0] - 5), int(p[1] - 5)))

        # 2. Outer plasma aura (Vibrant Purple / Blue mix)
        pygame.draw.ellipse(
            screen,
            (150, 30, 220),
            (int(self.x - 6), int(self.y), 12, 28)
        )

        # 3. Inner high-intensity energy body (Electric Blue)
        pygame.draw.ellipse(
            screen,
            (0, 180, 255),
            (int(self.x - 4), int(self.y + 2), 8, 24)
        )

        # 4. Core laser beam (Neon Green)
        pygame.draw.ellipse(
            screen,
            (50, 255, 120),
            (int(self.x - 2), int(self.y + 4), 4, 20)
        )

        # 5. Jagged lightning veins (Para kumikilat-kilat habang dahan-dahang lumilipad)
        for i in range(3):
            lx = self.x + math.sin(self.energy_offset + i * 2) * 5
            ly = self.y + (i * 8) + 4
            pygame.draw.line(
                screen,
                (255, 255, 255),
                (int(self.x), int(ly)),
                (int(lx), int(ly + 6)),
                2
            )

        # 6. Pinaka-sentro na puting kislap
        pygame.draw.line(
            screen,
            (255, 255, 255),
            (int(self.x), int(self.y + 6)),
            (int(self.x), int(self.y + 22)),
            2
        )