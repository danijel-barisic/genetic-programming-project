import pygame
import random
import math
import json
import pickle

from GP import GP
from OutputDecoder import AngleDecoder, DirectionDecoder

class FoodEntity:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.colour = FOOD_COLOUR
		self.radius = DEFAULT_RADIUS

	def __str__(self):
		return f"Food location: {self.x}, {self.y}"

class WarriorEntity:
	def __init__(self, x, y, colour, unit):
		self.x = x
		self.y = y
		self.colour = colour
		self.unit = unit
		self.radius = DEFAULT_WARRIOR_RADIUS
		self.vision = DEFAULT_VISION_RANGE
		self.angle = random.randint(0, 360)
		self.food_in_range = []
		self.speed = MAXIMUM_SPEED
		self.score = 0
		self.traveled = 0 
		self.distance_to_food = DEFAULT_VISION_RANGE


	def increase_size(self):
		self.radius += 5
		self.vision += 5

	def __str__(self):
		return f"Warrior location: {self.x},{self.y} - Score: {self.score}"


with open('./config.json') as f:
    config = json.load(f)

# Pygame display values
DISPLAY_WIDTH  = config["DISPLAY_WIDTH"]
DISPLAY_HEIGHT = config["DISPLAY_HEIGHT"]

# RGB values of colours
BG_COLOUR 			= config["BG_COLOUR"]
FOOD_COLOUR 		= config["FOOD_COLOUR"]
ANGLE_COLOUR 		= config["ANGLE_COLOUR"]
ENTITY_COLOUR 		= config["ENTITY_COLOUR"]
VISION_RANGE_COLOUR = config["VISION_RANGE_COLOUR"]
OUR_ENTITY_COLOUR 	= config["OUR_ENTITY_COLOUR"]
TEXT_COLOUR 		= config["TEXT_COLOUR"]

DEFAULT_RADIUS 			= config["DEFAULT_RADIUS"]
DEFAULT_WARRIOR_RADIUS 	= config["DEFAULT_WARRIOR_RADIUS"]
DEFAULT_VISION_RANGE 	= config["DEFAULT_VISION_RANGE"] + DEFAULT_WARRIOR_RADIUS
NUMBER_OF_FOOD 			= config["NUMBER_OF_FOOD"]
NUMBER_OF_WARRIORS 		= config["NUMBER_OF_WARRIORS"]
MAXIMUM_SPEED 			= config["MAXIMUM_SPEED"]

#game lasts ~(NUMBER_OF_TICKS/TICK_SPEED) seconds  
NUMBER_OF_TICKS = config["NUMBER_OF_TICKS"]
TICK_SPEED 		= config["TICK_SPEED"]


gp = GP(2, 2, NUMBER_OF_WARRIORS)
angle_decoder = AngleDecoder()
direction_decoder = DirectionDecoder()
population = gp.create_population()


pygame.init()
gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('Protein Warriors')
clock = pygame.time.Clock()


# writes generation and time passed in top left corner
def write_time(gen, count):
	font = pygame.font.SysFont(None, 25)
	text = font.render(f"Generation: {gen} - Time passed: {count}", True, TEXT_COLOUR)
	gameDisplay.blit(text, (10, 10))


def draw_food(food):
	pygame.draw.circle(gameDisplay, food.colour, [food.x, food.y], food.radius, 0)

# also writes score next to the center of the circle
def draw_warrior(war):

	pygame.draw.circle(gameDisplay, VISION_RANGE_COLOUR, [war.x, war.y], war.vision, 1)
	pygame.draw.circle(gameDisplay, war.colour, [war.x, war.y], war.radius, 0)

	pygame.draw.line(gameDisplay, ANGLE_COLOUR, (war.x, war.y),
			(war.x + math.cos(math.radians(war.angle))* war.radius,
			 war.y + math.sin(math.radians(war.angle))* war.radius), 3)

	font = pygame.font.SysFont(None, 20)
	text = font.render(f"Score: {war.score}", True, TEXT_COLOUR)
	gameDisplay.blit(text, (war.x, war.y))


