from math import sqrt
from random import randrange, random, choice
from Algorithm import Algorithm
import json
import os
import shutil

with open('./config.json') as f:
    config = json.load(f)

OPERATOR_PARAMS = config["OPERATOR_PARAMS"] # 2 input + 1 output
MUTATION_CHANCE = config["MUTATION_CHANCE"]

LAYER_COUNT = config["LAYER_COUNT"]
LAYER_DEPTH = config["LAYER_DEPTH"]

A = config["A"]
B = config["B"]

FLOAT_INT_LIMIT = config["FLOAT_INT_LIMIT"]
CONST_LEAF_RANGE = config["CONST_LEAF_RANGE"]

DEFAULT_CGP = config["DEFAULT_CGP"]

def get_symbol(i):
    if i == 1:
        return "+"
    elif i == 2:
        return "-"
    elif i == 3:
        return "*"
    elif i == 4:
        return "/"
    elif i == 5:
        return "%"
    elif i == 6:
        return "neg"
    elif i == 7:
        return "^2"
    elif i == 8:
        return "sqrt"

def get_index(s):
    if s == "+":
        return 1
    elif s == "-":
        return 2
    elif s == "*":
        return 3
    elif s == "/":
        return 4
    elif s == "%":
        return 5
    elif s == "neg":
        return 6
    elif s == "^2":
        return 7
    elif s == "sqrt":
        return 8

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

    def f1(a, b):
        a = a if abs(a) < FLOAT_INT_LIMIT else int(a)
        b = b if abs(b) < FLOAT_INT_LIMIT else int(b)
        return a + b

    def f2(a, b):
        a = a if abs(a) < FLOAT_INT_LIMIT else int(a)
        b = b if abs(b) < FLOAT_INT_LIMIT else int(b)
        return a - b 

    def f3(a, b):
        a = a if abs(a) < FLOAT_INT_LIMIT else int(a)
        b = b if abs(b) < FLOAT_INT_LIMIT else int(b)
        return a * b

    def f4(a, b):
        a = a if abs(a) < FLOAT_INT_LIMIT else int(a)
        b = b if abs(b) < FLOAT_INT_LIMIT else int(b)
        return a / b if abs(b) >= 1 else a

    def f5(a, b):
        a = int(a)
        b = int(b)
        return a % b if abs(b) >= 1 else a

    def f6(a, b):
        a = a if abs(a) < FLOAT_INT_LIMIT else int(a)
        return -a

    def f7(a, b):
        a = a if abs(a) < FLOAT_INT_LIMIT else int(a)
        return a ** 2

    def f8(a, b):
        a = a if abs(a) < FLOAT_INT_LIMIT else int(a)
        return sqrt(a) if a >= 0 else sqrt(-a)

    function_dict = {
        1 : f1,
        2 : f2,
        3 : f3,
        4 : f4,
        5 : f5,
        6 : f6,
        7 : f7,
        8 : f8,
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
        if DEFAULT_CGP:
            return self.algorithm_default(population)
        else:
            return self.algorithm_mutation_only(population)

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

        if max_fitness != min_fitness:

            for object in objects:
                object[0] = A + (B-A) * (object[0] - min_fitness)/(max_fitness - min_fitness)

            temp = 0

            for object in objects:
                x = object[0]
                object[0] += temp
                temp += x

        else:

            curr = 1
            for object in objects:
                object[0] = curr
                curr += 1

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

        if max_fitness != min_fitness:

            for object in objects:
                object[0] = A + (B-A) * (object[0] - min_fitness)/(max_fitness - min_fitness)

            temp = 0

            for object in objects:
                x = object[0]
                object[0] += temp
                temp += x

        else:

            curr = 1
            for object in objects:
                object[0] = curr
                curr += 1

        population = []
        adjusted_size = self.population_size

        while adjusted_size % 4 != 0: 
            adjusted_size -= 1
        
        
        added_units_num = self.population_size - adjusted_size
        upper_population_index = int((3 / 4) * adjusted_size)

        for index in range(upper_population_index, self.population_size -1):
            
            units = [None] * 4

            for unit in units:

                unit = objects[index][1]
                self.mutate(unit)
                population.append(unit)
        
        for _ in range(added_units_num):
            rand_unit = choice(population)
            population.append(rand_unit)

        return population

    def save_population(self, population):
        
        dir_name = "CGP_population"
        if os.path.exists(dir_name):
            shutil.rmtree("CGP_population")
        
        os.mkdir("CGP_population")
        ind = 1

        for unit in population:
            genome = unit.genome
            f = open(f"CGP_population/unit_{ind}.txt", "w")
            for index in range(len(genome)):
                if index < LAYER_DEPTH * LAYER_COUNT * 3:
                    if index % 3 == 0:
                        f.write(f"({genome[index]}")
                    elif index % 3 == 1:
                        f.write(f", {genome[index]}")
                    else:
                        f.write(f", {get_symbol(genome[index])}) ")

                    if (index + 1) % (LAYER_DEPTH * 3) == 0:
                        f.write("\n")
                else:
                    f.write(f"{genome[index]} ")

            f.close()
            ind += 1

    def read_population(self):
        population = []

        dir_name = "CGP_population"
        for f in os.listdir(dir_name):
            unit = Unit(self.input_count, self.output_count, self, create_genome=False)
            genome = []

            file = open(f"CGP_population/{f}", "r")
            r = file.readlines()
            for j in range(len(r) - 1):
                line = r[j]
                line = line.rstrip().split(" ")
                line = [c.replace("(", "") for c in line]
                line = [c.replace(")", "") for c in line]
                line = [c.replace(",", "") for c in line]
                for i in range(len(line)):
                    if i % 3 == 2:
                        genome.append(get_index(line[i]))
                    else:
                        genome.append(int(line[i]))

            final_line = r[-1].rstrip().split(" ")
            for el in final_line:
                genome.append(int(el))

            unit.genome = genome
            population.append(unit)

        return population

if __name__ == "__main__":
    cgp = CGP(6, 2, 1)
    p = cgp.create_population()
    cgp.save_population(p)
    pop = cgp.read_population()