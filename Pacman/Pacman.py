from asyncio.windows_events import NULL
import pygame
import random
import math
import heapq
import pdb
import generator
from collections import deque
pygame.init()
pygame.font.init()
font = pygame.font.Font(None, 36) 
WIDTH, HEIGHT = 1000, 600
CELL_SIZE = 30
PACMAN_SPEED = 80
GHOST_SPEED = 1500
LIVES = 3

def create_map():
    rows, cols = 19, 31
    maze = generator.generate_maze_with_cycles(rows, cols, cycle_probability=0.3, max_cycles=40)
    pacman_pos, ghost_positions = generator.place_pacman_and_ghosts(maze)
    generator.write_maze_to_file(maze, pacman_pos, ghost_positions, filename="maps2.txt")
create_map()
def load_maps(filename):
    maps = []
    pacman_positions = []
    ghost_positions = []
    with open(filename, 'r') as file:
        current_map = []
        for line in file:
            line = line.strip()
            if not line:
                if current_map:
                    maps.append(current_map)
                current_map = []
            elif line.startswith("pacman:"):
                pacman = line.split(":")[1]
                pacman_pos = tuple(map(int, pacman.split(',')))
                pacman_positions.append(pacman_pos)
            elif line.startswith("ghosts:"):
                ghosts = line.split(":")[1]
                ghost_coords = [tuple(map(int, pos.split(','))) for pos in ghosts.split(';')]
                ghost_positions.append(ghost_coords)
            else:
                current_map.append([int(x) for x in line])   
        if current_map:
            maps.append(current_map)
    return maps, pacman_positions, ghost_positions