# if the player leaves the area, the game ends, only affects our player 
def leaving_boundaries(our_war):
	if our_war.x > DISPLAY_WIDTH - our_war.radius or our_war.x - our_war.radius < 0 \
		or our_war.y > DISPLAY_HEIGHT - our_war.radius or our_war.y - our_war.radius < 0:
			return True
	return False

# checks if the center of the entity has passed the edge of the screen
def warrior_boundaries(war):
	if war.x > DISPLAY_WIDTH:
		war.x -= DISPLAY_WIDTH
	elif war.x < 0:
		war.x += DISPLAY_WIDTH

	if war.y > DISPLAY_HEIGHT:
		war.y -= DISPLAY_HEIGHT
	elif war.y < 0:
		war.y += DISPLAY_HEIGHT

# calculates the distance between centers, we are squaring both sides because math.sqrt is an expensive call
def distance_between_centers_squared(ent1, ent2):
	return (ent2.x - ent1.x)*(ent2.x - ent1.x) + (ent2.y - ent1.y)*(ent2.y - ent1.y)

# usage in both vision range and radius
def distance_of_radii_squared(ent1r, ent2r):
	return (ent1r + ent2r)*(ent1r + ent2r)

# calculates distance between entities, slightly incorrect as it works with subtracting squared values
# could be changed if precise calculations need to be run and we use only non-squared values
def distance_between_circles(ent1, ent2):
	return distance_between_centers_squared(ent1, ent2) - distance_of_radii_squared(ent1.radius, ent2.radius)

# collision if sum of radii is bigger than distance between centers #sudar ako je suma 2 radijusa veca od udaljenosti 2 centra
def check_crossover(ent1, ent2):
	# squaring both sides save processing power and speeds up
	if distance_between_centers_squared(ent1, ent2) <= distance_of_radii_squared(ent1.radius, ent2.radius):
		return True
	return False

def check_crossover_vision(ent1, ent2):
	# squaring both sides save processing power and speeds up
	if distance_between_centers_squared(ent1, ent2) <= distance_of_radii_squared(ent1.radius, ent2.vision):
		return True
	return False

def find_closest_food(war):
	#smallest_dist = (DISPLAY_HEIGHT+DISPLAY_WIDTH)*2
	smallest_dist = 99999
	closes_food = 0
	for idx, food in enumerate(war.food_in_range):
		dist = distance_between_circles(war, food)
		if dist < smallest_dist:
			smallest_dist = dist
			closes_food = idx

	war.food_in_range = war.food_in_range[closes_food]
	#war.distance_to_food = math.sqrt(smallest_dist)


# moving our entity
def check_player_events(x_change, y_change):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			gameExit = True

		if event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()
			food_ent = FoodEntity(pos[0], pos[1])

			food.append(food_ent)

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				x_change = -5
			if event.key == pygame.K_RIGHT:
				x_change = 5
			if event.key == pygame.K_UP:
				y_change = -5
			if event.key == pygame.K_DOWN:
				y_change = 5

		if event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
				x_change = 0
			if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
				y_change = 0

	return x_change, y_change


