import pygame
import random
from collections import deque
from copy import deepcopy

# Game configuration
SIZE = 4
TILE_SIZE = 100
MARGIN = 10
WINDOW_SIZE = SIZE * (TILE_SIZE + MARGIN) + MARGIN

# Colors
BG_COLOR = (187, 173, 160)
EMPTY_COLOR = (205, 193, 180)
TEXT_COLOR = (119, 110, 101)

# Tile colors
TILE_COLORS = {
    2: (238, 228, 218),
    4: (237, 224, 200),
    8: (242, 177, 121),
    16: (245, 149, 99),
    32: (246, 124, 95),
    64: (246, 94, 59),
    128: (237, 207, 114),
    256: (237, 204, 97),
    512: (237, 200, 80),
    1024: (237, 197, 63),
    2048: (237, 194, 46),
}

# Directions
ACTIONS = {
    pygame.K_UP: 'UP',
    pygame.K_w: 'UP',
    pygame.K_DOWN: 'DOWN',
    pygame.K_s: 'DOWN',
    pygame.K_LEFT: 'LEFT',
    pygame.K_a: 'LEFT',
    pygame.K_RIGHT: 'RIGHT',
    pygame.K_d: 'RIGHT'
}

class Game2048:
    def __init__(self, difficulty="medium"):
        self.size = SIZE
        self.board = [[0]*self.size for _ in range(self.size)]
        self.difficulty = difficulty
        self.add_tile()
        self.add_tile()

    def reset(self):
        self.board = [[0]*self.size for _ in range(self.size)]
        self.add_tile()
        self.add_tile()

    def add_tile(self):
        empty = [(i, j) for i in range(self.size) for j in range(self.size) if self.board[i][j] == 0]
        if empty:
            i, j = random.choice(empty)
            r = random.random()
            if self.difficulty == "easy":
                self.board[i][j] = 2 if r < 0.7 else 4   # 70% 2, 30% 4
            elif self.difficulty == "medium":
                self.board[i][j] = 2 if r < 0.8 else 4   # 80% 2, 20% 4
            elif self.difficulty == "hard":
                self.board[i][j] = 2 if r < 0.9 else 4   # 90% 2, 10% 4

    def compress(self, row):
        new_row = [i for i in row if i != 0]
        new_row += [0]*(self.size - len(new_row))
        return new_row

    def merge(self, row):
        for i in range(self.size-1):
            if row[i] != 0 and row[i] == row[i+1]:
                row[i] *= 2
                row[i+1] = 0
        return row

    def move_left(self):
        moved = False
        new_board = []
        for idx, row in enumerate(self.board):
            row = self.compress(row)
            row = self.merge(row)
            row = self.compress(row)
            new_board.append(row)
            if row != self.board[idx]:
                moved = True
        self.board = new_board
        if moved:
            self.add_tile()
        return moved

    def rotate_clockwise(self):
        self.board = [list(row) for row in zip(*self.board[::-1])]

    def move(self, direction):
        moved = False
        if direction == 'LEFT':
            moved = self.move_left()
        elif direction == 'RIGHT':
            self.rotate_clockwise()
            self.rotate_clockwise()
            moved = self.move_left()
            self.rotate_clockwise()
            self.rotate_clockwise()
        elif direction == 'UP':
            self.rotate_clockwise()
            self.rotate_clockwise()
            self.rotate_clockwise()
            moved = self.move_left()
            self.rotate_clockwise()
        elif direction == 'DOWN':
            self.rotate_clockwise()
            moved = self.move_left()
            self.rotate_clockwise()
            self.rotate_clockwise()
            self.rotate_clockwise()
        return moved

    def game_over(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] == 0:
                    return False
                if i < self.size-1 and self.board[i][j] == self.board[i+1][j]:
                    return False
                if j < self.size-1 and self.board[i][j] == self.board[i][j+1]:
                    return False
        return True

# Drawing function
def draw_board(screen, game, font):
    screen.fill(BG_COLOR)
    for i in range(SIZE):
        for j in range(SIZE):
            value = game.board[i][j]
            rect_x = MARGIN + j * (TILE_SIZE + MARGIN)
            rect_y = MARGIN + i * (TILE_SIZE + MARGIN)
            rect = pygame.Rect(rect_x, rect_y, TILE_SIZE, TILE_SIZE)
            color = TILE_COLORS.get(value, EMPTY_COLOR)
            pygame.draw.rect(screen, color, rect)
            if value != 0:
                text_color = TEXT_COLOR if value <= 4 else (255, 255, 255)
                text = font.render(str(value), True, text_color)
                text_rect = text.get_rect(center=rect.center)
                screen.blit(text, text_rect)
    pygame.display.flip()

def draw_menu(screen, font):
    screen.fill(BG_COLOR)
    title = font.render("Select Difficulty", True, (0,0,0))
    easy = font.render("1. Easy", True, (0,0,0))
    medium = font.render("2. Medium", True, (0,0,0))
    hard = font.render("3. Hard", True, (0,0,0))
    screen.blit(title, (50, 50))
    screen.blit(easy, (50, 150))
    screen.blit(medium, (50, 250))
    screen.blit(hard, (50, 350))
    pygame.display.flip()

    difficulty = "medium"
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    difficulty = "easy"
                    waiting = False
                elif event.key == pygame.K_2:
                    difficulty = "medium"
                    waiting = False
                elif event.key == pygame.K_3:
                    difficulty = "hard"
                    waiting = False
    return difficulty

# Main loop
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
    pygame.display.set_caption("2048 Game")
    font = pygame.font.SysFont("Arial", 32, bold=True)
    clock = pygame.time.Clock()

    difficulty = draw_menu(screen, font)
    game = Game2048(difficulty)
    running = True

    while running:
        draw_board(screen, game, font)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key in ACTIONS:
                    game.move(ACTIONS[event.key])
                elif event.key == pygame.K_q:
                    running = False

        if game.game_over():
            print("Game Over!")
            running = False

        clock.tick(10)

    pygame.quit()

if __name__ == "__main__":
    main()
