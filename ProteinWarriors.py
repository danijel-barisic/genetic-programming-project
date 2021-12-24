import pygame
import random
import math

class FoodEntity:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.colour = red
		self.radius = DEFAULT_RADIUS

	def __str__(self):
		return f"Food location: {self.x}, {self.y}"

class WarriorEntity:
	def __init__(self, x, y, colour):
		self.x = x
		self.y = y
		self.colour = colour
		self.radius = DEFAULT_WARRIOR_RADIUS
		self.vision = DEFAULT_VISION_RANGE
		self.angle = random.randint(0, 360)
		self.food_in_range = []
		self.speed = 5
		self.score = 0
		self.traveled = 0 
		self.distance_to_food = 0


	def increase_size(self):
		self.radius += 5
		self.vision += 5

	def __str__(self):
		return f"Warrior location: {self.x},{self.y} - Score: {self.score}"

# constants
display_width = 800
display_height = 600

# RGB values of colours
black = (0,0,0)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)
yellow = (255,255,0)
white = (255,255,255)

PI = math.pi

DEFAULT_RADIUS = 15
DEFAULT_WARRIOR_RADIUS = 20
DEFAULT_VISION_RANGE = DEFAULT_WARRIOR_RADIUS + 50
NUMBER_OF_FOOD = 5
NUMBER_OF_WARRIORS = 4

#game lasts (NUMBER_OF_TICKS/TICK_SPEED) seconds  
NUMBER_OF_TICKS = 300
TICK_SPEED = 30


pygame.init()

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Protein Warriors')
clock = pygame.time.Clock()


# starting food
food = []
for i in range(NUMBER_OF_FOOD):
	random_x = random.randrange(20, display_width-20)
	random_y = random.randrange(20, display_height-20)
	food_ent = FoodEntity(random_x, random_y)

	food.append(food_ent)


warriors = []
# create warrior entities
for i in range(NUMBER_OF_WARRIORS):
	random_x = random.randrange(20, display_width-20)
	random_y = random.randrange(20, display_height-20)
	warrior_ent = WarriorEntity(random_x, random_y, green)

	warriors.append(warrior_ent)

# writes time passed in top left corner
def write_time(count):
	font = pygame.font.SysFont(None, 25)
	text = font.render(f"Time passed: {count}", True, white)
	gameDisplay.blit(text, (10, 10))


def draw_food(food):
	pygame.draw.circle(gameDisplay, food.colour, [food.x, food.y], food.radius, 0)

# also writes score next to the center of the circle
def draw_warrior(war):

	pygame.draw.circle(gameDisplay, blue, [war.x, war.y], war.vision, 0)
	pygame.draw.circle(gameDisplay, war.colour, [war.x, war.y], war.radius, 0)

	pygame.draw.line(gameDisplay, red, (war.x, war.y),
			(war.x + math.cos(math.radians(war.angle))* war.radius,
			 war.y + math.sin(math.radians(war.angle))* war.radius), 3)

	font = pygame.font.SysFont(None, 20)
	text = font.render(f"Score: {war.score}", True, white)
	gameDisplay.blit(text, (war.x, war.y))


# if the player leaves the area, the game ends, only affects our player 
def leaving_boundaries(our_war):
	if our_war.x > display_width - our_war.radius or our_war.x - our_war.radius < 0 \
		or our_war.y > display_height - our_war.radius or our_war.y - our_war.radius < 0:
			return True
	return False

# checks if the center of the entity has passed the edge of the screen
def warrior_boundaries(war):
	if war.x > display_width:
		war.x -= display_width
	elif war.x < 0:
		war.x += display_width

	if war.y > display_height:
		war.y -= display_height
	elif war.y < 0:
		war.y += display_height

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
	#smallest_dist = (display_height+display_width)*2
	smallest_dist = 99999
	closes_food = 0
	for idx, food in enumerate(war.food_in_range):
		dist = distance_between_circles(war, food)
		if dist < smallest_dist:
			smallest_dist = dist
			closes_food = idx

	war.food_in_range = war.food_in_range[closes_food]

	## maybe useful?
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
	
	# starting values for our entity
	our_warrior_x = (display_width * 0.45)
	our_warrior_y = (display_height * 0.8)
	our_warrior = WarriorEntity(our_warrior_x, our_warrior_y, yellow)

	x_change, y_change = 0, 0
	gameExit = False

	#while not gameExit: 	## runs game indefinetly
	for i in range(NUMBER_OF_TICKS):
		if gameExit:
			return


		################## checking all movements and warrior-food crossovers
		x_change, y_change = check_player_events(x_change, y_change)
		our_warrior.x += x_change
		our_warrior.y += y_change
		our_warrior.traveled += abs(x_change) + abs(y_change) 

		# player leaving boundaries ends game
		if leaving_boundaries(our_warrior):
			gameExit = True


		################## drawing the simulation
		gameDisplay.fill(black)
		draw_warrior(our_warrior)
		
		for f in food:
			draw_food(f)

		# needed to check our with in the crossover function
		temp_wars_with_ours = warriors[:]
		temp_wars_with_ours.append(our_warrior)

		# check crossovers between each food and warrior
		eaten_food = []
		crossovers_to_check = [(food_ent, warrior_ent) for food_ent in food for warrior_ent in temp_wars_with_ours]
		for pair in crossovers_to_check:
			if check_crossover(*pair):
				if pair[0] in eaten_food:
					continue

				eaten_food.append(pair[0])
				food.remove(pair[0])

				pair[1].score += 1
				pair[1].increase_size()

		# placeholder, we can change radius here
		for w in warriors:
			x_travel = math.cos(math.radians(w.angle)) * w.speed
			y_travel = math.sin(math.radians(w.angle)) * w.speed
			w.x += x_travel
			w.y += y_travel

			# count traveled
			w.traveled += abs(x_travel) + abs(y_travel) 

			warrior_boundaries(w)
			draw_warrior(w)

			# each iterations can have new foods be in range or get out of range 
			w.food_in_range = []
			w.distance_to_food = 0


		# each iterations can have new foods be in range or get out of range 
		our_warrior.food_in_range = []
		our_warrior.distance_to_food = 0

		########## maybe every few moves to save CPU usage?
		######### checking if food in vision field
		crossovers_to_check = [(food_ent, warrior_ent) for food_ent in food for warrior_ent in temp_wars_with_ours]
		for pair in crossovers_to_check:
			if check_crossover_vision(*pair):
				pair[1].food_in_range.append(pair[0])

		for w in temp_wars_with_ours:
			if len(w.food_in_range):
				# unlists the element
				if len(w.food_in_range) == 1:
					w.food_in_range = w.food_in_range[0]

				#finds the closes of N foods in vision field
				elif len(w.food_in_range) >= 2:
					find_closest_food(w)

				w.angle = math.degrees(math.atan2(w.food_in_range.y - w.y, w.food_in_range.x - w.x))

				## maybe useful?
				#w.distance_to_food = math.sqrt(distance_between_circles(w, w.food_in_range))


		################## replenishing the food
		# potentially 2 or more food can be eaten in the same frame
		while(len(food) < NUMBER_OF_FOOD):
			random_x = random.randrange(20, display_width-20)
			random_y = random.randrange(20, display_height-20)
			food_ent = FoodEntity(random_x, random_y)

			food.append(food_ent)


		write_time(i)
		pygame.display.update()
		clock.tick(TICK_SPEED)


game_loop()
pygame.quit()
