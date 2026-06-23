import random
import numpy as np
from deap import base, creator, tools
from multiprocessing import Pool, freeze_support
import pygame

from snake_env import SnakeEnv
from snake_render import SnakeRenderer

INPUT_SIZE = 9
HIDDEN_SIZE = 8
OUTPUT_SIZE = 3

GENOME_LENGTH = (
    INPUT_SIZE * HIDDEN_SIZE +
    HIDDEN_SIZE +
    HIDDEN_SIZE * OUTPUT_SIZE +
    OUTPUT_SIZE
)

PERFECT_FITNESS = 899 * 1000  # perfect game = 899 food * 1000 reward


class NeuralNet:
    def __init__(self, genome):
        idx = 0

        w1 = INPUT_SIZE * HIDDEN_SIZE
        b1 = HIDDEN_SIZE
        w2 = HIDDEN_SIZE * OUTPUT_SIZE
        b2 = OUTPUT_SIZE

        self.W1 = np.array(genome[idx:idx + w1]).reshape(HIDDEN_SIZE, INPUT_SIZE)
        idx += w1
        self.b1 = np.array(genome[idx:idx + b1])
        idx += b1
        self.W2 = np.array(genome[idx:idx + w2]).reshape(OUTPUT_SIZE, HIDDEN_SIZE)
        idx += w2
        self.b2 = np.array(genome[idx:idx + b2])

    def forward(self, x):
        h = np.tanh(self.W1 @ x + self.b1)
        o = self.W2 @ h + self.b2
        return int(np.argmax(o))


def evaluate(ind):
    env = SnakeEnv()
    brain = NeuralNet(ind)

    steps = 0
    max_steps = 3000

    while not env.dead and steps < max_steps:
        state = np.array(env.get_state(), dtype=float)
        action = brain.forward(state)
        env.ai_step(action)
        steps += 1

    fitness = (
        env.score * 1000.0 +        # MASSIVE reward for eating
        env.distance_reward * 5.0 + # strong reward for approaching food
        env.steps_survived * 0.001  # tiny reward for living
    )
    return (fitness,)


creator.create("FitnessMax", base.Fitness, weights=(1.0,))
creator.create("Individual", list, fitness=creator.FitnessMax)

toolbox = base.Toolbox()
toolbox.register("attr_float", random.uniform, -1.0, 1.0)
toolbox.register("individual", tools.initRepeat, creator.Individual,
                 toolbox.attr_float, GENOME_LENGTH)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)
toolbox.register("evaluate", evaluate)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("mutate", tools.mutGaussian, mu=0, sigma=0.3, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)


def watch(best):
    renderer = SnakeRenderer()
    env = SnakeEnv()
    brain = NeuralNet(best)

    running = True

    while running and not env.dead:
        state = np.array(env.get_state(), dtype=float)
        action = brain.forward(state)
        env.ai_step(action)

        # starvation exit
        if env.steps_since_food > 900:
            print("Viewer stopped: starvation timeout")
            break

        renderer.draw(env)

        # handle quit / space
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    print("Viewer skipped by user")
                    running = False


def evolve_forever(pop_size=600):
    pop = toolbox.population(n=pop_size)
    gen = 0

    while True:
        offspring = toolbox.select(pop, len(pop))
        offspring = list(map(toolbox.clone, offspring))

        for c1, c2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.5:
                toolbox.mate(c1, c2)
                del c1.fitness.values
                del c2.fitness.values

        for m in offspring:
            if random.random() < 0.3:
                toolbox.mutate(m)
                del m.fitness.values

        invalid = [ind for ind in offspring if not ind.fitness.valid]
        fits = toolbox.map(toolbox.evaluate, invalid)
        for ind, fit in zip(invalid, fits):
            ind.fitness.values = fit

        pop[:] = offspring

        best = tools.selBest(pop, 1)[0]
        print(f"Gen {gen:04d} | Best fitness: {best.fitness.values[0]:.2f}")

        # show every 50 generations
        if gen % 50 == 0 and gen > 0:
            print("Showing best snake...")
            watch(best)

        # perfect game
        if best.fitness.values[0] >= PERFECT_FITNESS:
            print("Perfect game achieved!")
            watch(best)
            break

        gen += 1


if __name__ == "__main__":
    freeze_support()

    pool = Pool()
    toolbox.register("map", pool.map)

    evolve_forever()

    pool.close()
    pool.join()
