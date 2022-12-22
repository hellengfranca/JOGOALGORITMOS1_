
import pygame
from pygame.locals import *
from pygame import mixer
import pickle
from os import path


pygame.mixer.pre_init(44100, 16, 2, 512)
mixer.init()
pygame.init()

clock = pygame.time.Clock()
fps = 60
screen_width = 600
screen_height = 600

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('BIRTHDAY RUNAWAY')

# definindo a fonte
coin_points = pygame.font.SysFont('Minecraft.ttf', 70)
font_points = pygame.font.SysFont('Minecraft.ttf', 30)

# variaveis
tile_size = 30
gameover = 0
start_menu = True
level = 0
max_levels = 7
points = 0

# cores
white = (255, 255, 255)
yellow = (255, 255, 0)


# images
lua_img = pygame.image.load('lua.png')
ceu_img = pygame.image.load('BACKGROUND edited size.jpg')
restart_img = pygame.image.load('restart button.png')
start_img = pygame.image.load('start button.png')
exit_img = pygame.image.load('exit button.png')

# sounds and music
pygame.mixer.music.load('menu.wav')
pygame.mixer.music.play(-1, 0, 5000)
coin_sound = pygame.mixer.Sound('coin.wav')
coin_sound.set_volume(0.4)
jump_sound = pygame.mixer.Sound('jump.wav')
jump_sound.set_volume(0.4)
gameover_sound = pygame.mixer.Sound('gameover.wav')
gameover_sound.set_volume(0.5)
menu_sounds = pygame.mixer.Sound('menu.wav')
menu_sounds.set_volume((0.3))

def drawtext(texto, fonte, texto_col, x, y):
    img = fonte.render(texto, True, texto_col)
    screen.blit(img, (x, y))



# reset level
def reset_level(level):
    player.reset(100, screen_height - 100)
    poisoncake_group.empty()
    lava_group.empty()
    exit_group.empty()
    if path.exists(f"level{level}_data"):
        pickle_in = open(f"level{level}_data", 'rb')
        world_data = pickle.load(pickle_in)
    world = World(world_data)

    return world


