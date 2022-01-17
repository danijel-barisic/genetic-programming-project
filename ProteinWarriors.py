import pygame
import random
import math
import json
import pickle
import string

from GP import GP
from CGP import CGP
from OutputDecoder import AngleDecoder, DirectionDecoder

class FoodEntity:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.colour = FOOD_COLOUR
		self.radius = DEFAULT_RADIUS * random.uniform(1,1.2)

	def __str__(self):
		return f"Food location: {self.x}, {self.y}"

class WarriorEntity:
	def __init__(self, x, y, colour, unit):
		self.x = x
		self.y = y
		self.colour = colour
		self.unit = unit
		self.radius = DEFAULT_WARRIOR_RADIUS * random.uniform(1,1.1)
		self.vision = DEFAULT_VISION_RANGE
		self.angle = random.randint(0, 360)
		self.angle_to_warrior = 0
		self.food_in_range = []
		self.warriors_in_range = []
		self.speed = MAXIMUM_SPEED
		self.score = 0
		self.enemy_score = 0
		self.enemy_in_sight = 0
		self.traveled = 0 
		self.distance_to_food = DEFAULT_VISION_RANGE
		self.distance_to_warrior = DEFAULT_VISION_RANGE


	def increase_size(self, increase_by):
		self.radius += increase_by
		self.vision += increase_by

	def __str__(self):
		return f"Warrior location: {self.x},{self.y} - Score: {self.score}"

	def __getstate__(self):
		return self.__dict__.copy()

with open('./config.json') as f:
	config = json.load(f)

# Pygame display values
DISPLAY_WIDTH  = config["DISPLAY_WIDTH"]
DISPLAY_HEIGHT = config["DISPLAY_HEIGHT"]
LEARNING_WITHOUT_VISUALS = config["LEARNING_WITHOUT_VISUALS"]

# RGB values of colours
BG_COLOUR 			= config["BG_COLOUR"]
FOOD_COLOUR 		= config["FOOD_COLOUR"]
ANGLE_COLOUR 		= config["ANGLE_COLOUR"]
ENTITY_COLOUR 		= config["ENTITY_COLOUR"]
VISION_RANGE_COLOUR = config["VISION_RANGE_COLOUR"]
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

WRITE_TO_FILE = config["WRITE_TO_FILE"]
FILE_NAME = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))

# writes generation and time passed in top left corner
def write_time(gameDisplay, gen, count):
	font = pygame.font.SysFont(None, 25)
	text = font.render(f"Generation: {gen} - Time passed: {count}", True, TEXT_COLOUR)
	gameDisplay.blit(text, (10, 10))


def draw_food(gameDisplay, food):
	pygame.draw.circle(gameDisplay, food.colour, [food.x, food.y], food.radius, 0)

# also writes score next to the center of the circle
def draw_warrior(gameDisplay, war):

	pygame.draw.circle(gameDisplay, VISION_RANGE_COLOUR, [war.x, war.y], war.vision, 1)
	pygame.draw.circle(gameDisplay, war.colour, [war.x, war.y], war.radius, 0)

	pygame.draw.line(gameDisplay, ANGLE_COLOUR, (war.x, war.y),
			(war.x + math.cos(math.radians(war.angle))* war.radius,
			 war.y + math.sin(math.radians(war.angle))* war.radius), 3)

	font = pygame.font.SysFont(None, 20)
	text = font.render(f"Score: {round(war.score, 3)}", True, TEXT_COLOUR)
	gameDisplay.blit(text, (war.x, war.y))

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

def check_crossover_warriors_vision(ent1, ent2):
	# squaring both sides save processing power and speeds up
	if distance_between_centers_squared(ent1, ent2) <= distance_of_radii_squared(ent1.vision, ent2.vision):
		return True
	return False

def find_closest_obj(war, objects_in_range):
	smallest_dist = 99999
	closes_idx = 0
	for idx, obj in enumerate(objects_in_range):
		dist = distance_between_circles(war, obj)
		if dist < smallest_dist:
			smallest_dist = dist
			closes_idx = idx
	
	return closes_idx

