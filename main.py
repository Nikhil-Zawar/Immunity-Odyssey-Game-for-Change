import pygame
import os
import random
import csv
import button
import pygame.image

pygame.init()


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# set frame rate
clock = pygame.time.Clock()
FPS = 60

# define game variables
SCROLL_THRESH = 200
GRAVITY = 0.75
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT//ROWS
TILE_TYPES = 21
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False

MAX_LEVELS = 5

# define player actions and variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False

# load music
# pygame.mixer.music.load('audio/music2.mp3')
# pygame.mixer.music.set_volume(0.3)
# pygame.mixer.music.play(-1,0.0,5000)

jump_fx = pygame.mixer.Sound('audio/Jump.wav')
jump_fx.set_volume(0.05)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.05)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.05)

# load background images
# button images
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

# background images
pine1_img = pygame.image.load('img/background/pine1.png').convert_alpha()
pine2_img = pygame.image.load('img/background/pine2.png').convert_alpha()
mountain_img = pygame.image.load('img/background/mountain.png').convert_alpha()
sky_cloud_img = pygame.image.load('img/background/sky_cloud.png').convert_alpha()

# load tile images for the world
img_list = []
for x in range(TILE_TYPES):
    img = pygame.image.load(f'img/tile/{x}.png')
    img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    img_list.append(img)

# load images
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()
health_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()
item_boxes = {
    "Health" : health_box_img,
    "Ammo" : ammo_box_img,
    "Grenade" : grenade_box_img
}
# define colours
BG = (0,0,180)
GREEN = (0,144,0)
WHITE = (255,255,255)
RED = (255,0,0)

# define font
font = pygame.font.SysFont('Futura', 30)

def draw_text(text, font, color, x, y, scale):
    img = font.render(text, True, color)
    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
    screen.blit(img, (x,y))

def draw_bg():
    screen.fill(BG)
    width = sky_cloud_img.get_width()
    for x in range(5):
        screen.blit(sky_cloud_img, (width*x - bg_scroll*0.5,0))
        screen.blit(mountain_img, (width*x - bg_scroll*0.6, SCREEN_HEIGHT - mountain_img.get_height() - 300))
        screen.blit(pine1_img, (width*x - bg_scroll*0.7, SCREEN_HEIGHT - pine1_img.get_height() - 150))
        screen.blit(pine2_img, (width*x - bg_scroll*0.8, SCREEN_HEIGHT - pine2_img.get_height()))
    # pygame.draw.line(screen, GREEN, (0,500), (SCREEN_WIDTH, 500), 10)

def reset_level():
    enemy_group.empty()
    bullet_group.empty()
    grenade_group.empty()
    explosion_group.empty()
    item_box_group()
    decoration_group()
    water_group()
    exit_group()

    # create empty tile list
    wdata = []
    for row in range(ROWS):
        r = [-1]*COLS
        wdata.append(r)
    
    return wdata


