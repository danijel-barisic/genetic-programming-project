
# INSTRUCTIONS for running neural network algorithm for protein warriors:
# 1) In config.json put INPUT_COUNT=2 (eating opponents is disabled for neural network, due complexity and slowness)
# 2) Run ProteinWarriorsNoEating.py

from keras.models import Sequential
from keras.layers import Dense
import numpy as np

from Algorithm import Algorithm
import json
from pso.optimizer import Optimizer

# Figure out how pso fits into the algorithm (whether you remember history, or you do it dynamically, or something
#   completely else that depends on NN's or sumn.)
# Figure out WHEN to apply pso, how to select the fittest (it's in evolve_population I think) etc.
# Finish the evaluate function of the unit, determine the appropriate args n arg shape, perhaps it's simply the input values,
# or no.
# Determine input array shapes by backtracking NN interface.

with open('./config.json') as f:
    config = json.load(f)

MAXIMUM_SPEED = config["MAXIMUM_SPEED"]
LOSS = 'mse'


class Unit:
    def __init__(self, input_count, output_count, nn):
        self.nn = nn
        self.input_count = input_count
        self.output_count = output_count
        self.input_values = []
        self.output_values = []
        self.fitness = 0
        # self.model = Sequential()
        # self.create_network()
        # self.train_samples = []  # samples (tuple of: input tuple of size input_count,
        # and output tuple of size output_count). This is history of movement n calculations of right moves.
        # self.x_train = []  # np.zeros((300,2))
        # self.y_train = []  # np.zeros((300,1))
        self.arr = np.zeros((2, 1))

    # def create_network(self):
    #     # self.model = Sequential()
    #     self.model.add(Dense(self.input_count, activation='relu', input_dim=2, name="Dense1"))
    #     # # self.model.add(Dense(3, activation='relu'))
    #     # self.model.add(Input())
    #     self.model.add(Dense(self.output_count, activation='sigmoid', name="Dense2"))
    #
    #     # self.model.add(Dense(4, activation='sigmoid', input_shape=(2,), use_bias=True))
    #     # self.model.add(Dense(4, activation='sigmoid', use_bias=True))
    #     # self.model.add(Dense(3, activation='softmax', use_bias=True))
    #     self.model.compile(optimizer='adam', loss=LOSS,
    #                        metrics=['mae'])  # TODO maybe other optimizer n loss, n do I need metrics?
    #     # or self.model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    def evaluate(self):

        # model.predict is the thing responsible for calculating output value on yo weighted NN applied on test data
        # (or even on train data, it's all data after all, but it makes sense to test on data that's not identical to
        # train data, to see that it really do be working
        # self.model.predict(....)

        correct_output = (MAXIMUM_SPEED, self.input_values[1])

        # self.x_train= np.append(self.x_train,tuple(self.input_values))
        # self.y_train = np.append(self.y_train,correct_output)
        # self.train_samples.append(())

        # self.x_train.append(tuple(self.input_values))
        # self.y_train.append(correct_output)

        self.nn.x_train.append(tuple(self.input_values))
        self.nn.y_train.append(correct_output)

        x = [[self.input_values[0], self.input_values[
            1]]]  # inner array is first sample, second inner array if it existed would be second sample,
        # members of the array are features, there are 2 features, angle n speed
        # for input_val in self.input_values:
        #     y.append([input_val[0],input_val[1]])

        # self.output_values = self.model.predict(self.arr) #error
        self.arr = np.array(x)

        y_pred = self.nn.model(self.arr) # shorthand for predict
        pred = list()
        for i in range(len(y_pred)):
            pred.append((np.argmax(y_pred[i])))

        pred.append(MAXIMUM_SPEED)
        self.output_values = pred

    def __lt__(self, other):
        return self


class NN(Algorithm):

    def __init__(self, input_count, output_count, population_size):
        Algorithm.__init__(self, input_count, output_count, population_size)
        self.model = Sequential()
        self.create_network()
        self.x_train = []
        self.y_train = []

    def create_network(self):
        self.model.add(Dense(self.input_count, activation='relu', input_dim=2, name="Dense1"))
        self.model.add(Dense(self.output_count, activation='sigmoid', name="Dense2"))
        self.model.compile(optimizer='adam', loss=LOSS,
                           metrics=['mae'])

    # function which returns a randomly generated population
    def create_population(self):
        population = []
        for _ in range(self.population_size):
            population.append(Unit(self.input_count, self.output_count, self))
        return population

    # # function which takes current population as a parameter, and returns evolved population
    # def evolve_population(self, population):
    #
    #     for i,unit in enumerate(population):
    #         pso = Optimizer(model=unit.model,
    #                         loss=LOSS,
    #                         n=5,  # Number of particles
    #                         acceleration=1.0,  # Contribution of recursive particle velocity (acceleration)
    #                         local_rate=0.6,  # Contribution of locally best weights to new velocity
    #                         global_rate=0.4)  # Contribution of globally best weights to new velocity
    #
    #         # print("Training unit " + str(i+1) +": ")
    #         # Train model on provided data
    #         pso.fit(unit.x_train, unit.y_train, steps=10, batch_size=20)
    #
    #     for unit in population:
    #         unit.x_train.clear()
    #         unit.y_train.clear()
    #
    #     return population

    # function which takes current population as a parameter, and returns evolved population
    def evolve_population(self, population):

        pso = Optimizer(model=self.model,
                        loss=LOSS,
                        n=5,  # Number of particles
                        acceleration=1.0,  # Contribution of recursive particle velocity (acceleration)
                        local_rate=0.6,  # Contribution of locally best weights to new velocity
                        global_rate=0.4)  # Contribution of globally best weights to new velocity

        # print("Training unit " + str(i+1) +": ")
        # Train model on provided data
        pso.fit(self.x_train, self.y_train, steps=20, batch_size=50)

        self.x_train.clear()
        self.y_train.clear()

        return population

    # function which takes a unit and its inputs as parameters, and returns the values that unit produces
    def calculate_values(self, unit, inputs):
        if len(inputs) != self.input_count:
            raise Exception

        unit.input_values = []
        unit.output_values = []
        for input in inputs:
            unit.input_values.append(input)

        unit.evaluate()  # calculate output values for the unit I believe, by using .predict( ... ) on model

        return tuple(unit.output_values)  # necessary for game movement I believe
