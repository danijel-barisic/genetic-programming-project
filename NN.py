from keras.models import Sequential
from keras.layers import Dense
import numpy as np
import pyswarms as ps

from Algorithm import Algorithm

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

        self.model.compile(optimizer='adam', loss='mse',
                           metrics=['mae'])

    def evaluate(self):
        y_pred = self.model.predict(np.array([self.input_values]))
        pred = list()
        for i in range(y_pred.size):
            pred.append(y_pred[0][i])

        self.output_values = pred

    def __lt__(self, other):
        return self


def convert_flat_weights_to_nn_format(flat_weights, input_count, output_count):
    result_list = []

    tmp_array = np.empty((input_count, HIDDEN_COUNT1), dtype=np.float32)

    for i in range(input_count):
        tmp_array[i] = [flat_weights[i * HIDDEN_COUNT1 + j] for j in range(HIDDEN_COUNT1)]

    result_list.append(tmp_array)
    result_list.append(np.array([0.] * HIDDEN_COUNT1, dtype=np.float32))

    tmp_array = np.empty((HIDDEN_COUNT1, HIDDEN_COUNT2), dtype=np.float32)
    init_index = input_count * HIDDEN_COUNT1

    for i in range(HIDDEN_COUNT1):
        tmp_array[i] = [flat_weights[init_index + i * HIDDEN_COUNT2 + j] for j in range(HIDDEN_COUNT2)]

    result_list.append(tmp_array)
    result_list.append(np.array([0.] * HIDDEN_COUNT2, dtype=np.float32))

    tmp_array = np.empty((HIDDEN_COUNT2, output_count), dtype=np.float32)
    init_index = init_index + HIDDEN_COUNT1 * HIDDEN_COUNT2

    for i in range(HIDDEN_COUNT2):
        tmp_array[i] = [flat_weights[init_index + i * output_count + j] for j in range(output_count)]

    result_list.append(tmp_array)
    result_list.append(np.array([0.] * output_count, dtype=np.float32))

    return result_list


def fitness_func(swarm, **kwargs):
    population = kwargs["population"]
    n_particles = len(population)

    res = np.empty(shape=n_particles)

    for i, unit in enumerate(population):
        res[i] = -unit.fitness

    # The computed fitness for each particle.
    return res


class NN(Algorithm):

    def __init__(self, input_count, output_count, population_size):
        Algorithm.__init__(self, input_count, output_count, population_size)

    def create_population(self):
        population = []
        for _ in range(self.population_size):
            population.append(Unit(self.input_count, self.output_count, self))
        return population

    def evolve_population(self, population):

        options = {'c1': 0.5, 'c2': 0.3, 'w': 0.9}

        dimensions = self.input_count * HIDDEN_COUNT1 + HIDDEN_COUNT1 * HIDDEN_COUNT2 + \
                     HIDDEN_COUNT2 * self.output_count

        optimizer = ps.single.GlobalBestPSO(n_particles=self.population_size, dimensions=dimensions, options=options)

        stats = optimizer.optimize(fitness_func, iters=1000, population=population, )

        for i, unit in enumerate(population):
            pos = optimizer.swarm.position[i]
            unit.model.set_weights(convert_flat_weights_to_nn_format(pos, unit.input_count, unit.output_count))

        return population

    def calculate_values(self, unit, inputs):
        if len(inputs) != self.input_count:
            raise Exception

        unit.input_values = []
        unit.output_values = []
        for input in inputs:
            unit.input_values.append(input)

        unit.evaluate()

        return tuple(unit.output_values)
