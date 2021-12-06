import pygame
import random


class FoodEntity:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.colour = red
		self.radius = DEFAULT_RADIUS
		#self.size = DEFAULT_SIZE

	def __str__(self):
		return f"Food location: {self.x},{self.y}"

class WarriorEntity:
	def __init__(self, x, y, colour):
		self.x = x
		self.y = y
		self.colour = colour
		self.radius = DEFAULT_WARRIOR_RADIUS
		self.score = 0
		self.speed = 5
		#self.size = DEFAULT_SIZE

	def increase_size(self):
		self.radius += 20

	def __str__(self):
		return f"Warrior location: {self.x},{self.y} - Score: {self.score}"

# constants
display_width = 800
display_height = 600

# RGB values of colours
black = (0,0,0)
white = (255,255,255)
red = (255,0,0)
green = (0,255,0)
blue = (0,0,255)

DEFAULT_RADIUS = 15
DEFAULT_WARRIOR_RADIUS = 20
NUMBER_OF_FOOD = 5
NUMBER_OF_WARRIORS = 4


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

## TODO: change
## currently kind of obsolete since out score is written on our entity
# writes our score in top left corner
def write_score(count):
	font = pygame.font.SysFont(None, 25)
	text = font.render(f"Score: {count}", True, white)
	gameDisplay.blit(text, (10, 10))


def draw_food(food_entity):
	pygame.draw.circle(gameDisplay, food_entity.colour, [food_entity.x, food_entity.y], food_entity.radius, 0)

# also writes score next to the center of the circle
def draw_warrior(warrior_entity):
	pygame.draw.circle(gameDisplay, warrior_entity.colour, [warrior_entity.x, warrior_entity.y], warrior_entity.radius, 0)
	font = pygame.font.SysFont(None, 20)
	text = font.render(f"Score: {warrior_entity.score}", True, white)
	gameDisplay.blit(text, (warrior_entity.x, warrior_entity.y))

# this only affects out warrior, 
# if the player leaves the area, the game ends
def leaving_boundaries(our_warrior):
	if our_warrior.x > display_width - our_warrior.radius or our_warrior.x - our_warrior.radius < 0 \
		or our_warrior.y > display_height - our_warrior.radius or our_warrior.y - our_warrior.radius < 0:
			return True
	return False

## TODO: change if others dissagree
## causes flickering, needs fixing
# current idea is something similar to snake game. Leaving one side puts you on the other
def warrior_boundaries(warrior_entity):
	if warrior_entity.x > display_width - warrior_entity.radius:
		warrior_entity.x = warrior_entity.x - display_width
	elif warrior_entity.x - warrior_entity.radius < 0:
		warrior_entity.x = display_width + warrior_entity.x

	if warrior_entity.y > display_height - warrior_entity.radius:
		warrior_entity.y = warrior_entity.y - display_height
	elif warrior_entity.y - warrior_entity.radius < 0:
		warrior_entity.y = display_height + warrior_entity.y


# checking if food and warrior are in contact with eachother with respect to their radiuses
def check_crossover(food, warrior):
	# first check x crossover
	if ((warrior.x + warrior.radius) > (food.x - food.radius) and (warrior.x + warrior.radius) < (food.x + food.radius)) \
		or ((warrior.x - warrior.radius) > (food.x - food.radius) and ((warrior.x - warrior.radius) < (food.x + food.radius))) \
		or (food.x > (warrior.x - warrior.radius) and food.x < (warrior.x + warrior.radius)):

			# also check y crossover
			if ((warrior.y + warrior.radius) > (food.y - food.radius) and (warrior.y + warrior.radius) < (food.y + food.radius)) \
				or ((warrior.y - warrior.radius) > (food.y - food.radius) and ((warrior.y - warrior.radius) < (food.y + food.radius))) \
				or (food.y > (warrior.y - warrior.radius) and food.y < (warrior.y + warrior.radius)):
					return True

	return False


# moving our entity
def check_movement(x_change, y_change):
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			gameExit = True

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

	our_warrior = WarriorEntity(our_warrior_x, our_warrior_y, blue)

	x_change, y_change = 0, 0

	gameExit = False

	while not gameExit:

		################## checking all movements and warrior-food crossovers
		x_change, y_change = check_movement(x_change, y_change)
		our_warrior.x += x_change
		our_warrior.y += y_change

		# leaving boundaries ends game
		if leaving_boundaries(our_warrior):
			gameExit = True
		

		temporary_warriors_with_ours = warriors[:]
		temporary_warriors_with_ours.append(our_warrior)


		## TODO: fix bug when two warriors eat the same food in the same frame 
		## only happens when two warriors become really big
		## (iterate over remaining pairs with the same food and remove pairs)
		crossovers_to_check = [(food_ent, warrior_ent) for food_ent in food for warrior_ent in temporary_warriors_with_ours]
		for pair in crossovers_to_check:
			if check_crossover(*pair):
				print(f'>>>> food x and y crossover at {pair[0].x},{pair[0].y} <<<<')
				pair[1].score += 1
				pair[1].increase_size()

				food.remove(pair[0])


		################## drawing the simulation
		gameDisplay.fill(black)
		draw_warrior(our_warrior)

		for f in food:
			draw_food(f)

		# placeholder, currently random movements 
		for w in warriors:
			if random.randint(0,1):
				w.x += w.speed
			else:
				w.x -= w.speed
			if random.randint(0,1):
				w.y += w.speed
			else:
				w.y -= w.speed
			warrior_boundaries(w)
			draw_warrior(w)

								
		write_score(our_warrior.score)
		

		################## replenishing the food
		# potentially 2 or more food can be eaten in the same frame
		while(len(food) < NUMBER_OF_FOOD):
			random_x = random.randrange(20, display_width-20)
			random_y = random.randrange(20, display_height-20)
			food_ent = FoodEntity(random_x, random_y)

			food.append(food_ent)


		
		pygame.display.update()
		clock.tick(20)


game_loop()
pygame.quit()
