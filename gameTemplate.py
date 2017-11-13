#! /usr/bin/python
#MATT/CALEB/WYATT
#PYTHON FINAL PROJECT WIREFRAME
import math
from math import sqrt
import pygame
from pygame import *

WIN_WIDTH = 800
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30

def main():
    global cameraX, cameraY, alive
    alive = True
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pygame.display.set_caption("Use arrows to move!")
    timer = pygame.time.Clock()

    up = down = left = right = running = attack = defend = False
    bg = Surface((32,32))
    bg.convert()
    bg.fill(Color("#000000"))
    entities = pygame.sprite.Group()
    player = Player(32, 32)
    enemy = Enemy(32, 32)
    platforms = []
    x = y = 0
    level = [
        "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
        "P                                          P",
        "P                                          P",
        "P                                          P",
        "P                    PPPPPPPPPPP           P",
        "P                                          P",
        "P                                          P",
        "P                                          P",
        "P    PPPPPPPP                              P",
        "P                                          P",
        "P                          PPPPPPP         P",
        "P                 PPPPPP                   P",
        "P                                          P",
        "P                                          P",
        "P                                          P",
        "P          PPPPPP                          P",
        "P                                          P",
        "P                                          P",
        "P                                          P",
        "P                 PPPPPPPPPPP              P",
        "PPPPPPPPPPPP      P         PP             P",
        "P          PPPPPPPP         PPPP           P",
        "P                           PPPPPPP        E",
        "P                           PPPPPPPPP      E",
        "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",]
    # build the level
    for row in level:
        for col in row:
            if col == "P":
                p = Platform(x, y)
                platforms.append(p)
                entities.add(p)
            if col == "E":
                e = ExitBlock(x, y)
                platforms.append(e)
                entities.add(e)
            x += 32
        y += 32
        x = 0

    total_level_width  = len(level[0])*32
    total_level_height = len(level)*32
    camera = Camera(complex_camera, total_level_width, total_level_height)
    entities.add(player)
    entities.add(enemy)

    while alive == True:
        #alive = False
        timer.tick(60)
        global posX, posY ## tracers of the x,y coordinate of the sprite
        posX = player.rect.x
        posY = player.rect.y
        for e in pygame.event.get():
            if e.type == QUIT: raise SystemExit( "QUIT")
            if e.type == KEYDOWN and e.key == K_ESCAPE:
                raise SystemExit( "ESCAPE")
            if e.type == KEYDOWN and e.key == K_UP:
                up = True
            if e.type == KEYDOWN and e.key == K_DOWN:
                down = True
            if e.type == KEYDOWN and e.key == K_LEFT:
                left = True
            if e.type == KEYDOWN and e.key == K_RIGHT:
                right = True
            if e.type == KEYDOWN and e.key == K_SPACE:
                running = True
            if e.type == KEYDOWN and e.key == K_a:
                try:
                    entities.remove(weapon)
                except UnboundLocalError:
                    pass                
                attack = True   
                weapon = Weapon(8,8)                                    
                entities.add(weapon)
            
            if e.type == KEYUP and e.key == K_UP:
                up = False
            if e.type == KEYUP and e.key == K_DOWN:
                down = False
            if e.type == KEYUP and e.key == K_RIGHT:
                right = False
            if e.type == KEYUP and e.key == K_LEFT:
                left = False
            if e.type == KEYUP and e.key == K_a:
                break
                

        # draw background
        for y in range(32):
            for x in range(32):
                screen.blit(bg, (x * 32, y * 32))

        camera.update(player)
        # update player, draw everything else
        player.update(up, down, left, right, running, platforms, enemy, alive)
        enemy.update(entities, platforms, attack, player)
        if attack: 
            weapon.update(left, right, attack, platforms, entities, enemy)
        for e in entities:
            screen.blit(e.image, camera.apply(e))

        pygame.display.update()

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)

def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l+HALF_WIDTH, -t+HALF_HEIGHT, w, h)

def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l+HALF_WIDTH, -t+HALF_HEIGHT, w, h

    l = min(0, l)                           # stop scrolling at the left edge
    l = max(-(camera.width-WIN_WIDTH), l)   # stop scrolling at the right edge
    t = max(-(camera.height-WIN_HEIGHT), t) # stop scrolling at the bottom
    t = min(0, t)                           # stop scrolling at the top
    return Rect(l, t, w, h)

