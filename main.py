import pygame
from pygame import mixer
import os
import random
import csv
import button
from all_data import all_info, all_quiz, all_answer

mixer.init()
pygame.init()

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Games for Social Awareness about Health conditions & diseases')

#set framerate
clock = pygame.time.Clock()
FPS = 60

# we define colours as constants to use them frequently
BG = (144, 201, 120)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
PINK = (235, 65, 54)

# some constants and gloabal variables we would need
GRAVITY = 0.75
SCROLL_THRESHOLD = 200
NUM_ROWS = 16
NUM_COLS = 150
TILE_SIZE = SCREEN_HEIGHT // NUM_ROWS
TILE_TYPES = 21
MAX_LEVELS = 5
scroll_screen = 0
scroll_background = 0
begin_game = False
begin_intro = False
answered_correctly = False

level = 1
disease = 'Diabetes'
# all games images
diabetes_img = pygame.image.load('img/home_page/Diabetes.png')
aids_img = pygame.image.load('img/home_page/AIDS.png')
alziemers_img = pygame.image.load('img/home_page/alziemers.png')
breast_cancer_img = pygame.image.load('img/home_page/BreastCancer.png')
copd_img = pygame.image.load('img/home_page/COPD.png')
heartattack_img = pygame.image.load('img/home_page/HeartAttack.png')
hepatitis_img = pygame.image.load('img/home_page/Hepatitis.png')
disease1_img = pygame.image.load('img/home_page/disease1.png')
disease2_img = pygame.image.load('img/home_page/disease2.png')

# variables to control the movement of the player
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# we will load all the images into some variables so that we can use them again and again
# the background is four layers
# the layer which is neared to the player is the first layer
firstlayerbg_img = pygame.image.load('img/background/buildingsfar.png').convert_alpha()
secondlayerbg_img = pygame.image.load('img/background/buildingsnear.png').convert_alpha()
thridlayerbg_img = pygame.image.load('img/background/farther.png').convert_alpha()
sky_img = pygame.image.load('img/background/clouds.png').convert_alpha()

# all button images
start_btn_image = pygame.image.load('img/buttons/start_btn.png').convert_alpha()
end_btn_image = pygame.image.load('img/buttons/exit_btn.png').convert_alpha()
restart_btn_img = pygame.image.load('img/buttons/restart_btn.png').convert_alpha()
start_quiz_btn_img = pygame.image.load('img/buttons/start_quiz_btn.png').convert_alpha()
submit_quiz_btn_img = pygame.image.load('img/buttons/submit_quiz_btn.png').convert_alpha()
infopoint_btns_imgs = []
for i in range(6):
	infopoint_btn_img = pygame.image.load(f'img/collected_info/infopoint{i+1}.png')
	infopoint_btn_img = pygame.transform.scale(infopoint_btn_img, (int(infopoint_btn_img.get_width() * 0.7), int(infopoint_btn_img.get_height() *0.7)))
	infopoint_btns_imgs.append(infopoint_btn_img)

# bullets, grenades, and item boxes of all three types
bullet_image = pygame.image.load('img/icons/bullet.png').convert_alpha()
grenade_image = pygame.image.load('img/icons/grenade.png').convert_alpha()
healthBox_image = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammoBox_image = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenadeBox_image = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
	'Health'	: healthBox_image,
	'Ammo'		: ammoBox_image,
	'Grenade'	: grenadeBox_image
}

# information and quiz board images
infoboard_img = pygame.image.load('img/infoboard.png').convert_alpha()
quizboard_img = pygame.image.load('img/quiz.png').convert_alpha()
empty_option_img = pygame.image.load('img/buttons/empty_option.png').convert_alpha()
selected_option_img = pygame.image.load('img/buttons/selected_option.png').convert_alpha()
remove_option_img = pygame.image.load('img/buttons/remove_option.png').convert_alpha()
wrong_ans_img = pygame.image.load('img/wrong_answer.png')

