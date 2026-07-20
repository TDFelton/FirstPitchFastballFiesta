"""The Leaderboard
import the DB look at first pitches, then based on player_id as index the second column is first pitch barrels 
with first bitch barrels (fastballs) in parenthesis

build a class that reads in the db and pulls the necessary values
then a function building the leaderboad in pygame"""

import pygame
import sys
import sqlite3

conn = sqlite3.connect("barrels.db")
cur = conn.cursor()
pygame.init()
font = pygame.font.SysFont("bahnschrift", 36)


def fetch_leaders(conn, limit=15):
    cur = conn.cursor()
    cur.execute("""
                SELECT player_id, barrels, barrels_fastballs, fiestas
                FROM barrels_ranking
                GROUP BY player_id
                ORDER BY barrels DESC
                LIMIT ?
                """, (limit,))
    return cur.fetchall()


class Leaderboard():
    def __init__(self, leaders, width = 600, height = 600, x_rank = 40, x_name = 130, x_barrels = 370, x_fiestas = 500):
        self.leaders = leaders
        self.width = width
        self.height = height
        self.size = width,height
        self.x_rank = x_rank
        self.x_name = x_name
        self.x_barrels = x_barrels
        self.x_fiestas = x_fiestas
        self.font_title = pygame.font.SysFont("Oswald.ttf", 46)
        self.font_head = pygame.font.SysFont("Oswald.ttf", 30)
        self.font_row = pygame.font.SysFont("Oswald.ttf",18)
        self.screen = pygame.display.set_mode(self.size)
        self.row_height = 26
        self.rows_top = 186
        self.static = pygame.Surface(self.size).convert()
        self.build()

    def build(self):
        self.static.fill((18,20,26))
        msg1 = self.font_title.render("First Pitch Barrel Leaders", True, (235, 238, 243))
        msg_rect = msg1.get_rect(center = (self.width//2,60))
        self.static.blit(msg1, msg_rect)

        msg2 = self.font_head.render("2025 SEASON     Qualified Hitters", True, (122,136,153))
        msg2_rect = msg2.get_rect(center = (self.width // 2, 92))
        self.static.blit(msg2,msg2_rect)

        head_y = 140
        msg3 = self.font_head.render("#", True, (122,136,153))
        msg_rect3 = msg3.get_rect(topright = (self.x_rank,head_y))
        self.static.blit(msg3, msg_rect3)
        msg4 = self.font_head.render("Player", True, (122,136,153))
        msg_rect4 = msg4.get_rect(topright = (self.x_name,head_y))
        self.static.blit(msg4, msg_rect4)
        msg5 = self.font_head.render("Barrels(On fastballs)", True, (122,136,153))
        msg_rect5 = msg5.get_rect(topright = (self.x_barrels,head_y))
        self.static.blit(msg5, msg_rect5)
        msg6 = self.font_head.render("Fiestas", True, (122,136,153))
        msg_rect6 = msg6.get_rect(topright = (self.x_fiestas,head_y))
        self.static.blit(msg6, msg_rect6)
        pygame.draw.line(self.static,(44,49,59),(60, head_y + 24), (self.width - 60, head_y + 24))

        for rank, (name, barrels, barrel_fastballs, fiestas) in enumerate(self.leaders, start = 1):
            y = self.rows_top + rank * self.row_height

            if rank % 2 == 1:
                    pygame.draw.rect(self.static, (24,27,34),
                                     (60, y-4, self.width - 120, self.row_height))


            rank_surf = self.font_row.render(f"{rank}.", True, (235,238,243))
            rank_rect = rank_surf.get_rect(topright=(self.x_rank,y))
            self.static.blit(rank_surf, rank_rect)

            name_surf = self.font_row.render(name, True, (235,238,243))
            name_rect = name_surf.get_rect(topleft=(self.x_name - 60,y))
            self.static.blit(name_surf, name_rect)

            bar_surf = self.font_row.render(f"{barrels} ({barrel_fastballs})", True, (235,238,243))
            bar_rect = bar_surf.get_rect(topright=(self.x_barrels - 180,y))
            self.static.blit(bar_surf, bar_rect)

            fiesta_surf = self.font_row.render(f"{fiestas}", True, (235,238,243))
            fiesta_rect = bar_surf.get_rect(topright=(self.x_fiestas - 50,y))
            self.static.blit(fiesta_surf, fiesta_rect)

    def draw(self):
        self.screen.blit(self.static, (0,0))

leaders = fetch_leaders(conn, limit=15)
board = Leaderboard(leaders)

running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT: 
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    board.draw()
    pygame.display.flip()
    clock.tick(60)


pygame.quit()
conn.close()