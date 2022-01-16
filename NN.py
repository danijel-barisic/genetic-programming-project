from keras.models import Sequential
from keras.layers import Dense
import numpy as np
import pyswarms as ps

from Algorithm import Algorithm

LOSS = 'mse'

HIDDEN_COUNT1 = 5
HIDDEN_COUNT2 = 3


class Unit:
    def __init__(self, input_count, output_count, nn):
        self.nn = nn
        self.input_count = input_count
        self.output_count = output_count
        self.input_values = []
        self.output_values = []
        self.fitness = 0
        self.model = Sequential()
        self.create_network()

    def create_network(self):
        self.model.add(Dense(HIDDEN_COUNT1, activation='relu', input_dim=self.input_count, name="Dense1",
                             kernel_initializer='random_normal', bias_initializer='zeros'))
        self.model.add(Dense(HIDDEN_COUNT2, activation='sigmoid', name="Dense2",
                             kernel_initializer='random_normal', bias_initializer='zeros'))
        self.model.add(Dense(self.output_count, activation='sigmoid', name="Dense3",
                             kernel_initializer='random_normal', bias_initializer='zeros'))

        self.model.compile(optimizer='adam', loss=LOSS,
                           metrics=['mae'])

    def evaluate(self):
        # model.predict is the method responsible for calculating output value on your weighted NN depending on input

        y_pred = self.model.predict(np.array([self.input_values]))
        pred = list()
        for i in range(y_pred.size):
            pred.append(y_pred[0][i])

        self.output_values = pred

    def __lt__(self, other):
        return self


def fitness_func(swarm, **kwargs):
    """Method for unit/particle(?) fitness

    Inputs
    ------
    swarm: numpy.ndarray of shape (n_particles, dimensions)
        The swarm that will perform the search

    Returns
    -------
    numpy.ndarray of shape (n_particles, )
        The computed fitness for each particle
    """

    unit = kwargs["the_unit"]

    n_particles = swarm.shape[0]

    # negative fitness because pyswarms optimises for minimum
    return np.array([-unit.fitness] * n_particles)


def format_flat_weights(flat_weights, input_count, output_count):
    result_list = []

    tmp_array = np.empty((input_count, HIDDEN_COUNT1), dtype=np.float32)

    for i in range(input_count):
        tmp_array[i] = [flat_weights[i * HIDDEN_COUNT1 + j] for j in range(HIDDEN_COUNT1)]

    result_list.append(tmp_array)
    result_list.append(np.array([0.] * HIDDEN_COUNT1, dtype=np.float32))  # bias

    tmp_array = np.empty((HIDDEN_COUNT1, HIDDEN_COUNT2), dtype=np.float32)
    init_index = input_count * HIDDEN_COUNT1  # + HIDDEN_COUNT1

    for i in range(HIDDEN_COUNT1):
        tmp_array[i] = [flat_weights[init_index + i * HIDDEN_COUNT2 + j] for j in range(HIDDEN_COUNT2)]

    result_list.append(tmp_array)
    result_list.append(np.array([0.] * HIDDEN_COUNT2, dtype=np.float32))  # bias

    tmp_array = np.empty((HIDDEN_COUNT2, output_count), dtype=np.float32)
    init_index = init_index + HIDDEN_COUNT1 * HIDDEN_COUNT2  # + HIDDEN_COUNT2

    for i in range(HIDDEN_COUNT2):
        tmp_array[i] = [flat_weights[init_index + i * output_count + j] for j in range(output_count)]

    result_list.append(tmp_array)
    result_list.append(np.array([0.] * output_count, dtype=np.float32))  # bias

    return result_list


class NN(Algorithm):

    def __init__(self, input_count, output_count, population_size):
        Algorithm.__init__(self, input_count, output_count, population_size)

    # function which returns a randomly generated population
    def create_population(self):
        population = []
        for _ in range(self.population_size):
            population.append(Unit(self.input_count, self.output_count, self))
        return population

    # function which takes current population as a parameter, and returns evolved population
    def evolve_population(self, population):

        # PSO optimizes a function, and our NN represents one such function, mapping inputs (however many)
        # to outputs (currently 2 outputs). Each particle is more or less a list containing as many arguments
        # as there are dimensions, which are real numbers
        # representing individual weights of neurons in the NN, hence being a description of the NN.

        # Initialize swarm
        options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}

        # Call instance of PSO
        dimensions = self.input_count * HIDDEN_COUNT1 + HIDDEN_COUNT1 * HIDDEN_COUNT2 + \
                     HIDDEN_COUNT2 * self.output_count

        optimizer = ps.single.GlobalBestPSO(n_particles=100, dimensions=dimensions, options=options)

        for unit in population:
            # Perform optimization
            cost, pos = optimizer.optimize(fitness_func, iters=1000, the_unit=unit, )
            unit.model.set_weights(format_flat_weights(pos, unit.input_count, unit.output_count))

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
