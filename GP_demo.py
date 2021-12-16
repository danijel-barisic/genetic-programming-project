from random import random
from GP import GP

# stvaranje objekta s kojim se upravlja radom algoritma
gp = GP(3, 3, 20)

# stvaranje inicijalne populacije
population = gp.create_population()

# simuliranje više iteracija
for j in range(1, 10):

    # ovako se pojedinoj jedinci ažurira fitness
    for unit in population:
        unit.fitness = random() * 10

    # stvaranje nove populacije na temelju postojeće
    population = gp.evolve_population(population)

    # ovako se izračunavaju izlazi iz jedinke - funkciji se kao parametar predaju jedinka, i lista ulaza
    for unit in population:
        print(gp.calculate_values(unit, [1,2,3]))