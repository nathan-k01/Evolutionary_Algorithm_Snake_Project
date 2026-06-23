import pygame
from snake_env import WIDTH, HEIGHT, CELL

GREEN = (0, 155, 0)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
WHITE = (255, 255, 255)
GREY = (100, 100, 100)


class SnakeRenderer:
    def __init__(self):
        pygame.init()
        self.win = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake AI Viewer")
        self.clock = pygame.time.Clock()

    def draw(self, env):
        self.win.fill(GREEN)

        pygame.draw.rect(self.win, RED, (env.food_x, env.food_y, CELL, CELL))
        pygame.draw.rect(self.win, BLACK, (env.x, env.y, CELL, CELL))

        for seg in env.segments:
            pygame.draw.rect(self.win, GREY, (seg[0], seg[1], CELL, CELL))

        font = pygame.font.SysFont("Courier", 24)
        text = font.render(f"Score: {env.score}", True, WHITE)
        self.win.blit(text, (10, 10))

        pygame.display.update()
        self.clock.tick(15)