def game_loop(gameDisplay, population, gen, algorithm, EATING_MODE, angle_decoder, direction_decoder):
	try:
		clock = pygame.time.Clock()
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

			for i in range(NUMBER_OF_TICKS):
			
				if i % 2 == 1:
					# needed to tell the OS that the program is running
					pygame.event.pump()

					# passing values to algorithm and changing based on output
					for w in warriors:
						if not EATING_MODE:
							output = list(algorithm.calculate_values(w.unit, [w.distance_to_food, w.angle]))
						else:
							output = list(algorithm.calculate_values(w.unit, [w.distance_to_food, w.angle, w.distance_to_warrior, w.angle_to_warrior, w.score - w.enemy_score, w.enemy_in_sight]))
						w.speed = min(MAXIMUM_SPEED, direction_decoder.decode(output[0]))
						w.angle += angle_decoder.decode(output[1])


						x_travel = math.cos(math.radians(w.angle)) * w.speed
						y_travel = math.sin(math.radians(w.angle)) * w.speed
						w.x += x_travel
						w.y += y_travel

						# count traveled
						w.traveled += abs(x_travel) + abs(y_travel) 

						warrior_boundaries(w)

						# each iterations can have new foods or warriors be in range or get out of range 
						w.food_in_range = []
						w.warriors_in_range = []
						w.distance_to_food = 0

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

							pair[1].score += pair[0].radius / DEFAULT_RADIUS
							#pair[1].increase_size(pair[0].radius)

					if EATING_MODE:
						# warriors can eat other warriors
						eaten_wars = []
						warrior_interaction = [(war1, war2) for war1 in warriors for war2 in warriors]
						for war_pair in warrior_interaction:
							if war_pair[0] in eaten_wars or war_pair[1] in eaten_wars:
								continue

							if war_pair[0] == war_pair[1]:
								continue

							if check_crossover_warriors_vision(*war_pair):
								war_pair[0].warriors_in_range.append(war_pair[1])
								war_pair[1].warriors_in_range.append(war_pair[0])


							if check_crossover(*war_pair):
								if war_pair[0].score >= war_pair[1].score:
									war_pair[0].score += war_pair[1].radius * 0.3
									war_pair[1].score /= 2
									#war_pair[0].radius += war_pair[1].radius * 0.5

									eaten_wars.append(war_pair[1])
									warriors.remove(war_pair[1])
								else:
									war_pair[1].score += war_pair[0].radius * 0.3
									war_pair[0].score /= 2
									#war_pair[1].radius += war_pair[0].radius * 0.5


									eaten_wars.append(war_pair[0])
									warriors.remove(war_pair[0])

					# checking if there is food in the vision range
					for w in warriors:
						if len(w.food_in_range):
							# unlists the element
							if len(w.food_in_range) == 1:
								w.food_in_range = w.food_in_range[0]

							#finds the closes of N foods in vision field
							elif len(w.food_in_range) >= 2:
								closes_idx = find_closest_obj(w, w.food_in_range)
								w.food_in_range = w.food_in_range[closes_idx]

							w.angle = math.degrees(math.atan2(w.food_in_range.y - w.y, w.food_in_range.x - w.x))
							w.distance_to_food = math.sqrt(abs(distance_between_circles(w, w.food_in_range)))

						else:
							w.angle = 0
							w.distance_to_food = w.vision

						if EATING_MODE and len(w.warriors_in_range):
							# unlists the element
							if len(w.warriors_in_range) == 1:
								w.warriors_in_range = w.warriors_in_range[0]
							elif len(w.warriors_in_range) >= 2:
								closes_idx = find_closest_obj(w, w.warriors_in_range)
								w.warriors_in_range = w.warriors_in_range[closes_idx]

							w.enemy_score = w.warriors_in_range.score
							w.angle_to_warrior = math.degrees(math.atan2(w.warriors_in_range.y - w.y, w.warriors_in_range.x - w.x))
							w.distance_to_warrior = math.sqrt(abs(distance_between_circles(w, w.warriors_in_range)))
							w.enemy_in_sight = 1

						else:
							w.enemy_score = w.score + 1
							w.angle_to_warrior = 180
							w.distance_to_warrior = w.vision
							w.enemy_in_sight = 0


					################## replenishing the food
					# potentially 2 or more food can be eaten in the same frame
					while(len(food) < NUMBER_OF_FOOD):
						random_x = random.randrange(20, DISPLAY_WIDTH-20)
						random_y = random.randrange(20, DISPLAY_HEIGHT-20)
						food_ent = FoodEntity(random_x, random_y)

						food.append(food_ent)

				################## drawing the simulation
				gameDisplay.fill(BG_COLOUR)

				for f in food:
					draw_food(gameDisplay, f)

				for w in warriors:
					draw_warrior(gameDisplay, w)

				write_time(gameDisplay, gen, i)

				# hides the screen so we don't see the action
				if LEARNING_WITHOUT_VISUALS:
					pygame.display.iconify()
				else:
					pygame.display.update()

				clock.tick(TICK_SPEED)
			
			# returning eaten entities to update their fitness
			if EATING_MODE:
				for w in eaten_wars:
					warriors.append(w)

			best_fitness = 0
			for w in warriors:
				w.unit.fitness = w.score
				if w.score > best_fitness:
					best_fitness = w.score
			
			print(f'Generation {gen} ended - best fitness: {best_fitness}')
			# writing all entities into a file
			if WRITE_TO_FILE and gen % 5 == 0:
				with open(f"./trained/{ALGORITHM}_{FILE_NAME}.txt", 'wb') as f:
					print('Saving population to file!')

					write_list = []
					write_list.append(gen)
					for w in warriors:
						write_list.append(w.unit)
					
					pickle.dump(write_list, f)

			gen += 1
			#print(f"population PRE EVOLVE len {len(population)}")
			population = algorithm.evolve_population(population)
			#print(f"population POST EVOLVE len {len(population)}")

	except Exception as e:
		print(f"Error: {e}")
		pygame.quit()
		exit()


