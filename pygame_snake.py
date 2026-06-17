import pygame
import random
import sys
from multiprocessing import Process
import deap

# Initialize pygame
pygame.init()

# Window size
WIDTH, HEIGHT = 600, 600
CELL = 20

# Colors
GREEN = (0, 155, 0)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)

# Create window
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game (Pygame Edition)")

clock = pygame.time.Clock()


class SnakeGame:
    def __init__(self):
        self.high_score = 0
        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.dx = 0
        self.dy = 0
        self.segments = []
        self.score = 0
        self.delay = 10  # FPS

        self.spawn_food()

    def spawn_food(self):
        # Build a list of all empty grid cells
        empty_cells = [
            (x, y)
            for x in range(0, WIDTH, CELL)
            for y in range(0, HEIGHT, CELL)
            if (x, y) != (self.x, self.y) and (x, y) not in self.segments
        ]

        # If no empty cells exist, the player wins
        if not empty_cells:
            print("You filled the board! You win!")
            self.reset()
            return

        # Choose a random empty cell
        self.food_x, self.food_y = random.choice(empty_cells)

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def draw_snake(self):
        pygame.draw.rect(win, BLACK, (self.x, self.y, CELL, CELL))
        for seg in self.segments:
            pygame.draw.rect(win, GREY, (seg[0], seg[1], CELL, CELL))

    def draw_food(self):
        pygame.draw.rect(win, RED, (self.food_x, self.food_y, CELL, CELL))

    def update_segments(self):
        if len(self.segments) > 0:
            self.segments.insert(0, (self.x, self.y))
            self.segments.pop()

    def check_food_collision(self):
        if self.x == self.food_x and self.y == self.food_y:
            self.spawn_food()

            # Grow at the tail instead of the head
            if len(self.segments) > 0:
                tail = self.segments[-1]
                self.segments.append(tail)
            else:
                self.segments.append((self.x - self.dx, self.y - self.dy))

            self.score += 10
            self.delay += 0.2

    def check_border_collision(self):
        if self.x < 0 or self.x >= WIDTH or self.y < 0 or self.y >= HEIGHT:
            self.reset()

    def check_self_collision(self):
        for seg in self.segments:
            if self.x == seg[0] and self.y == seg[1]:
                self.reset()

    def draw_score(self):
        font = pygame.font.SysFont("Courier", 24)
        text = font.render(f"Score: {self.score}", True, WHITE)
        win.blit(text, (10, 10))

    def game_loop(self):
        running = True
        while running:
            clock.tick(self.delay)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_w and self.dy == 0:
                        self.dx, self.dy = 0, -CELL
                    elif event.key == pygame.K_s and self.dy == 0:
                        self.dx, self.dy = 0, CELL
                    elif event.key == pygame.K_a and self.dx == 0:
                        self.dx, self.dy = -CELL, 0
                    elif event.key == pygame.K_d and self.dx == 0:
                        self.dx, self.dy = CELL, 0

            self.update_segments()
            self.move()
            win.fill(GREEN)
            self.check_food_collision()
            self.check_border_collision()
            self.check_self_collision()
            self.draw_food()
            self.draw_snake()
            self.draw_score()
            pygame.display.update()


def run_game():
    SnakeGame().game_loop()

if __name__ == "__main__":
    p1 = Process(target=run_game)
    p2 = Process(target=run_game)

    p1.start()
    p2.start()

    p1.join()
    p2.join()