YELLOW = (255, 255, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
PURPLE = (240,0,255)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Pacman')
pacman_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
pacman_img.fill(YELLOW)
ghost_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
ghost_img.fill(RED)
ghost_bfs_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
ghost_bfs_img.fill(GREEN)
ghost_dfs_img = pygame.Surface((CELL_SIZE, CELL_SIZE))
ghost_dfs_img.fill(PURPLE)  
food_img = pygame.Surface((CELL_SIZE//2, CELL_SIZE//2))
food_img.fill(WHITE)

maps, pacman_positions, ghost_positions = load_maps('maps.txt') 
current_level = 0  
maze = maps[current_level]  
pacman_pos = list(pacman_positions[current_level])
ghost_pos = ghost_positions[current_level]
pacman_pos_1=pacman_pos.copy()
ghost_pos_1=[list(pos) for pos in ghost_pos]
#print(pacman_pos_1)
#print(ghost_pos_1)
ROWS, COLS = len(maze), len(maze[0])
food = [[1 if maze[row][col] == 0 else 0 for col in range(COLS)] for row in range(ROWS)]

def to_pixel(pos):
    return pos[0] * CELL_SIZE, pos[1] * CELL_SIZE

def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(maze, start, goal):
    queue = []
    heapq.heappush(queue, (0, start))
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0
    closed_set = set()
    while queue:
        current = heapq.heappop(queue)[1]
        if current == goal: 
            break
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_pos = (current[0] + dx, current[1] + dy)
            if (0 <= next_pos[0] < COLS and
                0 <= next_pos[1] < ROWS and
                maze[next_pos[1]][next_pos[0]] == 0 and
                next_pos not in closed_set):
                new_cost = cost_so_far[current] + 1
                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + heuristic(goal, next_pos)
                    heapq.heappush(queue, (priority, next_pos))
                    came_from[next_pos] = current
        closed_set.add(current)
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def bfs(maze, start, goal):
    queue = deque([start])
    visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
    visited[start[1]][start[0]] = True
    came_from = {}
    came_from[start] = None
    while queue:
        current = queue.popleft()
        if current == goal:
            break
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            next_pos = (current[0] + dx, current[1] + dy)
            if (0 <= next_pos[0] < COLS and 
                0 <= next_pos[1] < ROWS and 
                maze[next_pos[1]][next_pos[0]] == 0 and 
                not visited[next_pos[1]][next_pos[0]]):
                queue.append(next_pos)
                visited[next_pos[1]][next_pos[0]] = True
                came_from[next_pos] = current
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    return path

def dfs(maze, start, goal, visited_cell):
    stack = [start]
    visited = [[False for _ in range(COLS)] for _ in range(ROWS)]
    came_from = {}
    came_from[start] = None
    while stack:
        current = stack.pop()
        if current == goal:
            break
        if (not visited[current[1]][current[0]]):
            visited[current[1]][current[0]] = True
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                next_pos = (current[0] + dx, current[1] + dy)
                if (0 <= next_pos[0] < COLS and 
                    0 <= next_pos[1] < ROWS and 
                    maze[next_pos[1]][next_pos[0]] == 0 and 
                    not visited[next_pos[1]][next_pos[0]] and next_pos!=visited_cell):
                    stack.append(next_pos)
                    came_from[next_pos] = current
    current = goal
    path = []
    while current != start:
        path.append(current)
        current = came_from[current]
    path.reverse()
    print(path)
    return path
last_pacman_move_time = 0
def move_pacman(keys):
    global last_pacman_move_time
    current_time = pygame.time.get_ticks()
    if current_time - last_pacman_move_time >= PACMAN_SPEED:
        new_pos = pacman_pos[:]
        if keys[pygame.K_LEFT]:
            new_pos[0] -= 1
        if keys[pygame.K_RIGHT]:
            new_pos[0] += 1
        if keys[pygame.K_UP]:
            new_pos[1] -= 1
        if keys[pygame.K_DOWN]:
            new_pos[1] += 1
        if 0 <= new_pos[0] < COLS and 0 <= new_pos[1] < ROWS and maze[new_pos[1]][new_pos[0]] == 0:
            pacman_pos[:] = new_pos
            last_pacman_move_time = current_time

last_ghost_move_time = 0
visited_cell_dfs = NULL
def move_ghosts():
    global last_ghost_move_time, visited_cell_dfs
    current_time = pygame.time.get_ticks()
    if current_time - last_ghost_move_time >= GHOST_SPEED:
        next_positions = [] 
        path_a_star = astar(maze, (ghost_pos[0][0], ghost_pos[0][1]), (pacman_pos[0], pacman_pos[1]))
        if path_a_star:
            next_positions.append(path_a_star[0])
        path_bfs = bfs(maze, (ghost_pos[1][0], ghost_pos[1][1]), (pacman_pos[0], pacman_pos[1]))
        if path_bfs:
            next_positions.append(path_bfs[0])
        path_dfs = dfs(maze, (ghost_pos[2][0], ghost_pos[2][1]), (pacman_pos[0], pacman_pos[1]), visited_cell_dfs)
        if path_dfs:
            #if heuristic(list(ghost_pos[2]), list(pacman_pos)) < 10:
            #    path_dfs = bfs(maze, (ghost_pos[2][0], ghost_pos[2][1]), (pacman_pos[0], pacman_pos[1]))
            next_positions.append(path_dfs[0])
            visited_cell_dfs = ghost_pos[2]
        occupied_positions = set()
        for i, next_pos in enumerate(next_positions):
            if tuple(next_pos) not in occupied_positions:
                ghost_pos[i] = next_pos
                occupied_positions.add(tuple(next_pos))  
            else:
                pass
        last_ghost_move_time = current_time

def check_collision():
    for ghost in ghost_pos:
        if list(ghost) == pacman_pos:
            return True
    return False

def all_food_collected():
    for row in food:
        if 1 in row:
            return False
    return True

def next_level():
    global current_level, maze, food, pacman_pos, ghost_pos, ROWS, COLS, GHOST_SPEED
    current_level += 1
    if current_level < len(maps):
        maze = maps[current_level]
        pacman_pos = list(pacman_positions[current_level])
        ghost_pos = ghost_positions[current_level]
        ROWS, COLS = len(maze), len(maze[0])
        food = [[1 if maze[row][col] == 0 else 0 for col in range(COLS)] for row in range(ROWS)]
        GHOST_SPEED = GHOST_SPEED - 100
        pacman_pos_1 = pacman_pos.copy()
        ghost_pos_1 = [list(pos) for pos in ghost_pos]
        #print(ghost_pos)
        #print(current_level)
        #print(ROWS,COLS)
    else:
        print("You won")
        pygame.quit()
        pdb.set_trace()

def draw_lives(screen, lives):
    lives_text = font.render(f'Lives: {lives}', True, WHITE)
    screen.blit(lives_text, (10, 10))

running = True
clock = pygame.time.Clock()
lives = LIVES

while running:
    #print(pacman_pos_1)
    #print(ghost_pos_1)
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    if running:
        keys = pygame.key.get_pressed()
        move_pacman(keys)
        move_ghosts()
        if food[pacman_pos[1]][pacman_pos[0]] == 1:
            food[pacman_pos[1]][pacman_pos[0]] = 0
        if all_food_collected():
            next_level()
        if check_collision():
            lives -= 1
            if lives == 0:
                print("Game over")
                running = False
            else:
                pacman_pos=pacman_pos_1.copy()
                ghost_pos=[list(pos) for pos in ghost_pos_1]
        for row in range(ROWS):
            for col in range(COLS):
                color = BLUE if maze[row][col] == 1 else BLACK
                pygame.draw.rect(screen, color, pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                if food[row][col] == 1:
                    screen.blit(food_img, (col * CELL_SIZE + CELL_SIZE//4, row * CELL_SIZE + CELL_SIZE//4))
        screen.blit(pacman_img, to_pixel(pacman_pos))
        screen.blit(ghost_img, to_pixel(ghost_pos[0]))
        screen.blit(ghost_bfs_img, to_pixel(ghost_pos[1]))
        screen.blit(ghost_dfs_img, to_pixel(ghost_pos[2]))
        draw_lives(screen, lives)
        pygame.display.flip()
        clock.tick(60)
pygame.quit()
