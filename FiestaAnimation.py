import sys, pygame
pygame.init()
pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.init()
import random, math
import subprocess, os
from Fiesta_Classes import VibratingSprite, Particles

directory_now = os.path.dirname(os.path.realpath(__file__))

size = width, height = 600, 600
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
font = pygame.font.SysFont("bahnschrift", 36)

white = 255, 255, 255
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 225, 255), (225, 0, 225)]
infield_grass = (0, 128, 0)
outfield_grass = (0, 100, 0)
dirt = (165, 118, 52)
bases_lines = (255, 255, 255)

baseball = pygame.image.load("baseball.png")
celebration_sound = pygame.mixer.Sound("mariachi4.wav")
audio_file = os.path.join(directory_now, "mariachi4.wav")

frame_interval_ms = 50
filename_list = []
next_frame_time = 0
animation_timer = 0
animation_duration = 60
particle_count = []
t = 0.0
jump_t = 0
jump_count = 0
channel = None
running = True
animation_loop_seconds = 12
frame_counter = 0
    
def spawn_burst():
    x = random.randint(0, width)
    y = random.randint(0, height)
    color = random.choice(colors)
    return [Particles(x, y, color) for _ in range(50)]

def trigger_celebration(particle_count, animation_timer, t):
    if animation_timer > 0:
        animation_timer -= 1

    particle_count.extend(spawn_burst())
    for p in particle_count:
        p.update()
        p.draw(screen)
    particle_count = [p for p in particle_count if p.still_alive(width, height)]

    flash_on = (pygame.time.get_ticks() // 250) % 2 == 0
    if flash_on:
        msg = font.render("First Pitch Fastball Fiesta!", True, (255, 215, 0))
        msg_rect = msg.get_rect(center=(300, 40))
        screen.blit(msg, msg_rect)

    finished = hr_trot(screen, 300, 550, 450, t)
    hr_animation(screen, 300, 550, t/3, baseball)
    t += 0.005

    return particle_count, animation_timer, t, finished

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

def lerp(a,b,t):
    return a + (b-a) * t

def hr_trot(surf, c_x, c_y, size, t):
    finished = False
    if t < 4:
        bases = [
        (c_x, c_y),
        (c_x + size/2, c_y - size/2),
        (c_x, c_y - size),
        (c_x - size/2, c_y - size/2)
        ]
        leg = int(t % 4)
        start = bases[leg]
        end = bases[(leg + 1) % 4]
        pygame.draw.circle(surf, (0,0,0),(lerp(start[0],end[0],t-int(t)),lerp(start[1],end[1],t-int(t))),5)
    else:
        pygame.draw.circle(surf,(0,0,0), (c_x,c_y),5)
    return finished

def hr_animation(surf, c_x, c_y, t, baseball):
    p = min(t,1.0)
    arc_height = 300
    surf.blit(baseball,(lerp(c_x,120,p),lerp(c_y,-30,p)-arc_height * (math.sin(p*math.pi)** 0.5)))


while running:
    elapsed_time = pygame.time.get_ticks()
    screen.fill(white) 
    draw_diamond(screen, 300, 550, 450)
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            sys.exit()
    if channel is None:
        channel = celebration_sound.play(loops = -1)

    particle_count, animation_timer, t, finished = trigger_celebration(particle_count, animation_timer, t)
    if finished:
        channel.stop()
    if not finished and elapsed_time < animation_loop_seconds * 1000:
        if elapsed_time >= next_frame_time:
            filename = os.path.join(directory_now, 'temp[' + f"{frame_counter}" + '].png')
            pygame.image.save(screen, filename)
            filename_list.append(filename)
            frame_counter += 1
            next_frame_time += frame_interval_ms
    elif not finished:
        finished = True
        running = False

    t += 0.002
    pygame.display.flip()
    clock.tick(60)

command_list = ['ffmpeg', '-y', '-framerate', '20',
        '-i', os.path.join(directory_now, 'temp[%d].png'),
        '-pix_fmt', 'yuv420p', 
        '-vf', 'scale=trunc(iw/2)*2:trunc(ih/2)*2',
        '-crf', '18', 
        os.path.join(directory_now, 'anim.mp4')]
subprocess.call(command_list, cwd=directory_now)

audio_command = ['ffmpeg', '-y', '-stream_loop', '-1',
        '-i', audio_file,
        '-t', '15',
        '-c:a', 'pcm_s16le',
        os.path.join(directory_now, 'looped_audio.wav')
        ]

subprocess.call(audio_command, cwd=directory_now)

merge_command = ['ffmpeg', '-y',
        '-i', os.path.join(directory_now, 'anim.mp4'),
        '-i', os.path.join(directory_now, 'looped_audio.wav'),
        '-c:v', 'copy',
        '-c:a', 'aac',
        '-shortest',
    os.path.join(directory_now, 'anim_sound.mp4')
]
subprocess.call(merge_command, cwd=directory_now)

for filename in filename_list:
    os.remove(filename)
os.remove('anim.mp4')