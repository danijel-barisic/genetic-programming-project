from math import sqrt
from random import randrange, random
from Algorithm import Algorithm
import json

with open('./config.json') as f:
    config = json.load(f)

OPERATOR_PARAMS = config["OPERATOR_PARAMS"] # 2 input + 1 output
MUTATION_CHANCE = config["MUTATION_CHANCE"]

LAYER_COUNT = config["LAYER_COUNT"]
LAYER_DEPTH = config["LAYER_DEPTH"]

A = config["A"]
B = config["B"]

class Unit:
    def __init__(self, input_count, output_count, cgp, create_genome=True):
        self.input_count = input_count
        self.output_count = output_count
        self.input_values = []
        self.output_values = []
        self.fitness = 0
        self.cgp = cgp
        self.genome = []
        if create_genome:
            self.random_initialize()

    def random_initialize(self):
        self.genome = [None] * (OPERATOR_PARAMS * (LAYER_COUNT * LAYER_DEPTH) + self.output_count)
        index = 0
        upper_limit = self.input_count

        # node generating
        for _ in range(LAYER_COUNT):
            for _ in range(LAYER_DEPTH):
                self.genome[index] = randrange(upper_limit) + 1
                self.genome[index + 1] = randrange(upper_limit) + 1
                self.genome[index + 2] = randrange(len(CGP.function_dict)) + 1
                index += 3
            upper_limit += LAYER_DEPTH

        # output generating
        for _ in range(self.output_count):
            self.genome[index] = randrange(upper_limit) + 1
            index += 1

    def evaluate(self):

        index = 1
        values = {}
        for i in range(len(self.input_values)):
            values[index] = self.input_values[i]
            index += 1

        genome_index = 0

        for _ in range(LAYER_COUNT * LAYER_DEPTH):
            function = CGP.function_dict[self.genome[genome_index + 2]]
            param1 = values[self.genome[genome_index]]
            param2 = values[self.genome[genome_index + 1]]
            values[index] = function(param1, param2)
            index += 1
            genome_index += OPERATOR_PARAMS

        for i in range(self.output_count):
            self.output_values.append(values[self.genome[genome_index + i]])

    def __lt__(self, other):
        return self

class CGP(Algorithm):

    f1 = lambda a, b : a + b
    f2 = lambda a, b : a - b
    f3 = lambda a, b : a * b
    f4 = lambda a, b : a / b if b != 0 else a
    f5 = lambda a, b : a % b if b != 0 else a
    f6 = lambda a, b : -a
    f7 = lambda a, b : a ** 2
    f8 = lambda a, b : sqrt(a) if a >= 0 else sqrt(-a)
    f9 = lambda a, b : randrange(-5, 6)

    function_dict = {
        1 : f1,
        2 : f2,
        3 : f3,
        4 : f4,
        5 : f5,
        6 : f6,
        7 : f7,
        8 : f8,
        9 : f9
    }

    def __init__(self, input_count, output_count, population_size):
        Algorithm.__init__(self, input_count, output_count, population_size)

    def calculate_values(self, unit, inputs):
        if len(inputs) != self.input_count:
            raise Exception

        unit.input_values = []
        unit.output_values = []
        for input in inputs:
            unit.input_values.append(input)

        unit.evaluate()

        return tuple(unit.output_values)

    def create_population(self):
        population = []
        for _ in range(self.population_size):
            population.append(Unit(self.input_count, self.output_count, self))
        return population

    def evolve_population(self, population):
        return self.algorithm_default(population)

    def crossover(self, unit1, unit2):
        
        unit = Unit(self.input_count, self.output_count, self, create_genome=False)

        crossover_point = randrange(1, len(unit1.genome) - 1)

        unit.genome = unit1.genome[:crossover_point].copy() + unit2.genome[crossover_point:].copy()

        return unit

    def mutate(self, unit):
        
        bit_to_change = randrange(len(unit.genome))

        if bit_to_change < LAYER_COUNT * LAYER_DEPTH * OPERATOR_PARAMS:
            if (bit_to_change + 1) % OPERATOR_PARAMS == 0:
                unit.genome[bit_to_change] = randrange(len(CGP.function_dict)) + 1
            else:
                unit.genome[bit_to_change] = randrange(int(bit_to_change / (LAYER_DEPTH * OPERATOR_PARAMS)) * LAYER_DEPTH + self.input_count) + 1

        else:
            unit.genome[bit_to_change] = randrange(self.input_count + LAYER_COUNT * LAYER_DEPTH) + 1
    
    def algorithm_default(self, population):
        objects = [[unit.fitness, unit] for unit in population]
        objects.sort()

        min_fitness = objects[0][0]
        max_fitness = objects[-1][0]

        for object in objects:
            object[0] = A + (B-A) * (object[0] - min_fitness)/(max_fitness - min_fitness)

        temp = 0

        for object in objects:
            x = object[0]
            object[0] += temp
            temp += x

        population = []

        for _ in range(self.population_size):

            unit1 = None
            unit2 = None

            r1 = random() * objects[-1][0]
            r2 = random() * objects[-1][0]

            index1 = 0
            index2 = 0

            while r1 > objects[index1][0]:
                index1 += 1

            while r2 > objects[index2][0]:
                index2 += 1

            unit1 = objects[index1][1]
            unit2 = objects[index2][1]

            population.append(self.crossover(unit1, unit2))

        for unit in population:
            if random() < MUTATION_CHANCE:
                self.mutate(unit)

        return population

    def algorithm_mutation_only(self, population):
        objects = [[unit.fitness, unit] for unit in population]
        objects.sort()

        min_fitness = objects[0][0]
        max_fitness = objects[-1][0]

        for object in objects:
            object[0] = A + (B-A) * (object[0] - min_fitness)/(max_fitness - min_fitness)

        temp = 0

        for object in objects:
            x = object[0]
            object[0] += temp
            temp += x

        population = []
        adjusted_size = self.population_size

        while self.population_size % 4 != 0: 
            adjusted_size -= 1
        
        added_units_num = self.population_size - adjusted_size
        upper_population_index = (3 / 4) * adjusted_size

        for index in range(upper_population_index, self.population_size):

            units = [None] * 4

            for unit in units:

                unit = objects[index][1]
                self.mutate(unit)
                population.append(unit)
        
        for _ in range(added_units_num):

            rand_unit = random.choice(population)
            population.append(rand_unit)

        return population