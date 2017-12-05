#! /usr/bin/python
# Matthew Cirkovic
# Wyatt Hurst

import math
from math import sqrt
import pygame
from pygame import *
import time

WIN_WIDTH = 800
WIN_HEIGHT = 640
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

back1 = pygame.image.load("background.jpg")
back2 = pygame.image.load("background2.jpg")
back3 = pygame.image.load("background3.jpg")

level1 = [
                "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
                "PCC                                     CCCP",
                "PCC                                     CCCP",
                "PCC                                     CCCP",
                "PCC                                     CCCP",
                "PCC                                     CCCP",
                "PCC                                     CCCP",
                "PCC                                     CCCP",
                "PCC          CCCCC                      CCCP",
                "PCC          CCCCC                      CCCP",
                "PCC          CCCCC                      CCCP",
                "PCC          CCCCC                      CCCP",
                "PCC          CCCCCCCCCC            CCCCCCCCP",
                "PCCCC        CCCCCCCCCC            CCCCCCCCP",
                "PCC          CCCCC                      CCCP",
                "PCC          CCCCC                      CCCP",
                "PCC          CCCCC                      CCCP",
                "PCC          CCCCC             CCCCCCCCCCCCP",
                "PCC        CCCCCCC             CCCCCCCCCCCCP",
                "PCC          CCCCC                         1",
                "PCC          CCCCC        CCCCCCCCCCCCCCCCCP",
                "PCC          CCCCC       GCCCCCCCCCCCCCCCCCP",
                "PCC          CCCCC      GDCCCCCCCCCCCCCCCCCP",
                "PGGGGGGGGGGGGDDDDDGGGGGGDDCCCCCCCCCCCCCCCCCP",
                "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",]

level2 = [
                "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
                "P                                       CCCP",
                "P                                       CCCP",
                "PCCCCCCCCCCCCCCCCCCCCCC  CCCCCCCCCCCCCCCCCCP",
                "P                                       CCCP",
                "P                                       CCCP",
                "PCCCC  CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCP",
                "P                                       CCCP",
                "P                                       CCCP",
                "PCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC  CCCCCCCCCP",
                "P                                       CCCP",
                "P                                 C     CCCP",
                "P                                CC     CCCP",
                "P                               CCC     CCCP",
                "P                              CCCC     CCCP",
                "P                             CCCCC     CCCP",
                "P         CCCCCCCCCCCCCCCCCCCCCCCCC     CCCP",
                "P                                       CCCP",
                "P                                       CCCP",
                "PCCCCCCCCCCCCCCCCCCCC                   CCCP",
                "P                    CC                 CCCP",
                "P                      CC               CCCP",
                "P                        CC             CCCP",
                "P                          CC              2",
                "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",]

level3 = [
                "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P          E                               P",
                "P                                          P",
                "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          P",
                "P                                          1",
                "PPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP",]

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30
enemies = []

def main():
    pygame.init() #initialize the module
    sreen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pygame.display.set_caption("SAVE THE PRINCESS!")
    timer = pygame.time.Clock()
    alive = True
    scene = Scene1(0, back1, level1) #start first scene

    while alive:
        timer.tick(60)
        if pygame.event.get(QUIT):
            alive = False
            return
        scene.handle_events(pygame.event.get())
        scene.update()
        scene.render(screen)
        pygame.display.flip()

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
        self.xvel = -1
        self.yvel = 0
        self.onGround = False
        self.image = pygame.image.load("ghost.png").convert()
        self.image = pygame.transform.scale(self.image,(32,32))
        transparentColor = self.image.get_at((0, 0))
        self.image.set_colorkey(transparentColor)
        self.image.convert()
        self.rect = Rect(x, y, 32, 32)  

    def update(self, entities, platforms, attack, player):
        if self.yvel < 0: self.onGround = True
        if not self.onGround: 
            self.yvel += 0.3
            if self.yvel > 100: self.yvel = 100
        self.collide(self.xvel,0, platforms, player, entities)
        self.rect.left += self.xvel
        self.rect.top += self.yvel
        self.onGround = False
        self.collide(0,self.yvel,platforms, player, entities)
        if (abs(self.rect.x-player.rect.x) < (WIN_WIDTH/4)):
            self.move_towards_player(player)
        else:
            self.patrol()
            pass

    def collide(self, xvel, yvel, platforms, player, entities):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if xvel < 0:
                    self.rect.left = p.rect.right 
                if xvel > 0:
                    self.rect.right = p.rect.left
                if yvel > 0:
                    self.rect.bottom = p.rect.top
                    self.yvel = 0
                if yvel < 0:
                    self.rect.top = p.rect.bottom

    def move_towards_player(self, player):
        dx, dy = self.rect.x - player.rect.x, self.rect.y - player.rect.y
        dist = sqrt(dx**2 + dy**2)
        try: 
            dx, dy = dx / dist, -(dy / dist)
        except ZeroDivisionError:
            alive = False
        if dx < 0:
            self.rect.x += dx * self.xvel*3
        else:
            self.rect.x += dx * self.xvel

    def patrol(self):
        if  int(pygame.time.get_ticks()/1000%2) == 0:
            self.xvel = 2
        else:
            self.xvel = -2

