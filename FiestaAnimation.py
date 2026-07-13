import sys, pygame
pygame.init()
pygame.mixer.init()
import random, math
from Fiesta_Classes import VibratingSprite, Particles

size = width, height = 600, 600
speed = [1, 1]
clock = pygame.time.Clock()
white = 255, 255, 255
screen = pygame.display.set_mode(size)
font = pygame.font.SysFont("bahnschrift", 32)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 225, 255), (225, 0, 225)]
infield_grass = (0, 128, 0)
outfield_grass = (0, 100, 0)
dirt = (165, 118, 52)
bases_lines = (255, 255, 255)
background = (91, 91, 91)
    
def spawn_burst():
    x = random.randint(0, width)
    y = random.randint(0, height)
    color = random.choice(colors)
    return [Particles(x, y, color) for _ in range(50)]

def real_time_hitting():
    #### This function is a placeholder for the feed of game_time events
    pass

def condition_met(event):
    #### This function is a placeholder for condition of first pitch homerun
    condition_one = event['ball_eventcode'] == 11
    condition_two = event['pitch_in_atbat'] == 1
    return condition_one and condition_two

#maracas1 = pygame.image.load("maracas2.png").convert_alpha()
#maracas_rect1 = maracas1.get_rect()
#maracas2 = pygame.image.load("maracas2.png").convert_alpha()
#maracas_rect2 = maracas2.get_rect()
#maracas1_sprite = VibratingSprite(maracas1, 100, 150)
#maracas2_sprite = VibratingSprite(maracas2, 500, 150)

#celebration_sound = pygame.mixer.Sound("Mariachi_Trimmed.wav")

animation_timer = 0
animation_duration = 60
particle_count = []
counter = 0
burst_delay = 20

def trigger_celebration():
    global animation_timer
    animation_timer = animation_duration
    flash_on = (pygame.time.get_ticks() // 250) % 2 == 0
    if animation_timer == 60:
        #celebration_sound.play()
        pass
    if animation_timer > 0:
        #maracas1_sprite.draw(screen)
        #maracas2_sprite.draw(screen)
        if flash_on:
            msg = font.render("First Pitch Fastball Fiesta!", True, (255, 215, 0))
            msg_rect = msg.get_rect(center=(320, 60))
            screen.blit(msg, msg_rect)

def draw_base(surf, bx, by, s = 8):
    r = (math.sqrt(2)) * s
    top = (bx, by - r)
    right = (bx + r, by)
    bottom = (bx, by + r)
    left = (bx - r, by)
    pygame.draw.polygon(surf,bases_lines, (top,right,bottom,left))
    pass

def draw_diamond(surf, c_x, c_y, size):
    bases = {
    "home": (c_x, c_y),
    "first": (c_x + size/2, c_y - size/2),
    "second": (c_x, c_y - size),
    "third": (c_x - size/2, c_y - size/2)
    }
    points = [
        bases["home"],
        bases["first"],
        bases["second"],
        bases["third"]
    ]
    square_bases = [
        bases["first"],
        bases["second"],
        bases["third"]
    ]
    screen.fill(outfield_grass)
    cx_d, cy_d = c_x, c_y - size/2
    dirt_pts = [(cx_d + ((x - cx_d) * 1.15), 
                cy_d + ((y - cy_d) * 1.15)) 
                for (x,y) in points]
    infield_pts = [(cx_d + ((x - cx_d) * .9), 
                cy_d + ((y - cy_d) * .9)) 
                for (x,y) in points]
    r = 20 / (2 * math.sin(math.pi/5))
    home_points = [
        (
            c_x + r * math.cos((-math.pi/2) + 2*math.pi * i/5),
            c_y + r * math.sin((-math.pi/2) + 2*math.pi * i/5)
        )
        for i in range(5)
    ]
    pygame.draw.polygon(surf, dirt, dirt_pts)
    pygame.draw.polygon(surf, infield_grass, infield_pts)
    for x,y in square_bases:
       draw_base(surf, x, y)
    pygame.draw.polygon(surf, bases_lines, home_points)
    
    home_v = pygame.math.Vector2(bases["home"])
    first_v = pygame.math.Vector2(bases["first"])
    third_v = pygame.math.Vector2(bases["third"])
    end_first = home_v + (first_v - home_v) * 2.5
    end_third = home_v + (third_v - home_v) * 2.5

    pygame.draw.line(surf, bases_lines, bases["home"], end_first)
    pygame.draw.line(surf, bases_lines, bases["home"], end_third)
    pass


while True:
    screen.fill(white) 
    draw_diamond(screen, 300, 550, 450)
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            sys.exit()
    
    if counter % burst_delay == 0:
        particle_count.extend(spawn_burst())
    for p in particle_count:
        p.update()
        p.draw(screen)
    particle_count = [p for p in particle_count if p.still_alive(width, height)]

    trigger_celebration()
    if animation_timer > 0:
        animation_timer -= 1
    pygame.display.flip()
    clock.tick(60)
