import os
import sys

import pygame
from collections import deque
import random

ASSET_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def asset(name):
    return os.path.join(ASSET_DIR, name)


pygame.init()
pygame.mixer.init()


start_sound = pygame.mixer.Sound(asset("gamestart-272829.mp3"))
start_sound.set_volume(0.7)

eat_sound = pygame.mixer.Sound(asset("eat-323883.mp3"))
eat_sound.set_volume(0.7)

pygame.mixer.music.load(asset("8bit-music-for-game-68698.mp3"))
pygame.mixer.music.set_volume(0.7)

win_sound = pygame.mixer.Sound(asset("winning-218995.mp3"))
win_sound.set_volume(0.8)

gameover_sound = pygame.mixer.Sound(asset("game-over-deep-male-voice-clip-352695.mp3"))
gameover_sound.set_volume(0.9)

start_sound.play()
MUSIC_STARTED = False
MUSIC_ALLOWED = True


TILE = 40
ROWS = 11
COLS = 12

SCREEN_W = COLS * TILE
SCREEN_H = ROWS * TILE
SCREEN = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Pac-Man BFS")


PAC_MOVE_TIME = 220
GHOST_MOVE_TIME = 265

FONT = pygame.font.SysFont("arial", 28, bold=True)


ghost_img = pygame.image.load(asset("ghost.png")).convert_alpha()
ghost_img = pygame.transform.scale(ghost_img, (36, 36))

apple_img = pygame.image.load(asset("cherry.png")).convert_alpha()
apple_img = pygame.transform.scale(apple_img, (28, 28))


def neighbors(r, c):
    for dr, dc in [(1,0), (-1,0), (0,1), (0,-1)]:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS and maze[nr][nc] != "█":
            yield (nr, nc)


def bfs(start, goal):
    q = deque([start])
    visited = {start: None}

    while q:
        cur = q.popleft()

        if cur == goal:
            break

        for nxt in neighbors(*cur):
            if nxt not in visited:
                visited[nxt] = cur
                q.append(nxt)

    if goal not in visited:
        return [start]

    path = []
    cur = goal
    while cur is not None:
        path.append(cur)
        cur = visited[cur]

    path.reverse()
    return path


def maze_is_valid():
    visited = set()
    q = deque([pac_start])
    visited.add(pac_start)

    while q:
        r, c = q.popleft()
        for nr, nc in neighbors(r, c):
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                q.append((nr, nc))

    walkable = [(r, c) for r in range(ROWS) for c in range(COLS) if maze[r][c] != "█"]

    if len(visited) < len(walkable):
        return False

    visited_g = set()
    q = deque([ghost_start])
    visited_g.add(ghost_start)

    while q:
        r, c = q.popleft()
        for nr, nc in neighbors(r, c):
            if (nr, nc) not in visited_g:
                visited_g.add((nr, nc))
                q.append((nr, nc))

    return pac_start in visited_g


def build_maze():
    global maze, pac_start, ghost_start, food_total

    while True:
        maze = [["." for _ in range(COLS)] for _ in range(ROWS)]

        for r in range(ROWS):
            maze[r][0] = "█"
            maze[r][COLS-1] = "█"
        for c in range(COLS):
            maze[0][c] = "█"
            maze[ROWS-1][c] = "█"

        pac_start = (1, 1)
        ghost_start = (9, 10)

        NUM_WALLS = 12
        inside_tiles = [
            (r, c)
            for r in range(1, ROWS-1)
            for c in range(1, COLS-1)
            if (r, c) not in (pac_start, ghost_start)
        ]

        wall_spots = random.sample(inside_tiles, NUM_WALLS)
        for r, c in wall_spots:
            maze[r][c] = "█"

        NUM_CHERRIES = 8
        floor_tiles = [(r, c) for r in range(ROWS) for c in range(COLS) if maze[r][c] == "."]

        cherry_spots = random.sample(floor_tiles, NUM_CHERRIES)
        for r, c in cherry_spots:
            maze[r][c] = "o"

        food_total = NUM_CHERRIES

        if maze_is_valid():
            break


class Entity:
    def __init__(self, row, col, move_time):
        self.row = row
        self.col = col
        self.x = col * TILE
        self.y = row * TILE

        self.moving = False
        self.target_row = row
        self.target_col = col
        self.move_time = move_time
        self.move_timer = 0

        self.dir = (0, 0)

        self.mouth_timer = 0
        self.mouth_open = True

    def update(self, dt):
        self.mouth_timer += dt
        if self.mouth_timer >= 120:
            self.mouth_open = not self.mouth_open
            self.mouth_timer = 0

        if not self.moving:
            return

        self.move_timer += dt
        progress = min(1, self.move_timer / self.move_time)

        self.x = (self.col * TILE) + (self.target_col - self.col) * TILE * progress
        self.y = (self.row * TILE) + (self.target_row - self.row) * TILE * progress

        if progress >= 1:
            self.row = self.target_row
            self.col = self.target_col
            self.x = self.col * TILE
            self.y = self.row * TILE
            self.moving = False

    def try_move(self, dr, dc):
        if self.moving:
            return

        nr = self.row + dr
        nc = self.col + dc

        if maze[nr][nc] == "█":
            return

        self.target_row = nr
        self.target_col = nc
        self.move_timer = 0
        self.moving = True
        self.dir = (dr, dc)


