from Algorithm import Algorithm
from random import random, randrange
from math import sqrt

LEAF_CHANCE = 0.4
CONST_LEAF_CHANCE = 0.1
CONST_LEAF_RANGE = 10
A = 1
B = 10
MUTATION_CHANCE = 0.1
MUTATE_THIS_NODE_CHANCE = 0.5
CHOOSE_THIS_NODE_CHANCE = 0.5
RESULT_CHOOSE_CHANCE = 0.5

class AbsNode():
    def __lt__(self, other):
        return self

class AbsLeaf(AbsNode):
    pass

class Leaf(AbsLeaf):
    def __init__(self, unit):
        self.unit = unit
        self.input_index = randrange(unit.input_count)
        self.value = None
    def evaluate(self):
        self.value = self.unit.input_values[self.input_index]
    def copy(self):
        ret_val = Leaf(self.unit)
        ret_val.input_index = self.input_index
        ret_val.value = None
        return ret_val

class ConstLeaf(AbsLeaf):
    def __init__(self, unit):
        self.unit = unit
        self.value = randrange(-CONST_LEAF_RANGE, CONST_LEAF_RANGE + 1)
    def evaluate(self):
        pass
    def copy(self):
        ret_val = ConstLeaf(self.unit)
        ret_val.value = self.value
        return ret_val

class Plus(AbsNode):
    def __init__(self, unit):
        self.unit = unit
        self.subtrees = []
        self.children_count = 2
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x,y = self.subtrees[0].value, self.subtrees[1].value
        self.value = x + y
    def copy(self):
        ret_val = Plus(self.unit)
        self.children_count = 2
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val

class Minus(AbsNode):
    def __init__(self, unit):
        self.unit = unit
        self.subtrees = []
        self.children_count = 2
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x,y = self.subtrees[0].value, self.subtrees[1].value
        self.value = x - y
    def copy(self):
        ret_val = Minus(self.unit)
        self.children_count = 2
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val

class Times(AbsNode):
    def __init__(self, unit):
        self.unit = unit
        self.subtrees = []
        self.children_count = 2
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x,y = self.subtrees[0].value, self.subtrees[1].value
        self.value = x * y
    def copy(self):
        ret_val = Times(self.unit)
        self.children_count = 2
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val

class Divide(AbsNode):
    def __init__(self, unit):
        self.unit = unit
        self.subtrees = []
        self.children_count = 2
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x,y = self.subtrees[0].value, self.subtrees[1].value
        self.value = x / y if abs(y) >= 1 else x
    def copy(self):
        ret_val = Divide(self.unit)
        self.children_count = 2
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val

class Modulo(AbsNode):
    def __init__(self, unit):
        self.unit = unit
        self.subtrees = []
        self.children_count = 2
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x,y = self.subtrees[0].value, self.subtrees[1].value
        self.value = x % y if abs(y) >= 1 else x
    def copy(self):
        ret_val = Modulo(self.unit)
        self.children_count = 2
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val

class Negation(AbsNode):
    def __init__(self, unit):
        self.unit = unit
        self.subtrees = []
        self.children_count = 1
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x = self.subtrees[0].value
        self.value = -x
    def copy(self):
        ret_val = Negation(self.unit)
        self.children_count = 1
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val

class Square(AbsNode):
    def __init__(self, unit):
        self.unit = unit
        self.subtrees = []
        self.children_count = 1
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x = self.subtrees[0].value
        self.value = x**2
    def copy(self):
        ret_val = Square(self.unit)
        self.children_count = 1
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val

class Root(AbsNode):
    def __init__(self, unit):
        self.unit = unit
        self.subtrees = []
        self.children_count = 1
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x = self.subtrees[0].value
        self.value = sqrt(x) if x >= 0 else sqrt(-x)
    def copy(self):
        ret_val = Root(self.unit)
        self.children_count = 1
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val

class Branch(AbsNode):
    def __init__(self, unit):
        self.unit = unit
        self.subtrees = []
        self.children_count = 4
        self.value = None
    def evaluate(self):
        for subtree in self.subtrees:
            subtree.evaluate()
        x, y, z, w = self.subtrees[0].value, self.subtrees[1].value, self.subtrees[2].value, self.subtrees[3].value
        self.value = z if x < y else w
    def copy(self):
        ret_val = Branch(self.unit)
        self.children_count = 4
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val