class living(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, x_vel, ammo, grenades):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.char_type = char_type
        self.x_vel = x_vel
        self.y_vel = 0
        self.shoot_cooldown = 0
        self.start_ammo = ammo
        self.ammo = ammo
        self.health = 100
        self.max_health = self.health
        self.grenades = grenades
        self.direction = 1 #1 means looking towards right, and -1 means looking towards left
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        
        # ai specific variables
        self.move_counter = 0
        self.vision = pygame.Rect(0,0,150,20)
        self.idling = False
        self.idling_counter = 0

        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for animation_type in animation_types:
            # reset a temporary list of images
            temp_list = []
            # count number of files in the folder using os
            number_of_frames = len(os.listdir(f'img/{self.char_type}/{animation_type}'))
            for i in range(number_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{animation_type}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
            
        temp_list = []
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update_animation(self):
        # define timer - this will control the speed of the animation
        ANIMATION_COOLDOWN = 100
        # update image depending on current frame
        self.image = self.animation_list[self.action][self.frame_index]
        # Check if eoungh time has passed from the last update
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
        # if the animation has run out then reset back to start
        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action == 3:
                self.frame_index = len(self.animation_list[self.action]) - 1
            else:
                self.frame_index = 0

    def ai(self):
        if self.alive and player.alive:
            if self.idling == False and random.randint(1,200) == 1:
                self.idling = True
                self.idling_counter = 50
            # check if the ai is near the player
            if self.vision.colliderect(player.rect):
                # stop running and face the player
                self.update_action(0)
                self.shoot()
            else:
                if self.idling == False:
                    if self.direction == 1:
                        ai_moving_right = True
                    else:
                        ai_moving_right = False
                    ai_moving_left = not ai_moving_right
                    self.move(ai_moving_left, ai_moving_right)
                    self.update_action(1)
                    self.move_counter += 1

                    # update ai vision rect as the enemy moves
                    self.vision.center = (self.rect.centerx + int(self.vision.width // 2) * self.direction, self.rect.centery)
                    # pygame.draw.rect(screen, RED, self.vision, 3)

                    if self.move_counter > TILE_SIZE:
                        self.direction *= -1
                        self.move_counter *= -1
                else:
                    self.idling_counter -= 1
                    if self.idling_counter == 0:
                        self.idling = False
        self.rect.x += screen_scroll



    def update_action(self, new_action):
        # first check if the new action is different fromt the previous one
        if new_action != self.action :
            self.action = new_action
            #  update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def move(self, moving_left, moving_right):
        # reset movement variables
        screen_scroll = 0
        dx = 0
        dy = 0

        # assign movement variables if moving left or right
        if moving_left:
            dx = -self.x_vel
            self.flip = True
            self.direction = -1
        if moving_right:
            dx = self.x_vel
            self.flip = False
            self.direction = 1

        # jump
        if self.jump == True and self.in_air == False:
            self.y_vel = -15
            # negetive value because y = 0 at the top of the screen and increases its value as we go down
            #  at the bottom line the value of y = 800
            self.jump = False
            self.in_air = True
        
        # apply gravity
        self.y_vel += GRAVITY
        if self.y_vel > 10:
            self.y_vel = 10
        dy += self.y_vel

        # check collsion with floor
        # check for collision with the ground
        for tile in world.obstacle_list:
            # check collision in horizontal direction
            if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                dx = 0
                # if the ai has hit the wall then turn around
                if self.char_type == 'enemy':
                    self.direction *= -1
                    self.move_counter = 0
            # check collision in vertical direction
            if tile[1].colliderect(self.rect.x , self.rect.y + dy, self.width, self.height):
                # check if below the ground (jumping)
                if self.y_vel < 0:
                    self.y_vel = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the groung (falling)
                elif self.y_vel >= 0:
                    self.y_vel = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        
        # temporary floor 
        # if self.rect.bottom + dy > 500 :
        #     dy = 500 - self.rect.bottom
        #     self.in_air = False

        # check collision with water
        if pygame.sprite.spritecollide(self, water_group, False):
            self.health = 0
        
        level_complete = False
        if pygame.sprite.spritecollide(self, exit_group, False):
            level_complete = True

        # check is fallen off the map
        if self.rect.bottom > SCREEN_HEIGHT:
            self.health = 0
        

        # check if going off the edges of the screen
        if self.char_type == 'player':
            if self.rect.left + dx < 0 or self.rect.right + dx >SCREEN_WIDTH:
                dx = 0

        # update rectangle
        self.rect.x += dx
        self.rect.y += dy

        # update scroll based on player position
        if self.char_type == 'player':
            if (self.rect.right > SCREEN_WIDTH - SCROLL_THRESH\
                 and bg_scroll< (world.level_length * TILE_SIZE) - SCREEN_WIDTH)\
                  or (self.rect.left < SCROLL_THRESH and bg_scroll > abs(dx)):
                self.rect.x -= dx
                screen_scroll = -dx
                
        return screen_scroll, level_complete


    def shoot(self):
        # shoot bullets
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            self.ammo -= 1
            bullet =  Bullet(self.rect.centerx + (0.8 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
            shot_fx.play()


    def update_everything(self):
        self.update_animation()
        self.check_alive()
        # update cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def draw(self):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
        # pygame.draw.rect(screen, (255,0,0), self.rect, 1)


class World():
    def __init__(self):
        self.obstacle_list = []

    def process_data(self, data):
        self.level_length = len(data[0])
        #  iterate through each value in level  data file
        for y, row in enumerate(data):
            for x, tile in enumerate(row):
                if tile >= 0:
                    img = img_list[tile]
                    img_rect = img.get_rect()
                    img_rect.x = x * TILE_SIZE
                    img_rect.y = y * TILE_SIZE
                    tile_data = (img, img_rect)
                    if(tile < 9):
                        self.obstacle_list.append(tile_data)
                    elif(tile >= 9 and tile <= 10):
                        water = Water(img, x*TILE_SIZE, y*TILE_SIZE)
                        water_group.add(water)
                    elif(tile >= 11 and tile <=14):
                        decoration = Decoration(img, x*TILE_SIZE, y*TILE_SIZE)
                        decoration_group.add(decoration)
                    elif(tile == 15): # create player
                        player = living('player', x*TILE_SIZE, y*TILE_SIZE, 0.7, 6, 20, 5)
                        health_bar = HealthBar(10,10,player.health, player.max_health)
                    elif tile == 16: # create enemy
                        enemy = living('enemy', x*TILE_SIZE, y*TILE_SIZE, 2.5, 3, 20, 5)
                        enemy_group.add(enemy)
                    elif tile == 17: # create ammo box
                        item_box = ItemBox('Ammo', x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 18: # create grenade box
                        item_box = ItemBox('Grenade', x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 19: #create health box
                        item_box = ItemBox('Health', x*TILE_SIZE, y*TILE_SIZE)
                        item_box_group.add(item_box)
                    elif tile == 20: # create exit
                        exit = Exit(img, x*TILE_SIZE, y*TILE_SIZE)
                        exit_group.add(exit)
        return player, health_bar
    
    def draw(self):
        for tile in self.obstacle_list:
            tile[1][0] += screen_scroll
            screen.blit(tile[0], tile[1])

class Water(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class Decoration(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll


class Exit(pygame.sprite.Sprite):
    def __init__(self, img, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = img
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2, y + (TILE_SIZE - self.image.get_height()))

    def update(self):
        self.rect.x += screen_scroll

class ItemBox(pygame.sprite.Sprite):
    def __init__(self, item_type, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.item_type = item_type
        self.image = item_boxes[self.item_type]
        self.rect = self.image.get_rect()
        self.rect.midtop = (x + TILE_SIZE//2 , y + (TILE_SIZE - self.image.get_height()))
    
    def update(self):
        # scrolling update
        self.rect.x += screen_scroll
        # the main update function below
        if pygame.sprite.collide_rect(self, player):
            if(self.item_type == 'Health'):
                player.health += 25
                if player.health > player.max_health:
                    player.health = player.max_health
            elif(self.item_type == 'Ammo'):
                player.ammo += 10
            elif(self.item_type == 'Grenade'):
                player.grenades += 3
            self.kill()


class HealthBar():
    def __init__(self, x, y, health, max_health):
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health

    def draw(self, health):
        # update with new health
        self.health = health
        # define health ratio
        ratio = self.health / self.max_health
        pygame.draw.rect(screen, RED, (self.x, self.y, 150, 20))
        pygame.draw.rect(screen, GREEN, (self.x, self.y, int(150 * ratio), 20))

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.speed = 10
        self.image = bullet_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
    
    def update(self):
        #  move bullet
        self.rect.x += (self.direction * self.speed) + screen_scroll
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()

        # check for collision with level
        for tile in world.obstacle_list:
            if tile[1].colliderect(self.rect):
                self.kill()
        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive :
                player.health -= 5
                self.kill()
        for enemy in enemy_group:
            if pygame.sprite.spritecollide(enemy, bullet_group, False):
                if enemy.alive :
                    enemy.health -= 20
                    self.kill()


class Grenade(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.timer = 100
        self.y_vel = -10
        self.x_vel = 6
        self.image = grenade_img
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.direction = direction
        self.width = self.image.get_width()
        self.height = self.image.get_height()

    def update(self):
        self.y_vel += GRAVITY*0.5
        dx = self.x_vel * self.direction
        dy = self.y_vel

        # check collision with level
        for tile in world.obstacle_list:
            # check collision with the walls
            if tile[1].colliderect(self.rect.x + dx, self.rect.y , self.width, self.height):
                self.direction *= -1
                dx = self.direction * self.x_vel
            # check for collision in the y direction
            if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                self.x_vel = 0
                # check if below the ground, (thrown up)
                if self.y_vel < 0:
                    # self.y_vel = 0
                    dy = tile[1].bottom - self.rect.top
                # check if above the ground (falling)
                elif self.y_vel >= 0:
                    # self.y_vel = 0
                    self.in_air = False
                    dy = tile[1].top - self.rect.bottom
        
        # check collision with the floor
        # if self.rect.bottom + dy > player.rect.bottom:
        #     dy = player.rect.bottom - self.rect.bottom
        #     self.x_vel = 0
        # check collsion with the sides of screen/walls - here we want the grenade to bounce
        # if self.rect.left + dx <0 or self.rect.right + dx > SCREEN_WIDTH:
        #     self.direction *= -1
        #     dx = self.x_vel * self.direction
        # update grenade position
        self.rect.x += dx + screen_scroll
        self.rect.y += dy
        # countdown timer - the fuse of the grenade
        self.timer -= 1
        if self.timer <= 0:
            self.kill()
            grenade_fx.play()
            explosion = Explosion(self.rect.x, self.rect.y, 0.5)
            explosion_group.add(explosion)
            #  here we do a check - do damage to anyone who is nearby
            if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE*2 and \
            abs(self.rect.centery - player.rect.centery) < TILE_SIZE*2 :
                player.health -= 50
            for enemy in enemy_group:
                if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE*2 and \
                abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE*2 :
                    enemy.health -= 50


class Explosion(pygame.sprite.Sprite):
    def __init__(self, x, y, scale):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        for num in range(1,6):
            img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
            pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
            self.images.append(img)
        self.frame_index = 0
        self.image = self.images[self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
        self.counter = 0

    def update(self):
        EXPLOSION_SPEED = 4
        # scroll update
        self.rect.x += screen_scroll
        # update explosion animation
        self.counter += 1
        if self.counter > EXPLOSION_SPEED :
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.images) :
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
        if self.direction == 1: # whole screen fade
            pygame.draw.rect(screen, self.colour, (0-self.fade_counter,0,SCREEN_WIDTH//2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (SCREEN_WIDTH//2 +self.fade_counter,0,SCREEN_WIDTH//2, SCREEN_HEIGHT))
            pygame.draw.rect(screen, self.colour, (0,SCREEN_HEIGHT//2 +self.fade_counter,SCREEN_WIDTH, SCREEN_HEIGHT//2))
            pygame.draw.rect(screen, self.colour, (0,0- self.fade_counter,SCREEN_WIDTH, SCREEN_HEIGHT//2))
        if self.direction == 2: # vertical screen fade down
            pygame.draw.rect(screen, self.colour, (0,0,SCREEN_WIDTH, 0+self.fade_counter))
        if self.fade_counter >= SCREEN_WIDTH:
            fade_complete
        
        return fade_complete

# create screen fades
intro_fade = ScreenFade(1, GREEN, 4)
death_fade = ScreenFade(2, RED, 4)


# create buttons
start_button = button.Button(SCREEN_WIDTH //2 - 130, SCREEN_HEIGHT//2 - 150, start_img, 1)
exit_button = button.Button(SCREEN_WIDTH //2 - 110, SCREEN_HEIGHT//2 + 50, exit_img, 1)
restart_button = button.Button(SCREEN_WIDTH //2 - 100, SCREEN_HEIGHT//2 - 50, restart_img, 2)

# Create sprite groups
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# -- create item boxes
# item_box1 = ItemBox('Health', 100, 300)
# item_box_group.add(item_box1)
# item_box2 = ItemBox('Ammo', 400, 300)
# item_box_group.add(item_box2)
# item_box3 = ItemBox('Grenade', 600, 300)
# item_box_group.add(item_box3)
    
# player = living("player",200,200,0.7,3,20,5)
# health_bar = HealthBar(10,10,player.health, player.max_health)

# enemy1 = living("enemy", 400, 200,2,2,100,0)
# enemy2 = living("enemy", 800, 200,2,2,100,0)
# enemy_group.add(enemy1)
# enemy_group.add(enemy2)

# create empty tile list
world_data = []
for row in range(ROWS):
    r = [-1] * COLS
    world_data.append(r)

# load in level data
with open(f'level{level}_data.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for x, row in enumerate(reader):
        for y, tile in enumerate(row):
            world_data[x][y] = int(tile)

# process data
world = World()
player, health_bar = world.process_data(world_data)



run = True
while run:

    clock.tick(FPS)

    if start_game == False:
        # draw menu
        screen.fill(BG)
        # add buttons
        if start_button.draw(screen):
            start_game = True
            start_intro = True
        if exit_button.draw(screen):
            run = False

        # start_game = True
    else:


        # update backgroung
        draw_bg()
        # draw world
        world.draw()


        # display text
        health_bar.draw(player.health)
        draw_text(f'Player health: {player.health}', font, RED, 50,100,1)
        # show ammo
        draw_text(f'Ammo: {player.ammo}', font, WHITE, 50,140,1)
        for x in range(player.ammo):
            screen.blit(bullet_img, (160 + (x*10), 145))
        # show grenade
        draw_text(f'Grenades: {player.grenades}', font, WHITE, 50,180,1)
        for x in range(player.grenades):
            screen.blit(grenade_img, (180 + (x*10), 185))

        player.update_everything()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update_everything()
            enemy.draw()
        # update and draw groups
        bullet_group.update()
        bullet_group.draw(screen)
        grenade_group.update()
        grenade_group.draw(screen)
        explosion_group.update()
        explosion_group.draw(screen)
        item_box_group.update()
        item_box_group.draw(screen)
        decoration_group.update()
        decoration_group.draw(screen)
        water_group.update()
        water_group.draw(screen)
        exit_group.update()
        exit_group.draw(screen)

        # show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0 
        
        # Update player actions
        if player.alive:
            # shoot bullets
            if shoot :
                player.shoot()
            # throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx +(player.direction * (player.rect.width) * 0.5) , player.rect.centery, player.direction)
                grenade_group.add(grenade)
                grenade_thrown = True
                player.grenades -= 1
            if moving_left or moving_right:
                player.update_action(1) # 1 : run
            elif player.in_air :
                player.update_action(2) # 2 : jump
            else:
                player.update_action(0) # 0 : idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll
            # check if player has completed the level
            if level_complete:
                start_intro = True
                level += 1
                bg_scroll = 0
                world_data = reset_level()
                if level <= MAX_LEVELS:
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)

            # enemy.move(moving_left, moving_right)
        else:
            screen_scroll = 0
            if death_fade.fade():
                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)







    # for loop is the event handler
    for event in pygame.event.get():
        # quit game
        if event.type == pygame.QUIT:
            run = False
        # keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_SPACE:
                shoot = True
            if event.key == pygame.K_LCTRL:
                grenade = True
                grenade_thrown = False
            if event.key == pygame.K_UP and player.alive:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False

        
        # keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_SPACE:
                shoot = False
            if event.key == pygame.K_LCTRL:
                grenade = False



    pygame.display.update()







pygame.quit()