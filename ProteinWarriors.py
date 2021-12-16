import pygame
import random
import math

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
		self.vision = self.radius + 30
		#self.size = DEFAULT_SIZE

	def increase_size(self):
		self.radius += 20
		self.vision = self.radius + 30

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

PI = math.pi

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


def draw_food(food):
	pygame.draw.circle(gameDisplay, food.colour, [food.x, food.y], food.radius, 0)

# also writes score next to the center of the circle
def draw_warrior(war):

	pygame.draw.circle(gameDisplay, blue, [war.x, war.y], war.vision, 0)
	pygame.draw.circle(gameDisplay, war.colour, [war.x, war.y], war.radius, 0)

	font = pygame.font.SysFont(None, 20)
	text = font.render(f"Score: {war.score}", True, white)
	gameDisplay.blit(text, (war.x, war.y))

	# start of the vision field
	#wRect = pygame.Rect(war.x-war.radius, war.y-war.radius, war.radius*2, war.radius*2)
	#pygame.draw.rect(gameDisplay, white, wRect)
	#pygame.draw.arc(gameDisplay, blue, wRect, PI/3, 2*PI/3)


# this only affects out warrior, 
# if the player leaves the area, the game ends
def leaving_boundaries(our_war):
	if our_war.x > display_width - our_war.radius or our_war.x - our_war.radius < 0 \
		or our_war.y > display_height - our_war.radius or our_war.y - our_war.radius < 0:
			return True
	return False

## causes flickering, but works well with bounds
# leaving one side puts you on the other
def warrior_boundaries(war):
	if war.x > display_width - war.radius:
		war.x -= display_width
	elif war.x - war.radius < 0:
		war.x += display_width

	if war.y > display_height - war.radius:
		war.y -= display_height
	elif war.y - war.radius < 0:
		war.y += display_height


# solves flickering by only checking if the center is over the edge
## TODO: check_crossover2, currently the part of the radius wont eat the food that's on the other side of the edge
## if it is inside the radius, only happens when the food is close to the edge and radius is large
def warrior_boundaries2(war):
	if war.x > display_width:
		war.x -= display_width
	elif war.x < 0:
		war.x += display_width

	if war.y > display_height:
		war.y -= display_height
	elif war.y < 0:
		war.y += display_height



# checking if food and warrior are in contact with eachother with respect to their radiuses
def check_crossover(food, war):
	# first check x crossover
	if ((war.x + war.radius) > (food.x - food.radius) and (war.x + war.radius) < (food.x + food.radius)) \
		or ((war.x - war.radius) > (food.x - food.radius) and ((war.x - war.radius) < (food.x + food.radius))) \
		or (food.x > (war.x - war.radius) and food.x < (war.x + war.radius)):

			# also check y crossover
			if ((war.y + war.radius) > (food.y - food.radius) and (war.y + war.radius) < (food.y + food.radius)) \
				or ((war.y - war.radius) > (food.y - food.radius) and ((war.y - war.radius) < (food.y + food.radius))) \
				or (food.y > (war.y - war.radius) and food.y < (war.y + war.radius)):
					return True

	return False


def check_crossover2(food, war):
	## TODO: if we are going to use warrior_boundaries2 func which moves x,y cords only if the center leaves the screen,
	# then we have to take into account the part of the circle/radius which is already on the other side of the screen
	# even if it is invisible

	pass


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
	# for i in range(200):
	# 	if gameExit:
	# 		return





		################## checking all movements and warrior-food crossovers
		x_change, y_change = check_movement(x_change, y_change)
		our_warrior.x += x_change
		our_warrior.y += y_change

		# leaving boundaries ends game
		if leaving_boundaries(our_warrior):
			gameExit = True
		
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
				print(f'>>>> food x and y crossover at {pair[0].x},{pair[0].y} <<<<')

				pair[1].score += 1
				pair[1].increase_size()


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

			warrior_boundaries2(w)
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
		clock.tick(40)


game_loop()
pygame.quit()