# to load the word we have different tiles and the tiles are basically numbers stored in csv format
# we will read the csv file for numbers and then according to the number we will decide the tile for it
# now since we are loading the images we will load the images of all the tiles in a list
tiles_images = []
for i in range(TILE_TYPES):
	image = pygame.image.load(f'img/tile/{i}.png')
	image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
	tiles_images.append(image)


# following fonts we will define, and use as we will need
Futura_font = pygame.font.SysFont('Futura', 30)
Helvitica_font = pygame.font.SysFont('Helvetica', 35)
Arial_font = pygame.font.SysFont('Arial', 35)
Garmond_font = pygame.font.SysFont('Garamond', 35)
Georgia_font = pygame.font.SysFont('Georgia', 20)
Robota_font = pygame.font.SysFont('Roboto', 28)
CenturyGothlic_font = pygame.font.SysFont('Century Gothic', 28)


#load music and sounds
# pygame.mixer.music.load('audio/music2.mp3')
#pygame.mixer.music.set_volume(0.3)
# pygame.mixer.music.play(-1, 0.0, 5000)
shoot_sound = pygame.mixer.Sound('audio/shot.wav')
shoot_sound.set_volume(0.05)
explode_sound = pygame.mixer.Sound('audio/grenade.wav')
explode_sound.set_volume(0.05)
jump_sound = pygame.mixer.Sound('audio/jump.wav')
jump_sound.set_volume(0.05)


# now we define some helper functions 
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))

def draw_bg():
	screen.fill(BG)
	width = sky_img.get_width()
	for x in range(5):
		screen.blit(sky_img, ((x * width) - scroll_background * 0.5, 0))
		screen.blit(thridlayerbg_img, ((x * width) - scroll_background * 0.6, SCREEN_HEIGHT - thridlayerbg_img.get_height() - 300))
		screen.blit(secondlayerbg_img, ((x * width) - scroll_background * 0.7, SCREEN_HEIGHT - secondlayerbg_img.get_height() - 150))
		screen.blit(firstlayerbg_img, ((x * width) - scroll_background * 0.8, SCREEN_HEIGHT - firstlayerbg_img.get_height()))

# when reseting the level we will need to empty all the sprite groups,
#  or else they will persist in further levels also

def reset_level():
	enemy_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()
	tokens_group.empty()
	information_group.empty()
	data = []
	for row in range(NUM_ROWS):
		r = [-1] * NUM_COLS
		data.append(r)
	return data