class Button():
    def __init__(self, x, y, image):
        self.image = pygame.transform.scale(image, (180, 180))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.clicked = False

    def draw(self):
        action = False
        # get position
        pos = pygame.mouse.get_pos()
        # check mouse presses
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False
        # to show the button on the screen
        screen.blit(self.image, self.rect)

        return action

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):

        self.reset(x, y)

    def update(self, gameover):
        dx = 0
        dy = 0
        andar_direito = 5

        if gameover == 0:
            # getting the commands
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE] and self.jumped == False and self.jumping == False:
                jump_sound.play()
                self.velocity_y = -16
                self.jumped = True

            if key[pygame.K_SPACE] == False:
                self.jumped = False
            if key[pygame.K_LEFT]:
                dx -= 3.5
                self.counter += 1
                self.direction = -1
            if key[pygame.K_RIGHT]:
                dx += 3.5
                self.counter += 1
                self.direction = 1
            if key[pygame.K_LEFT] == False and key[pygame.K_RIGHT] == False:
                self.counter = 0
                self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                    self.image = self.images_left[self.index]

            # animation
            if self.counter > andar_direito:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images_right):
                    self.index = 0
                if self.direction == 1:
                    self.image = self.images_right[self.index]
                if self.direction == -1:
                        self.image = self.images_left[self.index]


            # gravity
            self.velocity_y += 1
            if self.velocity_y > 10:
                self.velocity_y = 10
            dy += self.velocity_y

            # check collision
            self.jumping = True
            for tile in world.tile_list:
                #in x
                if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width, self.height):
                    dx = 0
                # in y
                if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width, self.height):
                    # check if bellow the ground
                    # jumping
                    if self.velocity_y < 0:
                        dy = tile[1].bottom - self.rect.top
                        self.velocity_y = 0
                    # falling
                    elif self.velocity_y >= 0:
                        dy = tile[1].top - self.rect.bottom
                        self.velocity_y = 0
                        self.jumping = False

            # check collision w/ obstacle
            if pygame.sprite.spritecollide(self, poisoncake_group, False):
                gameover_sound.play()
                gameover = -1

            # check collision w/ lava
            if pygame.sprite.spritecollide(self, lava_group, False):
                gameover_sound.play()
                gameover = -1

            # check collision with exit
            if pygame.sprite.spritecollide(self, exit_group, False):
                gameover = 1



            # update player positions
            self.rect.x += dx
            self.rect.y += dy

        elif gameover == -1:
            self.image = self.deadimg
            drawtext('GAME OVER', coin_points, yellow, (screen_width - 450), (screen_height - 500))
            if self.rect.y > 200:
                self.rect.y -= 5

            #draw player
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2)

        return gameover

    def reset(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images_right = []
        self.images_left = []

        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img_right = pygame.image.load(f'personagem +x {num}.png')
            img_right = pygame.transform.scale(img_right, (28, 35))
            img_left = pygame.transform.flip(img_right, True, False)
            self.images_left.append(img_left)
            self.images_right.append(img_right)
        dead = pygame.image.load('ghost.png')
        self.deadimg = pygame.transform.scale(dead, (tile_size, tile_size))
        self.image = self.images_right[self.index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.image.get_width()
        self.height = self.image.get_height()
        self.velocity_y = 0
        self.jumped = False
        self.direction = 0
        self.jumping = True


class World():
    def __init__(self, data):
        self.tile_list = []

        #load images
        dirt_img = pygame.image.load('DIRT BLOCK.png')
        grass_img = pygame.image.load('GRASS BLOCK.png')
        restart_img = pygame.image.load('start button.png')


        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1:
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)

                if tile == 2:
                    img = pygame.transform.scale(grass_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)
                if tile == 3:
                    poisoncake = Obstacle(col_count * tile_size, row_count * tile_size)
                    poisoncake_group.add(poisoncake)
                if tile == 6:
                    lava = Lava(col_count * tile_size, row_count * tile_size + (tile_size//1.85))
                    lava_group.add(lava)
                if tile == 7:
                    coin = Coin(col_count * tile_size + (tile_size//2), row_count * tile_size + (tile_size))
                    coin_group.add(coin)
                if tile == 8:
                    exit = Exit(col_count * tile_size, row_count * tile_size - (tile_size))
                    exit_group.add(exit)
                col_count += 1
            row_count += 1

    def draw(self):
        for tile in self.tile_list:
            screen.blit(tile[0], tile[1])
            pygame.draw.rect(screen, (255, 255, 255), tile[1], 1)

class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = pygame.image.load('poison cake.png')
        self.image = pygame.transform.scale(self.images, (tile_size - 15, tile_size))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.move_direction = 1
        self.move_counter = 0

    def update(self):
        self.rect.x += self.move_direction
        self.move_counter += 1
        if abs(self.move_counter) > 40:
            self.move_direction *= -1
            self.move_counter *= -1
        

class Lava(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = pygame.image.load('lava.png')
        self.image = pygame.transform.scale(self.images, (tile_size, tile_size//2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = pygame.image.load('coin.png')
        self.image = pygame.transform.scale(self.images, (tile_size// 1.5, tile_size// 1.5))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

class Exit(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = pygame.image.load('porta.png')
        self.image = pygame.transform.scale(self.images, (int(tile_size*0.95), tile_size * 2))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


player = Player(100, screen_height - 100)
poisoncake_group = pygame.sprite.Group()
lava_group = pygame.sprite.Group()
coin_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()

# load the level and create the world
if path.exists(f"level{level}_data"):
    pickle_in = open(f"level{level}_data", 'rb')
    world_data = pickle.load(pickle_in)
world = World(world_data)

# create button
restart_button = Button(screen_width // 2 - 90, screen_height // 2 - 100, restart_img)
start_button = Button(screen_width // 2 - 230, screen_height // 2 - 100, start_img)
exit_button = Button(screen_width // 2 + 40, screen_height// 2 - 100, exit_img)
run = True
while run:

    clock.tick(fps)

    screen.blit(ceu_img, (0, 0))
    screen.blit(lua_img, (100, 100))


    if start_menu == True:
        if exit_button.draw():
            run = False
        if start_button.draw():
            pygame.mixer.music.stop()
            start_menu = False


    else:
        world.draw()

        if gameover == 0:
            poisoncake_group.update()

            # update points
            # check if coin has been collected
            if pygame.sprite.spritecollide(player, coin_group, True):
                coin_sound.play()
                points += 1
            drawtext('coins = ' + str(points), font_points, white, tile_size - 10, 10)

        poisoncake_group.draw(screen)
        lava_group.draw(screen)
        coin_group.draw(screen)
        exit_group.draw(screen)

        gameover = player.update(gameover)

        # if player dies
        if gameover == -1:
            if restart_button.draw():
                world_data = []
                world = reset_level(level)
                gameover = 0
        # if player wins the level
        if gameover == 1:
            # reset game and go to the next level
            level += 1
            points = 0
            if level <= max_levels:
                # reset level
                world_data = []
                world = reset_level(level)
                gameover = 0
            else:
                drawtext('VOCE VENCEU!', coin_points, yellow, (screen_width - 480), (screen_height - 400))
                if restart_button.draw():
                    level = 0
                    world_data = []
                    world = reset_level(level)
                    gameover = 0
                    points = 0


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    pygame.display.update()

pygame.quit()