def game_loop():
	global population
	global gameDisplay

	# starting values for our entity
	# our_warrior_x = (DISPLAY_WIDTH * 0.45)
	# our_warrior_y = (DISPLAY_HEIGHT * 0.8)
	# our_warrior = WarriorEntity(our_warrior_x, our_warrior_y, OUR_ENTITY_COLOUR)
	#x_change, y_change = 0, 0

	gen = 1
	try:
		while True:
			# starting food
			food = []
			for i in range(NUMBER_OF_FOOD):
				random_x = random.randrange(20, DISPLAY_WIDTH-20)
				random_y = random.randrange(20, DISPLAY_HEIGHT-20)
				food_ent = FoodEntity(random_x, random_y)

				food.append(food_ent)


			warriors = []
			# create warrior entities
			for unit in population:
				random_x = random.randrange(20, DISPLAY_WIDTH-20)
				random_y = random.randrange(20, DISPLAY_HEIGHT-20)
				warrior_ent = WarriorEntity(random_x, random_y, ENTITY_COLOUR, unit)

				warriors.append(warrior_ent)


			gameExit = False
			for i in range(NUMBER_OF_TICKS):

				# needed to tell the OS that the program is running
				if i % 2 == 0:
					pygame.event.pump()
				
				if gameExit:	
					return


				################## drawing the simulation
				gameDisplay.fill(BG_COLOUR)
				

				################## checking player movements
				# x_change, y_change = check_player_events(x_change, y_change)
				# our_warrior.x += x_change
				# our_warrior.y += y_change
				# our_warrior.traveled += abs(x_change) + abs(y_change) 

				# player leaving boundaries ends game
				# if leaving_boundaries(our_warrior):
				# 	gameExit = True
				# draw_warrior(our_warrior)


				# needed to check our with in the crossover function
				#temp_wars_with_ours = warriors[:]
				# temp_wars_with_ours.append(our_warrior)

				if i % 2 == 0:
					# passing values to gp and changing based on output
					for w in warriors:
						output = list(gp.calculate_values(w.unit, [w.distance_to_food, w.angle]))
						w.speed = min(MAXIMUM_SPEED, direction_decoder.decode(output[0]))
						w.angle += angle_decoder.decode(output[1])


						x_travel = math.cos(math.radians(w.angle)) * w.speed
						y_travel = math.sin(math.radians(w.angle)) * w.speed
						w.x += x_travel
						w.y += y_travel

						# count traveled
						w.traveled += abs(x_travel) + abs(y_travel) 

						warrior_boundaries(w)

						# each iterations can have new foods be in range or get out of range 
						w.food_in_range = []
						w.distance_to_food = 0


					# each iterations can have new foods be in range or get out of range 
					# our_warrior.food_in_range = []
					# our_warrior.distance_to_food = 0

					################## checking if food in vision field
					eaten_food = []
					crossovers_to_check = [(food_ent, warrior_ent) for food_ent in food for warrior_ent in warriors]
					for pair in crossovers_to_check:
						if pair[0] in eaten_food:
							continue
						
						if check_crossover_vision(*pair):
							pair[1].food_in_range.append(pair[0])

						if check_crossover(*pair):

							eaten_food.append(pair[0])
							food.remove(pair[0])

							pair[1].score += 1
							pair[1].increase_size()


					for w in warriors:
						if len(w.food_in_range):
							# unlists the element
							if len(w.food_in_range) == 1:
								w.food_in_range = w.food_in_range[0]

							#finds the closes of N foods in vision field
							elif len(w.food_in_range) >= 2:
								find_closest_food(w)

							#w.angle = math.degrees(math.atan2(w.food_in_range.y - w.y, w.food_in_range.x - w.x))
							w.distance_to_food = math.sqrt(abs(distance_between_circles(w, w.food_in_range)))

						else:
							w.angle = 0
							w.distance_to_food = w.vision


					################## replenishing the food
					# potentially 2 or more food can be eaten in the same frame
					while(len(food) < NUMBER_OF_FOOD):
						random_x = random.randrange(20, DISPLAY_WIDTH-20)
						random_y = random.randrange(20, DISPLAY_HEIGHT-20)
						food_ent = FoodEntity(random_x, random_y)

						food.append(food_ent)

				for f in food:
					draw_food(f)

				for w in warriors:
					draw_warrior(w)

				write_time(gen, i)
				pygame.display.update()
				clock.tick(TICK_SPEED)
			
			best_fitness = 0
			best_unit = 0
			for w in warriors:
				w.unit.fitness = w.score
				if w.score > best_fitness:
					best_fitness = w.score
					best_unit = w.unit.trees
			
			print(f'Generation {gen} ended - best fitness: {best_fitness}') #- best unit: {pickle.dumps(best_unit)}
			gen += 1
			population = gp.evolve_population(population)

	except Exception as e:
		print(e)
		pygame.quit()
		exit()


if __name__ == '__main__':
	game_loop()
	pygame.quit()

