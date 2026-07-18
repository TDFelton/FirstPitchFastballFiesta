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

font = pygame.font.SysFont("bahnschrift", 36)

cur.execute("""SELECT * 
            FROM leaderboard2
            ORDER BY barrels(fastball) DESC
            LIMIT 15""")

leaderboard = cur.fetchall()

conn.close()

def init_db(conn):
    cur = conn.cursor()
    leaders = ("""
        CREATE TABLE IF NOT EXISTS barrels_ranking (
            player_id TEXT PRIMARY KEY,
            barrels INTEGER,
            barrels_fastballs INTEGER
        )
    """)
    cur.execute(leaders)
    cur.execute("SELECT COUNT(player_id) FROM barrels_ranking")
    if cur.fetchone()[0] == 0:
        cur.executemany("INSERT INTO barrels_ranking VALUES (?, ?, ?)", rows)
    conn.commit()

def fetch_leaders(conn, limit=15):
    cur = conn.cursor()
    cur.execute("""
                SELECT player_id, barrels, barrels_fastballs
                FROM barrels_ranking
                ORDER BY barrels DESC
                LIMIT ?
                """, (limit,))
    return cur.fetchall()


class Leaderboard():
    def __init__(self, leaders, width = 600, height = 600, x_rank = 240, x_name = 300, x_barrels = 480):
        self.leaders = leaders
        self.width = width
        self.height = height
        self.size = width,height
        self.x_rank = x_rank
        self.x_name = x_name
        self.x_barrels = x_barrels
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
        msg5 = self.font_head.render("BRL(FB)", True, (122,136,153))
        msg_rect5 = msg5.get_rect(topright = (self.x_barrels,head_y))
        self.static.blit(msg5, msg_rect5)
        pygame.draw.line(self.static,(44,49,59),(60, head_y + 24), (self.width - 60, head_y + 24))

        for rank, (name, barrels, barrel_fastballs) in enumerate(self.leaders, start = 1):
            y = self.rows_top + rank * self.row_height

            if rank % 2 == 1:
                    pygame.draw.rect(self.static, (24,27,34),
                                     (60, y-4, self.width - 120, self.row_height))


            rank_surf = self.font_row.render(f"{rank}.", True, (235,238,243))
            rank_rect = rank_surf.get_rect(topright=(self.x_rank,y))
            self.static.blit(rank_surf, rank_rect)

            name_surf = self.font_row.render(name, True, (235,238,243))
            name_rect = name_surf.get_rect(topleft=(self.x_name,y))
            self.static.blit(name_surf, name_rect)

            bar_surf = self.font_row.render(f"{barrels} ({barrel_fastballs})", True, (235,238,243))
            bar_rect = bar_surf.get_rect(topright=(self.x_barrels,y))
            self.static.blit(bar_surf, bar_rect)

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