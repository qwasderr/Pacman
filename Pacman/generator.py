
import random

def generate_maze_with_cycles(rows, cols, cycle_probability=0.1, max_cycles=10):
    maze = [[1 for _ in range(cols)] for _ in range(rows)]
    
    def in_bounds(x, y):
        return 1 <= x < rows - 1 and 1 <= y < cols - 1

    def dfs(x, y):
        directions = [(0, 2), (2, 0), (0, -2), (-2, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny) and maze[nx][ny] == 1: 
                maze[nx][ny] = 0
                maze[x + dx // 2][y + dy // 2] = 0
                dfs(nx, ny)

    start_x, start_y = random.randrange(1, rows, 2), random.randrange(1, cols, 2)
    maze[start_x][start_y] = 0
    dfs(start_x, start_y)
    
    cycles_added = 0
    while cycles_added < max_cycles:
        x = random.randrange(1, rows - 1, 2)
        y = random.randrange(1, cols - 1, 2)
        
        if maze[x][y] == 0: 
            directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
            random.shuffle(directions)
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if in_bounds(nx, ny) and maze[nx][ny] == 1:
                    maze[nx][ny] = 0
                    cycles_added += 1
                    break

    return maze

def place_pacman_and_ghosts(maze, num_ghosts=3):
    open_positions = [(x, y) for x in range(1, len(maze)-1) for y in range(1, len(maze[0])-1) if maze[x][y] == 0]
    
    pacman_pos = random.choice(open_positions)
    open_positions.remove(pacman_pos)
    
    ghost_positions = random.sample(open_positions, num_ghosts)
    
    return pacman_pos, ghost_positions

def write_maze_to_file(maze, pacman_pos, ghost_positions, filename="maps2.txt"):
    with open(filename, 'w') as f:
        for row in maze:
            f.write(''.join(str(cell) for cell in row) + '\n')
        f.write(f"pacman:{pacman_pos[1]},{pacman_pos[0]}\n")
        ghost_str = ';'.join([f"{pos[1]},{pos[0]}" for pos in ghost_positions])
        f.write(f"ghosts:{ghost_str}\n")

#rows, cols = 19, 31
#maze = generate_maze_with_cycles(rows, cols, cycle_probability=0.3, max_cycles=40)
#pacman_pos, ghost_positions = place_pacman_and_ghosts(maze)
#write_maze_to_file(maze, pacman_pos, ghost_positions, filename="maps2.txt")