class Weapon(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = 0
        self.image = Surface((8,8))
        self.image.fill(Color("#FF0000"))
        self.image = pygame.image.load("knife.png").convert()
        transparentColor = self.image.get_at((0, 0))
        self.image.set_colorkey(transparentColor)
        self.image = pygame.transform.scale(self.image, (40,40))
        self.onScreen = True
        self.rect = Rect(posX,posY, 8, 8)

    def update(self, left, right, platforms, entities, enemies, face_left, face_right):
        if self.onScreen and face_right:
            self.xvel = 12
        if self.onScreen and face_left:
            self.xvel = -12
        if self.onScreen and (self.rect.left+posX > HALF_WIDTH):
            self.onScreen = False
        self.rect.left += self.xvel
        for enemy in enemies:
            self.collide(self.xvel,0,platforms,entities, enemy) # checking for collisions with platforms

    def collide(self, xvel, yvel, platforms, entities, enemy):
         for p in platforms:
            if pygame.sprite.collide_rect(self, p):
                if xvel > 0:
                    self.rect.right = p.rect.left
                    self.onScreen = False
                    entities.remove(self)#deleting the weapon from entities upon collision
                if xvel < 0:
                    self.rect.left = p.rect.right
                    self.onScreen = False
                    entities.remove(self)
            if pygame.sprite.collide_rect(self,enemy):
                entities.remove(enemy)
                entities.remove(self)
                enemy.rect.x = -1
                enemy.rect.y = -1
                self.onScreen = False

class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = 0
        self.yvel = 0
        self.onGround = False
        self.image = pygame.image.load("knightRight.png").convert()
        self.image = pygame.transform.scale(self.image, (32, 32))
        transparentColor = self.image.get_at((0, 0))
        self.image.set_colorkey(transparentColor)
        self.rect = Rect(x, y, 32, 32)

    def update(self, up, down, left, right, running, platforms, enemies, alive):
        for enemy in enemies:
            if up:
                # only jump if on the ground
                if self.onGround: self.yvel -= 10
            if down:
                pass
            if running:
                self.xvel = 12
            if left:
                self.xvel = -8
                self.image = pygame.image.load("knight.png").convert()
                transparentColor = self.image.get_at((0, 0))
                self.image.set_colorkey(transparentColor)
                self.image = pygame.transform.scale(self.image, (32,32))
            if right:
                self.xvel = 8
                self.image = pygame.image.load("knightRight.png").convert()
                transparentColor = self.image.get_at((0, 0))
                self.image.set_colorkey(transparentColor)
                self.image = pygame.transform.scale(self.image, (32, 32))
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
            self.collide(self.xvel, 0, platforms, enemies, alive)
            # increment in y direction
            self.rect.top += self.yvel
            # assuming we're in the air    
            self.onGround = False
            # do y-axis collisions
            self.collide(0, self.yvel, platforms, enemies, alive)

    def collide(self, xvel, yvel, platforms, enemies, alive):
        for p in platforms:
            for enemy in enemies:
                if pygame.sprite.collide_rect(self, p):
                    if isinstance(p, ExitBlock1):
                        scene = Scene2(0, back2, level2)
                    if isinstance(p, ExitBlock2):
                        scene = Scene3(0, back3, level3)
                    if isinstance(p, ExitBlock):
                        raise SystemExit("GOODBYE")
                    if xvel > 0:
                        self.rect.right = p.rect.left
                    if xvel < 0:
                        self.rect.left = p.rect.right
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.yvel = 0
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
                if pygame.sprite.collide_rect(self,enemy):
                    if enemy:
                        raise SystemExit("YOU DIED...")
                

class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.transform.scale(pygame.image.load("grass.jpg"),(32,32))
        self.image.fill(Color(255,255,255,128))
        self.rect = Rect(x, y, 32, 32)

class Grass(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = pygame.transform.scale(pygame.image.load("grass.jpg"),(32,32))
        self.rect = Rect(x, y, 32, 32)

    def update(self):
        pass

class Dirt(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = pygame.transform.scale(pygame.image.load("dirt.jpg"),(32,32))
        self.rect = Rect(x, y, 32, 32)

    def update(self):
        pass

class Castle(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = pygame.transform.scale(pygame.image.load("brick.png"),(32,32))
        self.rect = Rect(x, y, 32, 32)

    def update(self):
        pass

class ExitBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image.fill(Color(255, 0, 0))

class ExitBlock1(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)

class ExitBlock2(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)

class Scene(object):
    def __init__(self):
        pass

    def render(self, screen):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def handle_events(self, events):
        raise NotImplementedError

class Scene1(Scene):
    def __init__(self, level, bg, level_set):
        super(Scene1, self).__init__()
        global cameraX, cameraY, alive
        alive = True
        back = bg
        pygame.init()
        screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
        pygame.display.set_caption("SAVE THE PRINCESS")
        timer = pygame.time.Clock()
        up = down = left = right = running = attack = defend = face_left = False
        face_right =True
        entities = pygame.sprite.Group()
        player = Player(100, 600)
        enemy1 = Enemy(1200, 600)
        enemy2 = Enemy(450, 100)
        platforms = []
        x = y = 0
        level = level_set
        enemies.append(enemy1)
        enemies.append(enemy2)
        
        # build the level
        for row in level:
            for col in row:
                if col == "P":
                    p = Platform(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "G":
                    p = Grass(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "D":
                    p = Dirt(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "C":
                    p = Castle(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "1":
                    e = ExitBlock1(x, y)
                    platforms.append(e)
                    entities.add(e)
                x += 32
            y += 32
            x = 0

        total_level_width  = len(level[0])*32
        total_level_height = len(level)*32
        camera = Camera(complex_camera, total_level_width, total_level_height)
        entities.add(player)
        entities.add(enemy1)
        entities.add(enemy2)

        while alive == True:
            timer.tick(60)
            global posX, posY
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
                    try:
                        if weapon.onScreen:
                            pass
                        else:
                            face_left = True
                            face_right = False
                    except UnboundLocalError:
                        face_right = False
                        face_left = True
                if e.type == KEYDOWN and e.key == K_RIGHT:
                    right = True
                    try:
                        if weapon.onScreen:
                            pass
                        else:
                            face_right = True
                            face_left = False
                    except UnboundLocalError:
                        face_right = True
                        face_left = True
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
                    attack = False

            screen.blit(back,(0,0))
            camera.update(player)
            player.update(up, down, left, right, running, platforms, enemies, alive)
            enemy1.update(entities, platforms, attack, player) 
            enemy2.update(entities, platforms, attack, player) 
            try :
                weapon.update(left, right, platforms, entities, enemies, face_left, face_right)
            except UnboundLocalError:
                pass
            for e in entities:
                screen.blit(e.image, camera.apply(e))
            pygame.display.update()
    
class Scene2(Scene):
    def __init__(self, level, bg, level_set):
        super(Scene2, self).__init__()
        global cameraX, cameraY, alive
        alive = True
        back = bg
        pygame.init()
        screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
        pygame.display.set_caption("SAVE THE PRINCESS")
        timer = pygame.time.Clock()
        up = down = left = right = running = attack = defend = face_left = False
        face_right =True
        entities = pygame.sprite.Group()
        player = Player(32, 32)
        enemy1 = Enemy(400, 32)
        enemy2 = Enemy(500, 150)
        enemy3 = Enemy(500,250)
        platforms = []
        x = y = 0
        level = level_set
        enemies.append(enemy1)
        enemies.append(enemy2)
        enemies.append(enemy3)
        
        for row in level:
            for col in row:
                if col == "P":
                    p = Platform(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "G":
                    p = Grass(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "D":
                    p = Dirt(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "C":
                    p = Castle(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "2":
                    e = ExitBlock2(x, y)
                    platforms.append(e)
                    entities.add(e)
                x += 32
            y += 32
            x = 0

        total_level_width  = len(level[0])*32
        total_level_height = len(level)*32
        camera = Camera(complex_camera, total_level_width, total_level_height)
        entities.add(player)
        entities.add(enemy1)
        entities.add(enemy2)
        entities.add(enemy3)


        while alive == True:
            timer.tick(60)
            global posX, posY
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
                    try:
                        if weapon.onScreen:
                            pass
                        else:
                            face_left = True
                            face_right = False
                    except UnboundLocalError:
                        face_right = False
                        face_left = True
                if e.type == KEYDOWN and e.key == K_RIGHT:
                    right = True
                    try:
                        if weapon.onScreen:
                            pass
                        else:
                            face_right = True
                            face_left = False
                    except UnboundLocalError:
                        face_right = True
                        face_left = True
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
                    attack = False

            screen.blit(back,(0,0))
            camera.update(player)
            player.update(up, down, left, right, running, platforms, enemies, alive)
            enemy1.update(entities, platforms, attack, player) 
            enemy2.update(entities, platforms, attack, player)
            enemy3.update(entities, platforms, attack, player)
            try :
                weapon.update(left, right, platforms, entities, enemies, face_left, face_right)
            except UnboundLocalError:
                pass
            for e in entities:
                screen.blit(e.image, camera.apply(e))
            pygame.display.update()

class Scene3(Scene):
    def __init__(self, level, bg, level_set):
        super(Scene3, self).__init__()
        global cameraX, cameraY, alive
        alive = True
        back = bg
        pygame.init()
        screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
        pygame.display.set_caption("SAVE THE PRINCESS")
        timer = pygame.time.Clock()
        up = down = left = right = running = attack = defend = face_left = False
        face_right =True
        entities = pygame.sprite.Group()
        player = Player(32, 32)
        enemy1 = Enemy(-1, 1)
        platforms = []
        x = y = 0
        level = level_set
        enemies.append(enemy1)
        
        for row in level:
            for col in row:
                if col == "P":
                    p = Platform(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "G":
                    p = Grass(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "D":
                    p = Dirt(x, y)
                    platforms.append(p)
                    entities.add(p)
                if col == "C":
                    p = Castle(x, y)
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
        entities.add(enemy1)

        while alive == True:
            timer.tick(60)
            global posX, posY
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
                    try:
                        if weapon.onScreen:
                            pass
                        else:
                            face_left = True
                            face_right = False
                    except UnboundLocalError:
                        face_right = False
                        face_left = True
                if e.type == KEYDOWN and e.key == K_RIGHT:
                    right = True
                    try:
                        if weapon.onScreen:
                            pass
                        else:
                            face_right = True
                            face_left = False
                    except UnboundLocalError:
                        face_right = True
                        face_left = True
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
                    attack = False
            
            screen.blit(back,(0,0))
            camera.update(player)
            player.update(up, down, left, right, running, platforms, enemies, alive)
            enemy1.update(entities, platforms, attack, player) 
            try :
                weapon.update(left, right, platforms, entities, enemies, face_left, face_right)
            except UnboundLocalError:
                pass
            for e in entities:
                screen.blit(e.image, camera.apply(e))
            pygame.display.update()

if __name__ == "__main__":
    main()
