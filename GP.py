from math import sqrt
from random import randrange, random
from copy import deepcopy

# constants
POPULATION_SIZE = 10
POPULATION_CUTOFF = int(POPULATION_SIZE / 2)
POPULATION_CROSSOVER = int(POPULATION_SIZE / 4)
POPULATION_BEST_MUTATION = POPULATION_SIZE - POPULATION_CUTOFF - POPULATION_CROSSOVER
POPULATION_FILL = POPULATION_SIZE - POPULATION_CUTOFF
FUNCTION_ARGUMENT_COUNT = 3
VARIABLE_NAMES = {0 : "x", 1 : "y", 2 : "z", 3 : "w", 4 : "q"}
SPACE = "."
LEAF_CHANCE = 0.7
CONST_LEAF_CHANCE = 0
NODE_CHANCE = 1 - LEAF_CHANCE - CONST_LEAF_CHANCE
CROSSOVER_SWAP_CHANCE = 0.5
RESULT_CHOOSE_CHANCE = 0.6
COMPONENT_CHOOSE_CHANCE = 0.5
MUTATE_NODE_OR_CHILD_CHANCE = 0.6
FUNCTION_CHECK_ABS_VALUE = 2
MUTATE_COUNT = 10
BEST_MUTATE_COUNT = 5
GENERATION_PRINT_GAP = 50

# abstract class serving as base for every type of node
class AbsNode():
    def __lt__(self, other):
        return self

# abstract class serving as base for every type of leaf
class AbsLeaf(AbsNode):
    pass

# class for modeling variable leaves
class Leaf(AbsLeaf):
    def __init__(self):
        self.input_index = randrange(gp.input_count)
        self.value = None
    def evaluate(self):
        self.value = gp.inputs[self.input_index]
    def print(self, spaces):
        print(f"{spaces * SPACE}{VARIABLE_NAMES[self.input_index]}")

# class for modeling constant leaves
class ConstLeaf(AbsLeaf):
    def __init__(self):
        self.value = randrange(-10, 11)
    def evaluate(self):
        pass
    def print(self, spaces):
        print(f"{spaces * SPACE}{self.value}")

# class for modeling operator + nodes
class Plus(AbsNode):
    def __init__(self):
        self.subtrees = []
        self.children_count = 2
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x, y = self.subtrees[0].value, self.subtrees[1].value
        self.value = x + y
    def print(self, spaces):
        print(f"{spaces * SPACE}PLUS (+)")
        for subtree in self.subtrees:
            subtree.print(spaces + 1)

# class for modeling binary operator - nodes
class Minus(AbsNode):
    def __init__(self):
        self.subtrees = []
        self.children_count = 2
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x, y = self.subtrees[0].value, self.subtrees[1].value
        self.value = x - y
    def print(self, spaces):
        print(f"{spaces * SPACE}MINUS (-)")
        for subtree in self.subtrees:
            subtree.print(spaces + 1)

# class for modeling operator * nodes
class Times(AbsNode):
    def __init__(self):
        self.subtrees = []
        self.children_count = 2
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x, y = self.subtrees[0].value, self.subtrees[1].value
        self.value = x * y
    def print(self, spaces):
        print(f"{spaces * SPACE}TIMES (*)")
        for subtree in self.subtrees:
            subtree.print(spaces + 1)

# class for modeling operator / nodes
class Divide(AbsNode):
    def __init__(self):
        self.subtrees = []
        self.children_count = 2
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x, y = self.subtrees[0].value, self.subtrees[1].value
        self.value = x / y if y != 0 else 0
    def print(self, spaces):
        print(f"{spaces * SPACE}DIVIDE (/)")
        for subtree in self.subtrees:
            subtree.print(spaces + 1)

# class for modeling operator % nodes
class Modulo(AbsNode):
    def __init__(self):
        self.subtrees = []
        self.children_count = 2
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x, y = self.subtrees[0].value, self.subtrees[1].value
        self.value = x % y if y != 0 else 0
    def print(self, spaces):
        print(f"{spaces * SPACE}MODULO (%)")
        for subtree in self.subtrees:
            subtree.print(spaces + 1)

# class for modeling unary operator - nodes
class Negation(AbsNode):
    def __init__(self):
        self.subtrees = []
        self.children_count = 1
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x = self.subtrees[0].value
        self.value = -x
    def print(self, spaces):
        print(f"{spaces * SPACE}NEGATION (UNARY -)")
        for subtree in self.subtrees:
            subtree.print(spaces + 1)

# class for modeling square operation nodes
class Square(AbsNode):
    def __init__(self):
        self.subtrees = []
        self.children_count = 1
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x = self.subtrees[0].value
        self.value = x**2
    def print(self, spaces):
        print(f"{spaces * SPACE}SQUARE (^2)")
        for subtree in self.subtrees:
            subtree.print(spaces + 1)

# class for modeling square root operation nodes
class Root(AbsNode):
    def __init__(self):
        self.subtrees = []
        self.children_count = 1
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x = self.subtrees[0].value
        self.value = sqrt(x) if x >= 0 else sqrt(-x)
    def print(self, spaces):
        print(f"{spaces * SPACE}SQUARE_ROOT (sqrt)")
        for subtree in self.subtrees:
            subtree.print(spaces + 1)