class Unit:
    def __init__(self, input_count, output_count, gp, create_tree = True):
        self.input_count = input_count
        self.output_count = output_count
        self.inputs_values = []
        self.output_values = []
        self.fitness = 0
        self.gp = gp
        self.trees = []
        if create_tree:
            for _ in range(self.output_count):
                self.trees.append(self.create_tree())

    def create_tree(self):
        chance = random()
        if chance < LEAF_CHANCE:
            return Leaf(self)
        elif chance < LEAF_CHANCE + CONST_LEAF_CHANCE:
            return ConstLeaf(self)
        else:
            rand = randrange(len(self.gp.node_dict))
            node = self.gp.node_dict[rand](self)
            for _ in range(node.children_count):
                child = self.create_tree()
                node.subtrees.append(child)
            return node

class GP(Algorithm):
    def __init__(self, input_count, output_count, population_size):
        Algorithm.__init__(self, input_count, output_count, population_size)
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

    def calculate_values(self, unit, inputs):
        if len(inputs) != self.input_count:
            raise Exception

        unit.input_values = []
        unit.output_values = []
        for input in inputs:
            unit.input_values.append(input)

        for tree in unit.trees:
            tree.evaluate()
            unit.output_values.append(tree.value)

        return tuple(unit.output_values)

    def create_population(self):
        population = []
        for _ in range(self.population_size):
            population.append(Unit(self.input_count, self.output_count, self))
        return population

    def evolve_population(self, population):
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
                tree_index = randrange(unit.output_count)
                self.mutate(unit, unit.trees[tree_index])
                unit.trees[tree_index] = self.mutate(unit, unit.trees[tree_index])

        return population

    def crossover(self, unit1, unit2):
        
        unit = Unit(self.input_count, self.output_count, self, create_tree=False)

        for i in range(unit.output_count):

            tree1 = unit1.trees[i]
            tree2 = unit2.trees[i]

            if random() < 0.5:
                tree1, tree2 = tree2, tree1

            tree2_component = self.choose_node_for_component(tree2).copy()

            tree1_result = None

            if isinstance(tree1, AbsLeaf):
                tree1_result = tree2_component

            else:
                tree1_copy = tree1.copy()
                tree1_result = self.mutate_and_create_result(tree1_copy, tree2_component)

            unit.trees.append(tree1_result)
        
        for tree in unit.trees:
            self.set_unit_object_in_tree(unit, tree)

        return unit

    def choose_node_for_component(self, tree):
        if isinstance(tree, AbsLeaf):
            return tree

        else:
            chance = random()
            if chance < CHOOSE_THIS_NODE_CHANCE:
                return tree
            else:
                sub_node_to_choose = randrange(tree.children_count)
                return self.choose_node_for_component(tree.subtrees[sub_node_to_choose])

    def mutate_and_create_result(self, tree, new_subtree):
        sub_node_index = randrange(tree.children_count)
        if random() < RESULT_CHOOSE_CHANCE or isinstance(tree.subtrees[sub_node_index], AbsLeaf):
            tree.subtrees[sub_node_index] = new_subtree

        else:
            tree.subtrees[sub_node_index] = self.mutate_and_create_result(tree.subtrees[sub_node_index], new_subtree)
        
        return tree

    def mutate(self, unit, tree):

        if isinstance(tree, AbsLeaf):
            tree = unit.create_tree()

        else:
            chance = random()
            if chance < MUTATE_THIS_NODE_CHANCE:
                tree = unit.create_tree()
            else:
                tree_index = randrange(tree.children_count)
                tree.subtrees[tree_index] = self.mutate(unit, tree.subtrees[tree_index])

        return tree

    def set_unit_object_in_tree(self, unit, tree):
        tree.unit = unit
        if not isinstance(tree, AbsLeaf):
            for subtree in tree.subtrees:
                self.set_unit_object_in_tree(unit, subtree)