class LivingBeing(pygame.sprite.Sprite):
	def __init__(self, x, y, character, scale,x_vel,bullets, bombs):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.health = 100
		self.max_health = 100
		self.x_vel = x_vel
		self.y_vel = 0
		self.character = character
		self.bullets = bullets
		self.start_bullets = bullets
		self.shoot_cooldown = 0
		self.bombs = bombs
		self.flip = False
		self.direction = 1 # value = 1 if direction is moving right and -1 if moving left
		self.jump = False
		self.in_air = True
		# to animate, we will load all discrete images in a list while initializing
		self.animation_list = []
		self.image_index = 0
		self.action = 0
		self.update_time = pygame.time.get_ticks()
		
		# variables specific to watch
		self.walk_counter = 0
		self.watch_area = pygame.Rect(0, 0, 150, 20)
		self.still = False
		self.still_counter = 0
		self.collection = 0
		
		#load all images for the players
		animation_types = ['Idle', 'Run', 'Jump', 'Death']
		for animation in animation_types:
			temp = []
			num_images = len(os.listdir(f'img/{self.character}/{animation}'))
			for i in range(num_images):
				image = pygame.image.load(f'img/{self.character}/{animation}/{i}.png').convert_alpha()
				image = pygame.transform.scale(image, (int(image.get_width() * scale), int(image.get_height() * scale)))
				temp.append(image)
			self.animation_list.append(temp)

		self.image = self.animation_list[self.action][self.image_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()

	def update(self):
		self.animate()
		self.if_alive()
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1

	def move(self, moving_left, moving_right):
		# reset variables
		scroll_screen = 0
		dx = 0
		dy = 0
		#  set values of variables for cases of moving left or right
		if moving_left:
			dx = -self.x_vel
			self.flip = True
			self.direction = -1
		if moving_right:
			dx = self.x_vel
			self.flip = False
			self.direction = 1
		if self.jump == True and self.in_air == False:
			self.y_vel = -15
			self.jump = False
			self.in_air = True
		# now put common gravity for enemies and players
		# gravity here is not acceleration, it is a constant speed
		self.y_vel += GRAVITY
		if self.y_vel > 10:
			self.y_vel
		dy += self.y_vel
		# while moving it can collide with floor, ceiling, walls, water, item_boxes

		#check for collision with ground, wall and ceiling in different cases
		for tile in world.obstacle_list:
			#collision with walls
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				dx = 0
				#if when enemy on watch hits a wall, then we just reverse its direction of walking
				if self.character == 'enemy':
					self.direction *= -1
					self.walk_counter = 0
			#collision with ceiling or floor
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				# with ceiling
				if self.y_vel < 0:
					self.y_vel = 0
					dy = tile[1].bottom - self.rect.top
				# with floor
				elif self.y_vel >= 0:
					self.y_vel = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom

		# collision with water
		if pygame.sprite.spritecollide(self, water_group, False):
			self.health = 0
		#collision with exit
		level_completed = False
		end_reached = False
		if pygame.sprite.spritecollide(self, exit_group, False):
			end_reached = True
			level_completed = True
		#if fallen off the map
		if self.rect.bottom > SCREEN_HEIGHT:
			self.health = 0
		#check if going off the edges of the screen
		if self.character == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > SCREEN_WIDTH:
				dx = 0
		#update rectangle position
		self.rect.x += dx
		self.rect.y += dy
		#update scroll based on player position
		if self.character == 'player':
			if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESHOLD and scroll_background < (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
				or (self.rect.left < SCROLL_THRESHOLD and scroll_background > abs(dx)):
				self.rect.x -= dx
				scroll_screen = -dx
		return scroll_screen, level_completed, end_reached

	def fire_bullet(self):
		if self.shoot_cooldown == 0 and self.bullets > 0:
			self.shoot_cooldown = 20
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
			bullet_group.add(bullet)
			self.bullets -= 1
			shoot_sound.play()

	def watch(self):
		if self.alive and player.alive:
			if self.still == False and random.randint(1, 200) == 1:
				self.update_action(0) #because 0 is idle
				self.still = True
				self.still_counter = 50
			# if while watching, the watch scope rectangle catches the player
			if self.watch_area.colliderect(player.rect):
				#stop walking
				self.update_action(0)#0: idle
				self.fire_bullet()
			else:
				if self.still == False:
					if self.direction == 1:
						watch_move_right = True
					else:
						watch_move_right = False
					watch_move_left = not watch_move_right
					self.move(watch_move_left, watch_move_right)
					self.update_action(1) #beacuase 1 is for run
					self.walk_counter += 1
					#update watch area as and when the enemy moves
					self.watch_area.center = (self.rect.centerx + 75 * self.direction, self.rect.centery)
					# pygame.draw.rect(screen, RED, self.vision, 3)
					if self.walk_counter > TILE_SIZE:
						self.direction *= -1
						self.walk_counter *= -1
				else:
					# if not still then this happens
					self.still_counter -= 1
					if self.still_counter <= 0:
						self.still = False

		# to scroll we will always add this line
		self.rect.x += scroll_screen

	def animate(self):
		ANIMATION_COOLDOWN = 100
		self.image = self.animation_list[self.action][self.image_index]
		#check if enough time has passed since the last update
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.image_index += 1
		if self.image_index >= len(self.animation_list[self.action]):
			if self.action == 3:
				self.image_index = len(self.animation_list[self.action]) - 1
			else:
				self.image_index = 0

	def update_action(self, new_action):
		# basically when there is a new action , then update the variable and the image
		if new_action != self.action:
			self.action = new_action
			#update the animation settings
			self.image_index = 0
			self.update_time = pygame.time.get_ticks()

	def if_alive(self):
		if self.health <= 0:
			self.health = 0
			self.x_vel = 0
			self.alive = False
			self.update_action(3)

	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)


class World():
	def __init__(self):
		self.obstacle_list = []

	def process_data(self, data):
		self.level_length = len(data[0])
		idx = 0
		#iterate through each value in level data file
		for y, row in enumerate(data):
			for x, tile in enumerate(row):
				if tile >= 0:
					image = tiles_images[tile]
					image_rect = image.get_rect()
					image_rect.x = x * TILE_SIZE
					image_rect.y = y * TILE_SIZE
					tile_data = (image, image_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(image, x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
					elif tile == 11:
						decoration = Decoration(image, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 12:
						# print("size of info_points_group before : ", len(tokens_group))
						# print("Found a tile of information at : ", x, y, " and index :", idx)
						token = Tokens(x*TILE_SIZE, y*TILE_SIZE, idx)
						tokens_group.add(token)
						idx += 1
						# print("size of info_points_group after : ", len(tokens_group))
					elif tile >= 13 and tile <= 14:
						decoration = Decoration(image, x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
					elif tile == 15:#create player
						player = LivingBeing( x * TILE_SIZE, y * TILE_SIZE, 'player',1.65, 5, 20, 5)
						health_bar = HealthBar(10, 10, player.health, player.health)
					elif tile == 16:#create enemies
						enemy = LivingBeing( x * TILE_SIZE, y * TILE_SIZE, 'enemy',1.65, 2, 20, 0)
						enemy_group.add(enemy)
					elif tile == 17:#create ammo box
						item_box = ItemBox('Ammo', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 18:#create grenade box
						item_box = ItemBox('Grenade', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 19:#create health box
						item_box = ItemBox('Health', x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
					elif tile == 20:#create exit
						exit = Exit(image, x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)

		return player, health_bar


	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += scroll_screen
			screen.blit(tile[0], tile[1])


class Decoration(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += scroll_screen


class Water(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += scroll_screen

class Exit(pygame.sprite.Sprite):
	def __init__(self, img, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))

	def update(self):
		self.rect.x += scroll_screen


class ItemBox(pygame.sprite.Sprite):
	def __init__(self, item_type, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))


	def update(self):
		#scroll
		self.rect.x += scroll_screen
		#check if the player has picked up the box
		if pygame.sprite.collide_rect(self, player):
			#check what kind of box it was
			if self.item_type == 'Health':
				player.health += 25
				if player.health > player.max_health:
					player.health = player.max_health
			elif self.item_type == 'Ammo':
				player.bullets += 15
			elif self.item_type == 'Grenade':
				player.bombs += 3
			#delete the item box
			self.kill()


class Tokens(pygame.sprite.Sprite):
	def __init__(self, x, y, index):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.index = index
		self.frame_index = 0
		self.animation_list = []
		self.update_time = pygame.time.get_ticks()

		#count number of files in the folder
		num_of_frames = len(os.listdir('img/info_point'))
		for i in range(num_of_frames):
			img = pygame.image.load(f'img/info_point/{i}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * 0.1), int(img.get_height() * 0.1)))
			self.animation_list.append(img)

		img = pygame.image.load('img/info_point/0.png').convert_alpha()
		img = pygame.transform.scale(img, (int(img.get_width() * 0.1), int(img.get_height() * 0.1)))
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (self.x + TILE_SIZE // 2, self.y + (TILE_SIZE - self.image.get_height()))

	def update_animation(self):
		ANIMATION_COOLDOWN = 100
		self.image = self.animation_list[self.frame_index]
		if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
			self.update_time = pygame.time.get_ticks()
			self.frame_index += 1
		if self.frame_index >= len(self.animation_list):
			self.frame_index = 0

	def update(self):
		self.update_animation()
		self.rect.x += scroll_screen
		if pygame.sprite.spritecollide(player, tokens_group, False):
			player.collection += 1
			information = Information(self.x, self.y, 1.5, self.index)
			information_group.add(information)
			self.kill()

class Information(pygame.sprite.Sprite):
	def __init__(self, x, y, scale, index):
		# print("object createed for information")
		pygame.sprite.Sprite.__init__(self)
		self.scale = scale
		self.index = index
		self.info_line = all_info[disease][f'Level{level}'][f'Point{self.index + 1}']
		self.btn_x = 30
		self.btn_y = 100 + int((self.index)*50)
		self.image = infopoint_btns_imgs[self.index]
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.btn_x, self.btn_y)

		self.box_image = infoboard_img
		self.box_image = pygame.transform.scale(self.box_image, (int(self.box_image.get_width() * scale), int( self.box_image.get_height() * scale * 0.7)))
		self.box_x = SCREEN_WIDTH//4 + 50
		self.box_y = 100
		self.info_x = self.box_x + 50
		self.info_y = self.box_y + 100

	def parsetext(self):
		line = self.info_line
		max_length = 36
		parts = []
		# Split the line into chunks of maximum length 36
		for i in range(0, len(line), max_length):
			parts.append(line[i:i+max_length])
		return parts
	
	def display_button(self):
		read_button = button.Button(self.btn_x, self.btn_y, infopoint_btns_imgs[self.index], 1)
		if read_button.draw(screen):
			self.display_info()

	def display_info(self):
		screen.blit(self.box_image, (self.box_x, self.box_y))
		lines = self.parsetext()
		for x,line in enumerate(lines):
			draw_text(line, Futura_font, WHITE, self.info_x , (x*40) + self.info_y)

	def update(self):
		# self.rect.x += scroll_screen

		self.display_button()
		

class HealthBar():
	def __init__(self, x, y, health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health

	def draw(self, health):
		#update with new health
		self.health = health
		#calculate health ratio
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, BLACK, (self.x - 2, self.y - 2, 154, 24))
		pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
		pygame.draw.rect(screen, GREEN, (self.x, self.y, 150 * ratio, 20))

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 10
		self.image = bullet_image
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction

	def update(self):
		#move bullet
		self.rect.x += (self.direction * self.speed) + scroll_screen
		#check if bullet has gone off screen
		if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
			self.kill()
		#check for collision with level
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()

		#check collision with characters
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if enemy.alive:
					enemy.health -= 25
					self.kill()

class Grenade(pygame.sprite.Sprite):
	def __init__(self, x, y, direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 100
		self.vel_y = -11
		self.speed = 7
		self.image = grenade_image
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		self.direction = direction

	def update(self):
		self.vel_y += GRAVITY
		dx = self.direction * self.speed
		dy = self.vel_y

		#check for collision with level
		for tile in world.obstacle_list:
			#check collision with walls
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			#check for collision in the y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
				self.speed = 0
				#check if below the ground, i.e. thrown up
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground, i.e. falling
				elif self.vel_y >= 0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom	


		#update grenade position
		self.rect.x += dx + scroll_screen
		self.rect.y += dy

		#countdown timer
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			explode_sound.play()
			explosion = Explosion(self.rect.x, self.rect.y, 0.5)
			explosion_group.add(explosion)
			#do damage to anyone that is nearby
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health = 0

class Explosion(pygame.sprite.Sprite):
	def __init__(self, x, y, scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
			self.images.append(img)
		self.frame_index = 0
		self.image = self.images[self.frame_index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0


	def update(self):
		#scroll
		self.rect.x += scroll_screen

		EXPLOSION_SPEED = 4
		#update explosion amimation
		self.counter += 1

		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.frame_index += 1
			#if the animation is complete then delete the explosion
			if self.frame_index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.frame_index]


class ScreenFade():
	def __init__(self, direction, colour, speed):
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0

	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:#whole screen fade
			pygame.draw.rect(screen, self.colour, (0 - self.fade_counter, 0, SCREEN_WIDTH // 2, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH // 2 + self.fade_counter, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
			pygame.draw.rect(screen, self.colour, (0, 0 - self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT // 2))
			pygame.draw.rect(screen, self.colour, (0, SCREEN_HEIGHT // 2 +self.fade_counter, SCREEN_WIDTH, SCREEN_HEIGHT))
		if self.direction == 2:#vertical screen fade down
			pygame.draw.rect(screen, self.colour, (0, 0, SCREEN_WIDTH, 0 + self.fade_counter))
		if self.fade_counter >= SCREEN_WIDTH:
			fade_complete = True

		return fade_complete

class Quiz:
	def __init__(self):
		self.x = SCREEN_WIDTH//4 + 50
		self.y = 370
		self.image = quizboard_img
		self.image = pygame.transform.scale(self.image, (int(self.image.get_width() * 1.5), int( self.image.get_height() * 1.8)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (self.x, self.y)
		self.start_quiz = False
		self.offset = []
		self.max_offset = 0
		self.a = False
		self.b = False
		self.c = False
		self.d = False

	def parsetext(self, line):
		max_length = 50
		parts = []
		# Split the line into chunks of maximum length 36
		for i in range(0, len(line), max_length):
			parts.append(line[i:i+max_length])
		return parts

	def display_ques(self):
		question = self.parsetext(all_quiz[disease][f'Level{level}']['Question'])
		option1 = self.parsetext(all_quiz[disease][f'Level{level}']['Option1'])
		option2 = self.parsetext(all_quiz[disease][f'Level{level}']['Option2'])
		option3 = self.parsetext(all_quiz[disease][f'Level{level}']['Option3'])
		option4 = self.parsetext(all_quiz[disease][f'Level{level}']['Option4'])
		offset_ques = 0
		offset_option1 = 0
		offset_option2 = 0
		offset_option3 = 0
		for i,line in enumerate(question):
			draw_text(line, CenturyGothlic_font, BLACK, self.x + 30, self.y + 100 + 30*i)
			offset_ques = 30*i + 35 + 100
		for i,line in enumerate(option1):
			draw_text(line, CenturyGothlic_font, BLACK, self.x + 30, self.y + 30*i + offset_ques)
			offset_option1 = 35 + offset_ques + (30*i)
		for i,line in enumerate(option2):
			draw_text(line, CenturyGothlic_font, BLACK, self.x + 30, self.y + 30*i + offset_option1)
			offset_option2 = 35 + offset_option1 + (30*i)
		for i,line in enumerate(option3):
			draw_text(line, CenturyGothlic_font, BLACK, self.x + 30, self.y + 30*i + offset_option2)
			offset_option3 = 35 + offset_option2 + (30*i)
		for i,line in enumerate(option4):
			draw_text(line, CenturyGothlic_font, BLACK, self.x + 30, self.y + 30*i + offset_option3)
		self.offset.append(offset_ques)
		self.offset.append(offset_option1)
		self.offset.append(offset_option2)
		self.offset.append(offset_option3)
		self.max_offset = offset_option3

	def display_options(self):
		option1_button = button.Button(150, self.y  + self.offset[0], empty_option_img, 1)
		option2_button = button.Button(150, self.y  + self.offset[1], empty_option_img, 1)
		option3_button = button.Button(150, self.y  + self.offset[2], empty_option_img, 1)
		option4_button = button.Button(150, self.y  + self.offset[3], empty_option_img, 1)
		remove1_button = button.Button(120, self.y  + self.offset[0], remove_option_img, 1)
		remove2_button = button.Button(120, self.y  + self.offset[1], remove_option_img, 1)
		remove3_button = button.Button(120, self.y  + self.offset[2], remove_option_img, 1)
		remove4_button = button.Button(120, self.y  + self.offset[3], remove_option_img, 1)
		if option1_button.draw(screen):
			self.a = True
		if option2_button.draw(screen):
			self.b = True
		if option3_button.draw(screen):
			self.c = True
		if option4_button.draw(screen):
			self.d = True
		
		if self.a:
			screen.blit(selected_option_img, (150 , self.y  + self.offset[0] ))
			if remove1_button.draw(screen):
				self.a = False
		if self.b:
			screen.blit(selected_option_img, (150 , self.y  + self.offset[1] ))
			if remove2_button.draw(screen):
				self.b = False
		if self.c:
			screen.blit(selected_option_img, (150 , self.y  + self.offset[2] ))
			if remove3_button.draw(screen):
				self.c = False
		if self.d:
			screen.blit(selected_option_img, (150 , self.y  + self.offset[3] ))
			if remove4_button.draw(screen):
				self.d = False

	def check_ans(self):
		load_ans = all_answer[disease][f'Level{level}']
		if (self.a == load_ans[0]) and (self.b == load_ans[1]) and (self.c == load_ans[2]) and (self.d == load_ans[3]):
			answered_correctly = 1
			# print(answered_correctly)
		else:
			answered_correctly = -1
			# print(answered_correctly)
		return answered_correctly

	def update(self):
		answer = False
		begin_quiz_button = button.Button(SCREEN_WIDTH//2 -50, SCREEN_HEIGHT//2 + 50 , start_quiz_btn_img, 1)
		submit_quiz_button = button.Button(150, self.y + self.max_offset + 20 , submit_quiz_btn_img, 1)
		if begin_quiz_button.draw(screen):
			self.start_quiz = True
		if self.start_quiz:
			screen.blit(self.image, (self.x, self.y))
			self.display_ques()
			self.display_options()
			if submit_quiz_button.draw(screen):
				answer = self.check_ans()
		return answer
		
quiz = Quiz()

def home_page(screen):
	screen.fill(BG)
	disease = ""
	answer_here = False
	aids_btn = button.Button(100, 50, aids_img, 1)
	copd_btn = button.Button(400, 50, copd_img, 1)
	heartattack_btn = button.Button(700, 50, heartattack_img, 1)
	diabetes_btn = button.Button(100, 300, diabetes_img, 1)
	breast_cancer_btn = button.Button(400, 300, breast_cancer_img, 1)
	hepatitis_btn = button.Button(700, 300, hepatitis_img, 1)
	alziemers_btn = button.Button(100, 550, alziemers_img, 1)
	if aids_btn.draw(screen):
		disease = "aids"
		answer_here = True
	if copd_btn.draw(screen):
		disease = "copd"
		answer_here = True
	if heartattack_btn.draw(screen):
		disease = "heart_attack"
		answer_here = True
	if diabetes_btn.draw(screen):
		disease = "diabetes"
		answer_here = True
	if breast_cancer_btn.draw(screen):
		disease = "Breast_Cancer"
		answer_here = True
	if hepatitis_btn.draw(screen):
		disease = "hepatitis"
		answer_here = True
	if alziemers_btn.draw(screen):
		disease = "alziemers"
		answer_here = True
	return answer_here, disease


#create screen fades
intro_fade = ScreenFade(1, BLACK, 4)
death_fade = ScreenFade(2, PINK, 4)


#create buttons
start_button = button.Button(SCREEN_WIDTH // 2 - 130, SCREEN_HEIGHT // 2 - 150, start_btn_image, 1)
exit_button = button.Button(SCREEN_WIDTH // 2 - 110, SCREEN_HEIGHT // 2 + 50, end_btn_image, 1)
restart_button = button.Button(SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, restart_btn_img, 2)

#create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()
tokens_group = pygame.sprite.Group()
information_group = pygame.sprite.Group()

#create empty tile list
world_data = []
for row in range(NUM_ROWS):
	r = [-1] * NUM_COLS
	world_data.append(r)
#load in level data and create world
with open(f'level{level}_data.csv', newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
world = World()
player, health_bar = world.process_data(world_data)

open_homepage = False
homepage_counter = 0

# point1 = InfoPoints(health_box_img, "Hey welcome to the game", 3)
# load_infopoints()

run = True
while run:

	clock.tick(FPS)

	if begin_game == False:
		#draw menu
		screen.fill(BG)
		#add buttons
		if start_button.draw(screen):
			open_homepage = True
			homepage_counter = 60
			# begin_game = True
			# begin_intro = True
		if open_homepage == True:
			homepage_counter -= 1
			if homepage_counter < 0:
				homepage_counter = 0
				# print("Here")
				further, linee = home_page(screen)
				disease = linee
				if further:
					begin_intro = True
					begin_game = True
		if open_homepage == False:
			if exit_button.draw(screen):
				run = False
	else:
		#update background
		draw_bg()
		#draw world map
		world.draw()
		#show player health
		health_bar.draw(player.health)
		#show ammo
		draw_text('AMMO: ', Futura_font, WHITE, 10, 35)
		for x in range(player.bullets):
			screen.blit(bullet_image, (90 + (x * 10), 40))
		#show grenades
		draw_text('GRENADES: ', Futura_font, WHITE, 10, 60)
		for x in range(player.bombs):
			screen.blit(grenade_image, (135 + (x * 15), 60))
		# point1.update()


		player.update()
		player.draw()

		for enemy in enemy_group:
			enemy.watch()
			enemy.update()
			enemy.draw()

		#update and draw groups
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		tokens_group.update()
		information_group.update()
		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)
		tokens_group.draw(screen)
		information_group.draw(screen)

		#show intro
		if begin_intro == True:
			if intro_fade.fade():
				begin_intro = False
				intro_fade.fade_counter = 0


		#update player actions
		if player.alive:
			#shoot bullets
			if shoot:
				player.fire_bullet()
			#throw grenades
			elif grenade and grenade_thrown == False and player.bombs > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
				 			player.rect.top, player.direction)
				grenade_group.add(grenade)
				#reduce grenades
				player.bombs -= 1
				grenade_thrown = True
			if player.in_air:
				player.update_action(2)#2: jump
			elif moving_left or moving_right:
				player.update_action(1)#1: run
			else:
				player.update_action(0)#0: idle
			scroll_screen, level_complete, end_reached = player.move(moving_left, moving_right)
			scroll_background -= scroll_screen
			#check if player has completed the level
			if player.collection == 6:
				if end_reached == True:
					# start quiz
					correctly_answered = 0
					correctly_answered = quiz.update()
					# correctly_answered = answered_correctly
					if correctly_answered == 1:
						if level_complete:
							begin_intro = True
							level += 1
							scroll_background = 0
							world_data = reset_level()
							if level <= MAX_LEVELS:
								#load in level data and create world
								with open(f'level{level}_data.csv', newline='') as csvfile:
									reader = csv.reader(csvfile, delimiter=',')
									for x, row in enumerate(reader):
										for y, tile in enumerate(row):
											world_data[x][y] = int(tile)
								world = World()
								player, health_bar = world.process_data(world_data)
					if correctly_answered == -1:
						screen.blit(wrong_ans_img, (SCREEN_WIDTH//2 - (wrong_ans_img.get_width()//2), SCREEN_HEIGHT//2 - (wrong_ans_img.get_height()//2)))
						# pass
						#restart level
			else:
				# player has not collected all 6 info points
				if end_reached:
					screen.blit(start_btn_image, (200	,200))
		else:
			scroll_screen = 0
			if death_fade.fade():
				if restart_button.draw(screen):
					death_fade.fade_counter = 0
					begin_intro = True
					scroll_background = 0
					world_data = reset_level()
					#load in level data and create world
					with open(f'level{level}_data.csv', newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
					world = World()
					player, health_bar = world.process_data(world_data)


	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				moving_left = True
			if event.key == pygame.K_RIGHT:
				moving_right = True
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_q:
				grenade = True
			if event.key == pygame.K_UP and player.alive:
				player.jump = True
				jump_sound.play()
			if event.key == pygame.K_ESCAPE:
				run = False


		#keyboard button released
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT:
				moving_left = False
			if event.key == pygame.K_RIGHT:
				moving_right = False
			if event.key == pygame.K_SPACE:
				shoot = False
			if event.key == pygame.K_q:
				grenade = False
				grenade_thrown = False


	pygame.display.update()

pygame.quit()