class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)


class Enemy(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = -2
        self.yvel = 0
        self.onGround = False
        self.image = Surface((32,32))
        self.image.fill(Color("#FFFF00"))
        self.image.convert()
        self.rect = Rect(WIN_WIDTH, y, 32, 32)  


    def update(self, entities, platforms, attack, player):
        if self.yvel < 0: self.onGround = True
        if not self.onGround: 
            self.yvel += 0.3
            if self.yvel > 100: self.yvel = 100
        self.rect.left += self.xvel
        self.collide(self.xvel,0, platforms, player, entities)
        self.rect.top += self.yvel
        self.onGround=False
        self.collide(0,self.yvel,platforms, player, entities)
        self.move_towards_player(player)
    
    def collide(self, xvel, yvel, platforms, player,entities):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if xvel < 0:
                    self.rect.left = p.rect.right 
                if xvel > 0:
                    self.rect.right = p.rect.left
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom

    def move_towards_player(self, player):
        # find normalized direction vector (dx, dy) between enemy and player
        dx, dy = self.rect.x - player.rect.x, self.rect.y - player.rect.y
        dist = sqrt(dx**2 + dy**2)
        try: 
            dx, dy = dx / dist, dy / dist
        except ZeroDivisionError:
            alive = False
        #print(dy)
        # move along this normalized vector towards the player at current speed
        if dx < 0:
            self.rect.x += dx * self.xvel*3
        else:
            self.rect.x += dx * self.xvel
        self.rect.y += dy * self.yvel

#class for weapon
class Weapon(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = 0
        self.image = Surface((8,8))
        self.image.fill(Color("#FF0000"))
        self.image.convert()
        self.rect = Rect(posX,posY, 8, 8) #passing the current x and y value of our sprite

    def update(self, left, right, attack, platforms, entities, enemy):
        if attack:
            self.xvel = 12
        #if attack and left:
        #    self.xvel = -8
        self.rect.left += self.xvel
        self.collide(self.xvel,0,platforms,entities, enemy) # checking for collisions with platforms

    def collide(self, xvel, yvel, platforms, entities, enemy):
         for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if xvel > 0:
                    self.rect.right = p.rect.left
                    attack = False
                    entities.remove(self)#deleting the weapon from entities upon collision
                if xvel < 0:
                    self.rect.left = p.rect.right
                    attack = False
                    entities.remove(self)
            if pygame.sprite.collide_rect(self,enemy):
                entities.remove(enemy)
                entities.remove(self)
                enemy.rect.x = 10000000000 ## clearing the enemy rectangle from screen upon death
                enemy.rect.y = -1000000000

    
class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.image = Surface((32,32))
        self.image.fill(Color("#0000FF"))
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)

    def update(self, up, down, left, right, running, platforms, enemy, alive):
        if up:
            # only jump if on the ground
            if self.onGround: self.yvel -= 10
        if down:
            pass
        if running:
            self.xvel = 12
        if left:
            self.xvel = -8
        if right:
            self.xvel = 8
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += 0.3
            # max falling speed
            if self.yvel > 100: self.yvel = 100
        if not(left or right):
            self.xvel = 0
        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions
        self.collide(self.xvel, 0, platforms, enemy, alive)
        # increment in y direction
        self.rect.top += self.yvel
        # assuming we're in the air
        self.onGround = False
        # do y-axis collisions
        self.collide(0, self.yvel, platforms, enemy, alive)

    def collide(self, xvel, yvel, platforms, enemy, alive):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if isinstance(p, ExitBlock):
                    pygame.event.post(pygame.event.Event(QUIT))
                if xvel > 0:
                    self.rect.right = p.rect.left
                    #print ("collide right")
                if xvel < 0:
                    self.rect.left = p.rect.right
                    #print ("collide left")
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.onGround = True
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom
            if pygame.sprite.collide_rect(self,enemy):
                if enemy:
                    raise SystemExit("YOU DIED...") #Death message
                

class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = Surface((32, 32))
        self.image.convert()
        self.image.fill(Color("#DDDDDD"))
        self.rect = Rect(x, y, 32, 32)

    def update(self):
        pass

class ExitBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image.fill(Color("#0033FF"))

if __name__ == "__main__":
    main()
