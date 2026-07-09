import sys, pygame
pygame.init()
pygame.mixer.init()
import random, math

class VibratingSprite:
    def __init__(self, image, x_pos, y_pos, amplitude=5, speed=0.01):
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.amplitude = amplitude
        self.speed = speed
    
    def draw(self, surf):
        time = pygame.time.get_ticks() * self.speed
        offset_x = self.x_pos + (math.sin(time) * self.amplitude)
        offset_y = self.y_pos + (math.cos(time) * self.amplitude)
        surf.blit(self.image, (offset_x, offset_y))


class Particles:
    def __init__(self, x, y, color):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1, 3)
        self.x, self.y = x, y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.color = color
        self.life = 60

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.1 # gravity
        self.life -= 1
    
    def draw(self, surf):
        if self.life > 0:
            alpha = max(0, min(255, int((self.life / 60) * 255)))
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            pygame.draw.circle(s, (*self.color, alpha), (2, 2),2)
            surf.blit(s, (self.x, self.y))
    def still_alive(self, width, height):
        return self.life > 0 and -20 <= self.x <= width + 20 and -20 <= self.y <= height + 20