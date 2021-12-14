#interface for modeling learning algorithms
class Algorithm:

    # constructor which takes number of inputs and number of outputs of one unit, and the number of units in population
    def __init__(self, inputs, outputs, population_size):
        self.inputs = inputs
        self.outputs = outputs
        self.population_size = population_size
    
    # function which returns a randomly generated population
    def create_population(self):
        pass

    # function which takes current population as a parameter, and returns evolved population
    def evolve_population(self, population):
        pass

    # function which takes a unit and its inputs as parameters, and returns the values that unit produces
    def calculate_value(self, unit, inputs):
        pass