def game_intro(gameDisplay):
	
	clock = pygame.time.Clock()
	intro = True
	angle = 0
	while intro:
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()
				exit()
		
		gameDisplay.fill(BG_COLOUR)
		# title
		font = pygame.font.SysFont(None, 75)
		text = font.render("Protein Warriors", True, TEXT_COLOUR)
		gameDisplay.blit(text, ((DISPLAY_WIDTH/4)+50,(DISPLAY_HEIGHT/4)))

		# rotating entity
		angle += 10
		# food
		pygame.draw.circle(gameDisplay, FOOD_COLOUR, [(DISPLAY_WIDTH/4),(DISPLAY_HEIGHT/4)-80], 15, 0)
		# entity
		pygame.draw.circle(gameDisplay, VISION_RANGE_COLOUR, [(DISPLAY_WIDTH/4)-100,(DISPLAY_HEIGHT/4)], 70, 1)
		pygame.draw.circle(gameDisplay, ENTITY_COLOUR, [(DISPLAY_WIDTH/4)-100,(DISPLAY_HEIGHT/4)], 20, 0)
		# line where it looks
		pygame.draw.line(gameDisplay, ANGLE_COLOUR, ((DISPLAY_WIDTH/4)-100,(DISPLAY_HEIGHT/4)),
			((DISPLAY_WIDTH/4)-100 + math.cos(math.radians(angle))* 20,
			(DISPLAY_HEIGHT/4)+ math.sin(math.radians(angle))* 20), 3)

		# buttons to choose an algorithm
		font = pygame.font.SysFont(None, 35)
		pygame.draw.rect(gameDisplay, ENTITY_COLOUR,((DISPLAY_WIDTH/4)-30,(DISPLAY_HEIGHT/2),100,50))
		text = font.render("GP", True, BG_COLOUR)
		gameDisplay.blit(text, ((DISPLAY_WIDTH/4),(DISPLAY_HEIGHT/2)+13))

		pygame.draw.rect(gameDisplay, ENTITY_COLOUR,((DISPLAY_WIDTH/2)-30,(DISPLAY_HEIGHT/2),100,50))
		text = font.render("CGP", True, BG_COLOUR)
		gameDisplay.blit(text, ((DISPLAY_WIDTH/2)-5,(DISPLAY_HEIGHT/2)+13))
		
		# currently not done
		pygame.draw.rect(gameDisplay, ENTITY_COLOUR,((3*(DISPLAY_WIDTH/4))-30,(DISPLAY_HEIGHT/2),100,50))
		text = font.render("NN", True, BG_COLOUR)
		gameDisplay.blit(text, ((3*(DISPLAY_WIDTH/4)),(DISPLAY_HEIGHT/2)+13))

		click = pygame.mouse.get_pressed()
		if click[0] == 1:
			mouse = pygame.mouse.get_pos()
			
			if (DISPLAY_WIDTH/4)-50 < mouse[0] < (DISPLAY_WIDTH/4)+120 and (DISPLAY_HEIGHT/2)-20 < mouse[1] < (DISPLAY_HEIGHT/2)+70:
				return "GP"
			elif (DISPLAY_WIDTH/2)-50 < mouse[0] < (DISPLAY_WIDTH/2)+120 and (DISPLAY_HEIGHT/2)-20 < mouse[1] < (DISPLAY_HEIGHT/2)+70:
				return "CGP"
			elif (3*(DISPLAY_WIDTH/4))-50 < mouse[0] < (3*(DISPLAY_WIDTH/4))+120 and (DISPLAY_HEIGHT/2)-20 < mouse[1] < (DISPLAY_HEIGHT/2)+70:
				return "NN"
			# else just continues if area wasn't correct

		pygame.display.update()
		clock.tick(10)


