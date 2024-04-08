                
import pygame
from random import choice

# Define constants
RES = WIDTH, HEIGHT = 900, 700
TILE = 50
cols, rows = WIDTH // TILE, HEIGHT // TILE

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
BLUE = (30, 79, 91)

pygame.init()
sc = pygame.display.set_mode(RES)
clock = pygame.time.Clock()

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.original_image = pygame.image.load('player.png')
        self.image = pygame.transform.scale(self.original_image, (TILE, TILE))

    def draw(self):
        sc.blit(self.image, (self.x * TILE, self.y * TILE))

    def move(self, dx, dy):
        new_x = self.x + dx
        new_y = self.y + dy

        if 0 <= new_x < cols and 0 <= new_y < rows:
            if dx == 1 and not grid_cells[self.x + 1 + self.y * cols].walls['left']:  # Moving right
                self.x = new_x
            elif dx == -1 and not grid_cells[self.x - 1 + self.y * cols].walls['right']:  # Moving left
                self.x = new_x
            elif dy == 1 and not grid_cells[self.x + (self.y + 1) * cols].walls['top']:  # Moving down
                self.y = new_y
            elif dy == -1 and not grid_cells[self.x + (self.y - 1) * cols].walls['bottom']:  # Moving up
                self.y = new_y

class Cell:
    def __init__(self, x, y):
        self.x, self.y = x, y
        self.walls = {'top': True, 'right': True, 'bottom': True, 'left': True}
        self.visited = False

    def draw(self):
        x, y = self.x * TILE, self.y * TILE
        color = pygame.Color('#1e1e1e') if self.visited else pygame.Color('#d1d1d1')
        pygame.draw.rect(sc, color, (x, y, TILE, TILE), border_radius=10)

        if self.walls['top']:
            pygame.draw.line(sc, pygame.Color('#1e4f5b'), (x, y), (x + TILE, y), 3)
        if self.walls['right']:
            pygame.draw.line(sc, pygame.Color('#1e4f5b'), (x + TILE, y), (x + TILE, y + TILE), 3)
        if self.walls['bottom']:
            pygame.draw.line(sc, pygame.Color('#1e4f5b'), (x + TILE, y + TILE), (x, y + TILE), 3)
        if self.walls['left']:
            pygame.draw.line(sc, pygame.Color('#1e4f5b'), (x, y + TILE), (x, y), 3)

    def check_cell(self, x, y):
        find_index = lambda x, y: x + y * cols
        if x < 0 or x > cols - 1 or y < 0 or y > rows - 1:
            return False
        return grid_cells[find_index(x, y)]  

    def check_neighbors(self):
        neighbors = []
        top = self.check_cell(self.x, self.y - 1)
        right = self.check_cell(self.x + 1, self.y)
        bottom = self.check_cell(self.x, self.y + 1)
        left = self.check_cell(self.x - 1, self.y)
        if top and not top.visited:
            neighbors.append(top)
        if right and not right.visited:
            neighbors.append(right)
        if bottom and not bottom.visited:
            neighbors.append(bottom)
        if left and not left.visited:
            neighbors.append(left)
        return choice(neighbors) if neighbors else False 

def remove_walls(current, next):
    dx = current.x - next.x
    if dx == 1:
        current.walls['left'] = False
        next.walls['right'] = False
    elif dx == -1:
        current.walls['right'] = False
        next.walls['left'] = False
    dy = current.y - next.y
    if dy == 1:
        current.walls['top'] = False
        next.walls['bottom'] = False
    elif dy == -1:
        current.walls['bottom'] = False
        next.walls['top'] = False

def draw_home_screen():
    # Draw background
    sc.fill(BLUE)
    
    # Draw title
    font = pygame.font.Font(None, 60)
    title_text = font.render("Maze Game", True, WHITE)
    title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    sc.blit(title_text, title_rect)

    # Draw buttons
    button_width, button_height = 200, 50
    play_button_rect = pygame.Rect((WIDTH - button_width) // 2, HEIGHT // 2, button_width, button_height)
    pygame.draw.rect(sc, GRAY, play_button_rect)
    font = pygame.font.Font(None, 40)
    play_text = font.render("Play", True, BLACK)
    play_text_rect = play_text.get_rect(center=play_button_rect.center)
    sc.blit(play_text, play_text_rect)

    exit_button_rect = pygame.Rect((WIDTH - button_width) // 2, HEIGHT // 2 + 100, button_width, button_height)
    pygame.draw.rect(sc, GRAY, exit_button_rect)
    exit_text = font.render("Exit", True, BLACK)
    exit_text_rect = exit_text.get_rect(center=exit_button_rect.center)
    sc.blit(exit_text, exit_text_rect)

    return play_button_rect, exit_button_rect

def main_game():
    current_cell = grid_cells[0]
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.move(0, -1)
                elif event.key == pygame.K_DOWN:
                    player.move(0, 1)
                elif event.key == pygame.K_LEFT:
                    player.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    player.move(1, 0)
        sc.fill(BLUE)
        for cell in grid_cells:
            cell.draw()

        player.draw()  # Draw the player on the screen

        next_cell = current_cell.check_neighbors()
        if next_cell:
            next_cell.visited = True
            stack.append(current_cell)
            remove_walls(current_cell, next_cell)
            current_cell = next_cell
        elif stack:
            current_cell = stack.pop()

        pygame.display.flip()
        clock.tick(60)

# Main loop
grid_cells = [Cell(col, row) for row in range(rows) for col in range(cols)]
stack = []
player = Player(0, 0)  # Initialize player at the starting position
while True:
    play_button_rect, exit_button_rect = draw_home_screen()
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if play_button_rect.collidepoint(event.pos):
                main_game()
            elif exit_button_rect.collidepoint(event.pos):
                exit()