build_maze()

pac = Entity(*pac_start, PAC_MOVE_TIME)
ghost = Entity(*ghost_start, GHOST_MOVE_TIME)

pac.dir = (0, 1)
wanted_dir = (0, 1)

score = 0
game_over = False
game_won = False

bfs_path = []


def restart():
    global pac, ghost, score, game_over, game_won, wanted_dir
    global MUSIC_STARTED, MUSIC_ALLOWED, food_total, bfs_path

    build_maze()

    pac = Entity(*pac_start, PAC_MOVE_TIME)
    ghost = Entity(*ghost_start, GHOST_MOVE_TIME)

    pac.dir = (0, 1)
    wanted_dir = (0, 1)

    score = 0
    game_over = False
    game_won = False

    bfs_path = []

    pygame.mixer.music.stop()
    start_sound.play()
    MUSIC_STARTED = False
    MUSIC_ALLOWED = True


clock = pygame.time.Clock()

while True:
    dt = clock.tick(60)

    if MUSIC_ALLOWED and not MUSIC_STARTED and not pygame.mixer.get_busy():
        pygame.mixer.music.play(-1)
        MUSIC_STARTED = True

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if e.type == pygame.KEYDOWN:
            if e.key == pygame.K_r:
                restart()
            if e.key == pygame.K_UP:
                wanted_dir = (-1, 0)
            if e.key == pygame.K_DOWN:
                wanted_dir = (1, 0)
            if e.key == pygame.K_LEFT:
                wanted_dir = (0, -1)
            if e.key == pygame.K_RIGHT:
                wanted_dir = (0, 1)

    if not (game_over or game_won):

        if not pac.moving:
            pac.try_move(*wanted_dir)
        pac.update(dt)

        if maze[pac.row][pac.col] == "o":
            maze[pac.row][pac.col] = "."
            score += 1
            food_total -= 1
            eat_sound.play()

            if food_total == 0:
                game_won = True
                pygame.mixer.music.stop()
                win_sound.play()

        if not ghost.moving:
            path = bfs((ghost.row, ghost.col), (pac.row, pac.col))

            bfs_path = path[:]

            if len(path) > 1:
                nr, nc = path[1]
                ghost.try_move(nr - ghost.row, nc - ghost.col)

        ghost.update(dt)

        if abs(pac.x - ghost.x) < 20 and abs(pac.y - ghost.y) < 20:
            game_over = True
            pygame.mixer.music.stop()
            gameover_sound.play()
            MUSIC_ALLOWED = False

    SCREEN.fill((0, 0, 0))

    for (r, c) in bfs_path:
        cx = c * TILE + TILE//2
        cy = r * TILE + TILE//2
        pygame.draw.circle(SCREEN, (0, 255, 255), (cx, cy), 4)

    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] == "█":
                pygame.draw.rect(SCREEN, (0, 0, 255), (c*TILE, r*TILE, TILE, TILE))
            elif maze[r][c] == "o":
                SCREEN.blit(apple_img, (c*TILE + 9, r*TILE + 9))

    px = pac.x + TILE//2
    py = pac.y + TILE//2
    pygame.draw.circle(SCREEN, (255,255,0), (int(px), int(py)), 18)

    if pac.mouth_open:
        dr, dc = pac.dir
        if dc == 1:
            pygame.draw.polygon(SCREEN, (0,0,0), [(px,py),(px+20,py+12),(px+20,py-12)])
        elif dc == -1:
            pygame.draw.polygon(SCREEN, (0,0,0), [(px,py),(px-20,py+12),(px-20,py-12)])
        elif dr == -1:
            pygame.draw.polygon(SCREEN, (0,0,0), [(px,py),(px-12,py-20),(px+12,py-20)])
        elif dr == 1:
            pygame.draw.polygon(SCREEN, (0,0,0), [(px,py),(px-12,py+20),(px+12,py+20)])

    SCREEN.blit(ghost_img, (ghost.x + 5, ghost.y + 5))

    SCREEN.blit(FONT.render(f"Score: {score}", True, (255,255,255)), (10, 10))

    if game_over:
        msg = FONT.render("GAME OVER - Press R to Restart", True, (255,255,255))
        SCREEN.blit(msg, msg.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))

    if game_won:
        msg = FONT.render("YOU WIN! - Press R to Restart", True, (255,255,0))
        SCREEN.blit(msg, msg.get_rect(center=(SCREEN_W//2, SCREEN_H//2)))

    pygame.display.update()
