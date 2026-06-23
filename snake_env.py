import random

WIDTH = 600
HEIGHT = 600
CELL = 20


class SnakeEnv:
    def __init__(self):
        self.reset()

    def reset(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.dx = 0
        self.dy = 0
        self.segments = []
        self.score = 0
        self.steps_survived = 0
        self.steps_since_food = 0
        self.dead = False

        self.spawn_food()

        # distance reward
        self.prev_food_dist = abs(self.food_x - self.x) + abs(self.food_y - self.y)
        self.distance_reward = 0

    def spawn_food(self):
        empty = [
            (x, y)
            for x in range(0, WIDTH, CELL)
            for y in range(0, HEIGHT, CELL)
            if (x, y) != (self.x, self.y) and (x, y) not in self.segments
        ]
        self.food_x, self.food_y = random.choice(empty)

    def move(self):
        self.x += self.dx
        self.y += self.dy

    def update_segments(self):
        if self.segments:
            self.segments.insert(0, (self.x, self.y))
            self.segments.pop()

    def check_food(self):
        if self.x == self.food_x and self.y == self.food_y:
            if self.segments:
                self.segments.append(self.segments[-1])
            else:
                self.segments.append((self.x - self.dx, self.y - self.dy))

            self.score += 10
            self.spawn_food()
            self.steps_since_food = 0  # reset starvation timer

    def check_death(self):
        if self.x < 0 or self.x >= WIDTH or self.y < 0 or self.y >= HEIGHT:
            self.dead = True
        for seg in self.segments:
            if (self.x, self.y) == seg:
                self.dead = True

    def ai_step(self, action):
        dirs = [(0, -CELL), (CELL, 0), (0, CELL), (-CELL, 0)]
        current = dirs.index((self.dx, self.dy)) if (self.dx, self.dy) in dirs else 0

        # turn logic
        if action == 1:
            current = (current - 1) % 4
        elif action == 2:
            current = (current + 1) % 4

        self.dx, self.dy = dirs[current]

        self.update_segments()
        self.move()
        self.check_food()
        self.check_death()

        self.steps_survived += 1
        self.steps_since_food += 1

        # distance reward
        dist = abs(self.food_x - self.x) + abs(self.food_y - self.y)

        if dist < self.prev_food_dist:
            self.distance_reward += 5      # strong reward for approaching food
        else:
            self.distance_reward -= 3      # strong penalty for moving away

        # penalty for being far from food
        self.distance_reward -= dist * 0.001

        # tiny penalty for doing nothing (forward)
        if action == 0:
            self.distance_reward -= 0.2

        self.prev_food_dist = dist

        # starvation rule
        max_steps_without_food = (WIDTH // CELL) * (HEIGHT // CELL)  # 900
        if self.steps_since_food > max_steps_without_food:
            self.dead = True

    def get_state(self):
        head = (self.x, self.y)
        dirs = [(0, -CELL), (CELL, 0), (0, CELL), (-CELL, 0)]
        current = dirs.index((self.dx, self.dy)) if (self.dx, self.dy) in dirs else 0

        left = dirs[(current - 1) % 4]
        right = dirs[(current + 1) % 4]
        straight = dirs[current]

        def danger(d):
            nx = head[0] + d[0]
            ny = head[1] + d[1]
            if nx < 0 or nx >= WIDTH or ny < 0 or ny >= HEIGHT:
                return 1.0
            if (nx, ny) in self.segments:
                return 1.0
            return 0.0

        danger_s = danger(straight)
        danger_l = danger(left)
        danger_r = danger(right)

        dir_up = 1.0 if current == 0 else 0.0
        dir_right = 1.0 if current == 1 else 0.0
        dir_down = 1.0 if current == 2 else 0.0
        dir_left = 1.0 if current == 3 else 0.0

        food_dx = (self.food_x - self.x) / WIDTH
        food_dy = (self.food_y - self.y) / HEIGHT

        return [
            danger_s, danger_l, danger_r,
            dir_up, dir_right, dir_down, dir_left,
            food_dx, food_dy
        ]
