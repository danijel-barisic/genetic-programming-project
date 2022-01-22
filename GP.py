from ast import Mod
from logging import root
from pickle import POP
from Algorithm import Algorithm
from random import random, randrange
from math import sqrt
import json
import os
import shutil

with open('./config.json') as f:
	config_file = json.load(f)
	with open(config_file["config"]) as g:
		config = json.load(g)

LEAF_CHANCE = config["LEAF_CHANCE"]
CONST_LEAF_CHANCE = config["CONST_LEAF_CHANCE"]
CONST_LEAF_RANGE = config["CONST_LEAF_RANGE"]
A = config["A"]
B = config["B"]
MUTATION_CHANCE = config["MUTATION_CHANCE"]
MUTATE_THIS_NODE_CHANCE = config["MUTATE_THIS_NODE_CHANCE"]
CHOOSE_THIS_NODE_CHANCE = config["CHOOSE_THIS_NODE_CHANCE"]
RESULT_CHOOSE_CHANCE = config["RESULT_CHOOSE_CHANCE"]
MAX_NODE_COUNT = config["MAX_NODE_COUNT"]
START_WITH_GOOD_SEED = config["START_WITH_GOOD_SEED"]
GOOD_SEED_PERCENTAGE = config["GOOD_SEED_PERCENTAGE"]
FLOAT_INT_LIMIT = config["FLOAT_INT_LIMIT"]

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
    def generate(self, depth, file):
        file.write(f"{depth * ' '}i{self.input_index}\n")

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
    def generate(self, depth, file):
        file.write(f"{depth * ' '}c{self.value}\n")

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
        x = x if abs(x) < FLOAT_INT_LIMIT else int(x)
        y = y if abs(y) < FLOAT_INT_LIMIT else int(y)
        self.value = x + y
    def copy(self):
        ret_val = Plus(self.unit)
        self.children_count = 2
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val
    def generate(self, depth, file):
        file.write(f"{depth * ' '}+\n")
        for subtree in self.subtrees:
            subtree.generate(depth + 1, file)

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
        x = x if abs(x) < FLOAT_INT_LIMIT else int(x)
        y = y if abs(y) < FLOAT_INT_LIMIT else int(y)
        self.value = x - y
    def copy(self):
        ret_val = Minus(self.unit)
        self.children_count = 2
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val
    def generate(self, depth, file):
        file.write(f"{depth * ' '}-\n")
        for subtree in self.subtrees:
            subtree.generate(depth + 1, file)

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
        x = x if abs(x) < FLOAT_INT_LIMIT else int(x)
        y = y if abs(y) < FLOAT_INT_LIMIT else int(y)
        self.value = x * y
    def copy(self):
        ret_val = Times(self.unit)
        self.children_count = 2
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val
    def generate(self, depth, file):
        file.write(f"{depth * ' '}*\n")
        for subtree in self.subtrees:
            subtree.generate(depth + 1, file)

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
        x = x if abs(x) < FLOAT_INT_LIMIT else int(x)
        y = y if abs(y) < FLOAT_INT_LIMIT else int(y)
        self.value = x / y if abs(y) >= 1 else x
    def copy(self):
        ret_val = Divide(self.unit)
        self.children_count = 2
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val
    def generate(self, depth, file):
        file.write(f"{depth * ' '}/\n")
        for subtree in self.subtrees:
            subtree.generate(depth + 1, file)

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
        x = int(x)
        y = int(y)
        self.value = x % y if abs(y) >= 1 else x
    def copy(self):
        ret_val = Modulo(self.unit)
        self.children_count = 2
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val
    def generate(self, depth, file):
        file.write(f"{depth * ' '}%\n")
        for subtree in self.subtrees:
            subtree.generate(depth + 1, file)

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
        x = x if abs(x) < FLOAT_INT_LIMIT else int(x)
        self.value = -x
    def copy(self):
        ret_val = Negation(self.unit)
        self.children_count = 1
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val
    def generate(self, depth, file):
        file.write(f"{depth * ' '}neg\n")
        for subtree in self.subtrees:
            subtree.generate(depth + 1, file)
    
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
        x = x if abs(x) < FLOAT_INT_LIMIT else int(x)
        self.value = x**2
    def copy(self):
        ret_val = Square(self.unit)
        self.children_count = 1
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val
    def generate(self, depth, file):
        file.write(f"{depth * ' '}^2\n")
        for subtree in self.subtrees:
            subtree.generate(depth + 1, file)
    
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
        x = x if abs(x) < FLOAT_INT_LIMIT else int(x)
        self.value = sqrt(x) if x >= 0 else sqrt(-x)
    def copy(self):
        ret_val = Root(self.unit)
        self.children_count = 1
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val
    def generate(self, depth, file):
        file.write(f"{depth * ' '}root\n")
        for subtree in self.subtrees:
            subtree.generate(depth + 1, file)
    
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
        self.value = z if x > y else w
    def copy(self):
        ret_val = Branch(self.unit)
        self.children_count = 4
        self.value = None
        ret_val.subtrees = []
        for subtree in self.subtrees:
            ret_val.subtrees.append(subtree.copy())
        return ret_val
    def generate(self, depth, file):
        file.write(f"{depth * ' '}?\n")
        for subtree in self.subtrees:
            subtree.generate(depth + 1, file)
    
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

    def __lt__(self, other):
        return self

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

        if START_WITH_GOOD_SEED:
            for _ in range(int(self.population_size * GOOD_SEED_PERCENTAGE)):
                unit = Unit(self.input_count, self.output_count, self, create_tree=False)

                node1 = Leaf(unit)
                node1.input_index = 3
                node2 = ConstLeaf(unit)
                node2.value = 180
                node3 = Minus(unit)
                node3.subtrees = [node1, node2]
                node4 = Leaf(unit)
                node4.input_index = 4
                node5 = ConstLeaf(unit)
                node5.value = 0
                node6 = Leaf(unit)
                node6.input_index = 3
                node7 = Branch(unit)
                node7.subtrees = [node4, node5, node6, node3]
                node8 = Leaf(unit)
                node8.input_index = 5
                node9 = ConstLeaf(unit)
                node9.value = 0
                node10 = Leaf(unit)
                node10.input_index = 1
                tree1 = Branch(unit)
                tree1.subtrees = [node8, node9, node7, node10]

                node3 = ConstLeaf(unit)
                node3.value = 200
                node4 = Leaf(unit)
                node4.input_index = 4
                node5 = ConstLeaf(unit)
                node5.value = 0
                node6 = ConstLeaf(unit)
                node6.value = 200
                node7 = Branch(unit)
                node7.subtrees = [node4, node5, node6, node3]
                node8 = Leaf(unit)
                node8.input_index = 5
                node9 = ConstLeaf(unit)
                node9.value = 0
                node10 = ConstLeaf(unit)
                node10.value = 200
                tree2 = Branch(unit)
                tree2.subtrees = [node8, node9, node7, node10]

                unit.trees = [tree2, tree1]

                population.append(unit)

        while len(population) < self.population_size:
            population.append(Unit(self.input_count, self.output_count, self))
        return population

    def evolve_population(self, population):
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

        while len(population) < self.population_size:

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

            new_unit = self.crossover(unit1, unit2)

            if random() < MUTATION_CHANCE:
                tree_index = randrange(new_unit.output_count)
                self.mutate(new_unit, new_unit.trees[tree_index])
                new_unit.trees[tree_index] = self.mutate(new_unit, new_unit.trees[tree_index])

            if self.check_unit(new_unit):
                population.append(new_unit)

        return population

    def check_unit(self, unit):
        for tree in unit.trees:
            if self.count_nodes(tree) > MAX_NODE_COUNT:
                return False
        return True

    def count_nodes(self, tree):
        if isinstance(tree, AbsLeaf):
            return 1
        else:
            nodes = 0
            for tree in tree.subtrees:
                nodes += self.count_nodes(tree)
            return nodes

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

    def save_population(self, population):

        dir_name = "GP_population"
        if os.path.exists(dir_name):
            shutil.rmtree("GP_population")
        
        os.mkdir("GP_population")
        index = 1

        for unit in population:
            f = open(f"GP_population/unit_{index}.txt", "w")
            for tree in unit.trees:
                tree.generate(0, f)
                f.write("\n")
            f.close()
            index += 1

    def read_population(self):
        population = []
        
        dir_name = "GP_population"
        for f in os.listdir(dir_name):
            unit = Unit(self.input_count, self.output_count, self, create_tree=False)

            file = open(f"GP_population/{f}", "r")
            r = file.readlines()
            r = [a.rstrip() for a in r]
            
            active_nodes = []
            
            for line in r:
                if line == "":
                    if len(active_nodes) > 0:
                        unit.trees.append(active_nodes[0])
                    active_nodes = []

                else:
                    whitespace_count = 0
                    while line[0] == ' ':
                        whitespace_count += 1
                        line = line[1:]

                    node = None
                    
                    if line[0] == "i":
                        node = Leaf(unit)
                        node.input_index = int(line[1:])

                    elif line[0] == "c":
                        node = ConstLeaf(unit)
                        node.value = int(line[1:])

                    elif line == "+":
                        node = Plus(unit)

                    elif line == "-":
                        node = Minus(unit)

                    elif line == "*":
                        node = Times(unit)

                    elif line == "/":
                        node = Divide(unit)

                    elif line == "%":
                        node = Modulo(unit)

                    elif line == "neg":
                        node = Negation(unit)

                    elif line == "^2":
                        node = Square(unit)

                    elif line == "root":
                        node = Root(unit)

                    elif line == "?":
                        node = Branch(unit)

                    if len(active_nodes) == 0:
                        active_nodes.append(node)

                    else:
                        active_nodes[whitespace_count-1].subtrees.append(node)

                        if len(active_nodes) > whitespace_count:
                            active_nodes = active_nodes[:whitespace_count]
                            active_nodes.append(node)
                        else:
                            active_nodes.append(node)

            population.append(unit)

        return population

if __name__ == "__main__":
    gp = GP(6,2, 20)
    p = gp.create_population()
    gp.save_population(p)
    pop = gp.read_population()