# class for modeling branching
class Branch(AbsNode):
    def __init__(self):
        self.subtrees = []
        self.children_count = 4
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x, y, z, w = self.subtrees[0].value, self.subtrees[1].value, self.subtrees[2].value, self.subtrees[3].value
        self.value = z if x > y else w
    def print(self, spaces):
        print(f"{spaces * SPACE}BRANCH (? :)")
        for subtree in self.subtrees:
            subtree.print(spaces + 1)

# central class in algorithm
class GP:
    def __init__(self, input_count):
        self.input_count = input_count
        self.inputs = {}
        for i in range(input_count):
            self.inputs[i] = None
        self.population = []
        self.node_dict = {
            0 : Plus,
            1 : Minus,
            2 : Times,
            3 : Divide,
            4 : Modulo,
            5 : Negation,
            6 : Square,
            7 : Root,
            8 : Branch
        }

    def create_population(self):
        for _ in range(POPULATION_SIZE):
            node = self.create_unit()
            self.population.append(node)

    def create_unit(self):
        chance = random()
        if chance < LEAF_CHANCE:
            return Leaf()
        elif chance < LEAF_CHANCE + CONST_LEAF_CHANCE:
            return ConstLeaf()
        else:
            rand = randrange(len(gp.node_dict))
            node = gp.node_dict[rand]()
            for _ in range(node.children_count):
                child = self.create_unit()
                node.subtrees.append(child)
            return node

    def crossover(self, unit1, unit2):
        if random() < CROSSOVER_SWAP_CHANCE:
            unit1, unit2 = unit2, unit1

        component = deepcopy(gp.choose_node_component(unit2))

        if isinstance(unit1, AbsLeaf):
            result = component

        else:
            result, index = gp.choose_node_result(unit1)
            result = deepcopy(result)
            result.subtrees[index] = component

        return result

    def choose_node_result(self, unit):
        index = randrange(unit.children_count)
        if random() < RESULT_CHOOSE_CHANCE or isinstance(unit.subtrees[index], AbsLeaf):
            return unit, index
        else:
            return self.choose_node_result(unit.subtrees[index])

    def choose_node_component(self, unit):
        if isinstance(unit, Leaf) or isinstance(unit, ConstLeaf):
            return unit

        else:
            chance = random()
            if chance < COMPONENT_CHOOSE_CHANCE:
                return unit
            else:
                child_to_choose = randrange(unit.children_count)
                return self.choose_node_component(unit.subtrees[child_to_choose])

    def mutate(self, unit):

        if isinstance(unit, AbsLeaf):
            unit = self.create_unit()

        else:
            chance = random()
            if chance < MUTATE_NODE_OR_CHILD_CHANCE:
                unit = self.create_unit()
            else:
                child_to_mutate = randrange(unit.children_count)
                unit.subtrees[child_to_mutate] = self.mutate(unit.subtrees[child_to_mutate])

        return unit

# global variables
gp = GP(FUNCTION_ARGUMENT_COUNT)
f = lambda x, y, z : z - x * y - z * x

if __name__ == "__main__":

    gp.create_population()

    generation = 0
    solution = None

    while True:
        generation += 1
        p = []
        for x in range(len(gp.population)):
            unit = gp.population[x]
            error = 0
            for i in range(-FUNCTION_CHECK_ABS_VALUE, FUNCTION_CHECK_ABS_VALUE + 1):
                for j in range(-FUNCTION_CHECK_ABS_VALUE, FUNCTION_CHECK_ABS_VALUE + 1):
                    for k in range(-FUNCTION_CHECK_ABS_VALUE, FUNCTION_CHECK_ABS_VALUE + 1):
                        gp.inputs[0], gp.inputs[1], gp.inputs[2] = i, j, k
                        unit.evaluate()
                        error += abs(f(i,j,k) - unit.value)

            p.append([error, unit])

        p.sort()

        if generation % GENERATION_PRINT_GAP == 0:
            print(f'GENERATION {generation} : MIN ERROR {p[0][0]}')

        if p[0][0] == 0:
            solution = p[0][1]
            break

        p = p[:POPULATION_CUTOFF]
        gp.population = [i[1] for i in p]

        for _ in range(POPULATION_FILL):
            unit1 = gp.population[randrange(POPULATION_CUTOFF)]
            unit2 = gp.population[randrange(POPULATION_CUTOFF)]
            gp.population.append(gp.crossover(unit1, unit2))

        for _ in range(POPULATION_BEST_MUTATION):
            unit = deepcopy(gp.population[0])
            mutations = randrange(BEST_MUTATE_COUNT + 1)
            for _ in range(mutations):
                unit = gp.mutate(unit)
            gp.population.append(unit)

        for i in range(1, POPULATION_SIZE):
            mutations = randrange(MUTATE_COUNT + 1)
            for _ in range(mutations):
                gp.population[i] = gp.mutate(gp.population[i])

    print(f"\nGENERATION {generation}:")
    solution.print(0)