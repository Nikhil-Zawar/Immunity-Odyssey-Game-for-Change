import pygame
import os

pygame.init()


SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

# set frame rate
clock = pygame.time.Clock()
FPS = 60

# define game variables
GRAVITY = 0.75

# define player actions and variables
moving_left = False
moving_right = False
shoot = False

# load images
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()

# define colours
BG = (0,0,180)
GREEN = (0,144,0)

def draw_bg():
    screen.fill(BG)
    pygame.draw.line(screen, GREEN, (0,500), (SCREEN_WIDTH, 500), 10)


class living(pygame.sprite.Sprite):
    def __init__(self, char_type, x, y, scale, x_vel, ammo):
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
        self.direction = 1 #1 means looking towards right, and -1 means looking towards left
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()


        # load all images for the players
        animation_types = ['Idle', 'Run', 'Jump', 'Death']
        for typ in animation_types:
            # reset a temporary list of images
            temp_list = []
            # count number of files in the folder using os
            number_of_frames = len(os.listdir(f'img/{self.char_type}/{typ}'))
            for i in range(number_of_frames):
                img = pygame.image.load(f'img/{self.char_type}/{typ}/{i}.png').convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width()*scale), int(img.get_height()*scale)))
                temp_list.append(img)
            self.animation_list.append(temp_list)
            
        temp_list = []
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)

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



    def update_action(self, new_action):
        # first check if the new action is different fromt the previous one
        if new_action != self.action :
            self.action = new_action
            #  update the animation settings
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def move(self, moving_left, moving_right):
        # reset movement variables
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
            self.y_vel = -11
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
        if self.rect.bottom + dy > 500 :
            dy = 500 - self.rect.bottom
            self.in_air = False
        


        # update rectangle
        self.rect.x += dx
        self.rect.y += dy

    def shoot(self):
        # shoot bullets
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = 20
            self.ammo -= 1
            bullet =  Bullet(self.rect.centerx + (0.6 * self.rect.size[0] * self.direction), self.rect.centery, self.direction)
            bullet_group.add(bullet)
        
    def update_everything(self):
        self.update_animation()
        self.draw()
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
        self.rect.x += (self.direction * self.speed)
        # check if bullet has gone off screen
        if self.rect.right < 0 or self.rect.left > SCREEN_WIDTH:
            self.kill()
        # check collision with characters
        if pygame.sprite.spritecollide(player, bullet_group, False):
            if player.alive :
                player.health -= 5
                self.kill()
        if pygame.sprite.spritecollide(enemy, bullet_group, False):
            if enemy.alive :
                enemy.health -= 20
                self.kill()



# Create sprite groups
bullet_group = pygame.sprite.Group()
    
player = living("player",200,200,2,3,20)
enemy = living("enemy", 400, 200,2,3,20)



run = True
while run:

    clock.tick(FPS)

    draw_bg()

    player.update_everything()
    enemy.update_everything()

    # update and draw groups
    bullet_group.update()
    bullet_group.draw(screen)


    
    # Update player actions
    if player.alive:
        if shoot :
            player.shoot()
        if moving_left or moving_right:
            player.update_action(1) # 1 : run
        elif player.in_air :
            player.update_action(2) # 2 : jump
        else:
            player.update_action(0) # 0 : idle
        player.move(moving_left, moving_right)
        enemy.move(moving_left, moving_right)

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
            if event.key == pygame.K_UP and player.alive:
                player.jump = True
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



    pygame.display.update()







pygame.quit()
