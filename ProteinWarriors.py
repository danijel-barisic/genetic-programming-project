import pygame
import random


class FoodEntity:
	def __init__(self, x, y):
		self.x = x
		self.y = y
		self.radius = DEFAULT_RADIUS
		#self.speed = DEFAULT_SPEED
		#self.size = DEFAULT_SIZE


pygame.init()

display_width = 800
display_height = 600

black = (0,0,0)
white = (255,255,255)
red = (255,0,0)

protein_entity_width = 50
DEFAULT_RADIUS = 15

gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Protein Warriors')
clock = pygame.time.Clock()

protein_img = pygame.image.load('protein.png')

# starting food
food = []
for i in range(5):
	random_x = random.randrange(20, display_width-20)
	random_y = random.randrange(20, display_height-20)
	food_ent = FoodEntity(random_x, random_y)

	food.append(food_ent)


def write_score(count):
	font = pygame.font.SysFont(None, 25)
	text = font.render(f"Score: {count}", True, white)
	gameDisplay.blit(text, (10, 10))


def draw_food(food_entity):
	pygame.draw.circle(gameDisplay, red, [food_entity.x, food_entity.y], food_entity.radius, 0)

def draw_protein(x,y):
	gameDisplay.blit(protein_img, (x,y))

def leaving_boundaries(x, y):
	if x > display_width - protein_entity_width or x < 0 or y > display_height - protein_entity_width or y < 0:
		return True
	return False


def check_movement(x_change, y_change):
	# moving our entity
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
	x = (display_width * 0.45)
	y = (display_height * 0.8)

	x_change = 0
	y_change = 0

	score_counter = 0
	gameExit = False

	while not gameExit:

		x_change, y_change = check_movement(x_change, y_change)

		x += x_change
		y += y_change


		gameDisplay.fill(black)
		draw_protein(x,y)

		#print(f"protein x,y = {x},{y}")
		for idx, f in enumerate(food):
			draw_food(f)
			#print(f"food no.{idx} center at x, y - {f.x},{f.y} ")

			# check x crossover
			if ((x + protein_entity_width) > (f.x - f.radius) and (x + protein_entity_width) < (f.x + f.radius)) \
				or (x > (f.x - f.radius) and (x < (f.x + f.radius))) \
				or (f.x > x and f.x < (x + protein_entity_width)):
				#print(f'x crossover at food no.{idx}')

					# also check y crossover
					if ((y + protein_entity_width) > (f.y - f.radius) and (y + protein_entity_width) < (f.y + f.radius)) \
						or (y > (f.y - f.radius) and (y < (f.y + f.radius))) \
						or (f.y > y and f.y < (y + protein_entity_width)):
							print(f'>>>> x and y crossover at food no.{idx} <<<<')
							score_counter += 1
							food.remove(f)


								
		# leaving boundaries ends game
		if leaving_boundaries(x, y):
			gameExit = True
		
		
		# if some food got eaten
		if len(food) < 5:
			random_x = random.randrange(20, display_width-20)
			random_y = random.randrange(20, display_height-20)
			food_ent = FoodEntity(random_x, random_y)

			food.append(food_ent)


		write_score(score_counter)

		pygame.display.update()
		clock.tick(60)



game_loop()
pygame.quit()
quit()