if __name__ == '__main__':

	INTRO_SCREEN = config["INTRO_SCREEN"]
	EATING_MODE = config["EATING_MODE"]

	READ_FROM_FILE = config["READ_FROM_FILE"]
	INPUT_FILE = config["INPUT_FILE"]

	ALGORITHM = config["ALGORITHM"]
	INPUT_COUNT = config["INPUT_COUNT"]
	OUTPUT_COUNT = config["OUTPUT_COUNT"]

	# simulator init
	pygame.init()
	gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
	pygame.display.set_caption('Protein Warriors')

	if INTRO_SCREEN:
		ALGORITHM = game_intro(gameDisplay)

	# importing NN when not needed slows the program drastically
	if ALGORITHM == "NN":
		from NN import NN
		EATING_MODE = False
		INPUT_COUNT = 2
		OUTPUT_COUNT = 2

	algorithm = eval(ALGORITHM + f"({INPUT_COUNT}, {OUTPUT_COUNT}, {NUMBER_OF_WARRIORS})")
	angle_decoder = AngleDecoder()
	direction_decoder = DirectionDecoder()
	
	gen = 1
	population = []
	if READ_FROM_FILE and INPUT_FILE != "":
		# just in case
		if '.txt' not in INPUT_FILE:
			INPUT_FILE += '.txt'
		try:
			with open(f"trained/{INPUT_FILE}", "rb") as f:
				loaded_list = pickle.load(f)
				gen = loaded_list.pop(0)
				population = loaded_list

		# in case of a wrong file or reading error
		except:
			print('Not successful reading from file')
			population = algorithm.create_population()
	else:		
		population = algorithm.create_population()

	print(f"Population starting len {len(population)}")
	game_loop(gameDisplay, population, gen, algorithm, EATING_MODE, angle_decoder, direction_decoder)
	pygame.quit()
