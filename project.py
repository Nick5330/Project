
from time import monotonic as timer
from time import sleep

import pygame
from random import randint

increase_width = 1.83
increase_height = 1.44
#окно игры
win_width = 700 * increase_width
win_height = 500 * increase_height
win_display = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("Ukrainian War: Assault")
pygame.display.set_icon(pygame.image.load("image/icon.png"))

x_bg = 0
bg_width = 2000 * increase_width
bg_height = 500 * increase_height

pygame.font.init()
font1 = pygame.font.SysFont("Arial", 30)
font2 = pygame.font.SysFont("Arial", 35)
font3 = pygame.font.SysFont("Arial", 50)
font4 = pygame.font.SysFont("Arial", 25)
font5 = pygame.font.SysFont("Arial", 40)
font6 = pygame.font.SysFont("Arial", 15)

#создание игрового класса
class GameSprite(pygame.sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed, player_width, player_height):
        super().__init__()
        self.player = player_image
        self.width = player_width
        self.height = player_height
        self.image = pygame.transform.scale(pygame.image.load("image/"+self.player), (self.width, self.height)) 
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.speed = player_speed
        

    def reset(self):
        win_display.blit(self.image, (self.rect.x, self.rect.y))

#класс воинов
class Warrior(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed, player_width, 
    player_height, fire_gun, player_health_point, player_armor ,player_gun_clip, player_total_ammo, 
    gun_reload, image_ammo_gun, ammo_width, ammo_height, bullet_distance, speed_bullet ,damage_gun, anim_walk, playerStand):
        super().__init__(player_image, player_x, player_y, player_speed, player_width, player_height)
        self.blink = fire_gun
        self.hp = player_health_point
        self.armor = player_armor
        self.clip = player_gun_clip
        self.ammo = player_total_ammo
        self.reload = gun_reload
        self.image_ammo = image_ammo_gun
        self.ammo_width = ammo_width
        self.ammo_height = ammo_height
        self.b_distance = bullet_distance
        self.damage = damage_gun

        self.b_speed = speed_bullet

        self.run = True
        self.animCount = 10
        self.type = True
        self.stand = playerStand
        self.anim_walk = anim_walk

        self.rpg = False

    def animation(self):
        if not self.rpg:
            if self.animCount + 1 >= 10:
                self.animCount = 0
            if self.run: 
                if self.type:
                    self.image = self.anim_walk[self.animCount//5]
                    self.animCount += 1   
            elif not self.run:
                if self.type:
                    self.image = self.stand
        
#класс игрока
class Player(Warrior):
    #передвижение спрайта
    def update(self, border_player, boost, y1, y2):
        keys_pressed = pygame.key.get_pressed()
        #анимация выхода в начале
        if self.rect.x < 50:
            self.rect.x += self.speed
            self.run = True
        else:
            #передвижение в лево
            if keys_pressed[pygame.K_a]:
                if self.rect.x >= 5:
                    self.rect.x -= self.speed * boost/2
                    self.run = True

            #передвижение в право
            elif keys_pressed[pygame.K_d]:                        
                if self.rect.x <= border_player:              
                    self.rect.x += self.speed * boost/2
                self.run = True              
            #перемещение вверх
            elif keys_pressed[pygame.K_w] and self.rect.y >= y1:
                self.rect.y -= self.speed
                self.run = True
            #перемещение вниз
            elif keys_pressed[pygame.K_s] and self.rect.y <= y2:
                self.rect.y += self.speed
                self.run = True
            
            else:
                self.run = False

        self.animation()
      
    #стрельба
    def shoot(self):
        new_bullet = Bullet(self.image_ammo, self.rect.right-20, self.rect.centery - 45, self.b_speed, self.ammo_width, self.ammo_height, self.b_distance)
        bullets_ua.add(new_bullet)               
        win_display.blit(self.blink, (self.rect.right-30, self.rect.centery - 50))

#класс пули
class Bullet(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed, player_width, player_height, bullet_distance):
        super().__init__(player_image, player_x, player_y, player_speed, player_width, player_height)
        self.b_distance = bullet_distance
        self.step = 0
        self.speed_y = 0
        self.speed_x = self.speed
        self.dest_x = 0
        self.dest_y = 0
    
    #строение траектории полета/нахождения противника(игрока)
    def find_path(self, dest_x, dest_y):
        self.dest_x = dest_x
        self.dest_y = dest_y

        delta_x = dest_x - self.rect.x
        count_up = delta_x // self.speed_x
        
        if self.rect.y >= dest_y:
            delta_y = self.rect.y - dest_y
            self.speed_y = delta_y / count_up
        else:
            delta_y = dest_y - self.rect.y
            self.speed_y = -(delta_y / count_up)

    #перемещение пули
    def move_to(self, reverse = False):
        if not reverse:
            self.rect.x += self.speed_x
            self.rect.y -= self.speed_y
        else:
            self.rect.x -= self.speed_x
            self.rect.y += self.speed_y
        
        self.step += self.speed
       
        if self.step >= self.b_distance:
            return False
        
        if self.rect.x <= win_width and not reverse:
            win_display.blit(self.image, (self.rect.x, self.rect.y))
            return True
        elif self.rect.x >= 0 and reverse:
            win_display.blit(self.image, (self.rect.x, self.rect.y))
            return True
        else:
            return False

#класс врага
class Enemy(Warrior):
    def __init__(self, player_image, player_x, player_y, player_speed, player_width, 
    player_height, fire_gun, player_health_point, player_armor ,player_gun_clip, player_total_ammo, gun_reload, image_ammo_gun, ammo_width, ammo_height, bullet_distance, speed_bullet ,damage_gun, anim_walk, enemyStand, player_exit_point, sound_shoot):
        super().__init__(player_image, player_x, player_y, player_speed, player_width, 
        player_height, fire_gun, player_health_point,player_armor ,player_gun_clip, player_total_ammo, gun_reload, image_ammo_gun, ammo_width, ammo_height, bullet_distance, speed_bullet ,damage_gun, anim_walk, enemyStand)

        self.x_ep = player_exit_point
        self.step = 100
        self.cd_shoot = 0
        self.count_shoot = self.clip

        self.bullets = pygame.sprite.Group()
        self.sound = sound_shoot
        self.sound.set_volume(0.2)
        
    #перемещение врага
    def update(self):
        global boost
        keys_pressed = pygame.key.get_pressed()
        if self.rect.x >= self.x_ep: 
            if keys_pressed[pygame.K_d]:
                self.rect.x -= 1 * boost/2
            if keys_pressed[pygame.K_a]:
                self.rect.x += 1 * boost/2
        else:
            if self.step:
                self.rect.x -= self.speed
                self.step -= 1
                self.run = True
            else:
                self.run = False 
                self.shoot()

            self.animation()
 
    #условие смерти врага
    def dead(self):
        if self.hp <= 0:
            self.kill()
            money = GameSprite("other/money.png", self.rect.centerx, self.rect.bottom-50, 0, 50, 25)
            moneys.append(money)
            for b in self.bullets:
                b.kill()
    #выстрел
    def shoot(self):
        if self.cd_shoot == 0:
            if self.count_shoot != 0:
                
                self.sound.play()
                new_bullet = Bullet(self.image_ammo, self.rect.left, self.rect.top+23, self.b_speed, self.ammo_width, self.ammo_height, self.b_distance)
                new_bullet.find_path(player.rect.x + player.width // 2, player.rect.y + player.height // 2)
                self.bullets.add(new_bullet)
                blink = pygame.transform.flip(self.blink, 1, 0)
                win_display.blit(blink, (self.rect.left-6, self.rect.top+23))
                self.count_shoot -= 1
            elif self.count_shoot == 0:
                self.cd_shoot = self.reload * 30
                self.count_shoot = self.clip
        else:
            self.cd_shoot -= 1
        
        for bullet in self.bullets:
            if not bullet.move_to(reverse=True):
                bullet.kill()
              

class Invader(GameSprite):
    def __init__(self, player_image, player_x, player_y, player_speed, player_width, 
    player_height, anim_walk, playerStand):
        super().__init__(player_image, player_x, player_y, player_speed, player_width, player_height)
        self.run = True
        self.animCount = 10
        self.type = True
        self.stand = playerStand
        self.anim_walk = anim_walk

        self.step = 50

    def animation(self):
        
        if self.animCount + 1 >= 10:
            self.animCount = 0
        if self.run: 
            if self.type:
                self.image = self.anim_walk[self.animCount//5]
                self.animCount += 1   
        elif not self.run:
            if self.type:
                self.image = self.stand

    def update(self):

        if self.rect.x < 350 * increase_width:
            self.rect.x += self.speed
        else:
            if self.step:
                self.rect.x += self.speed
                self.step -= 1
                self.run = True

            if self.step <= 0:
                self.run = False
                
        self.animation()

class Bar():
    def __init__(self, color, x, y, width, height, image, img_w, img_h):
        self.color = color
        self.x = x 
        self.y = y
        self.w = width
        self.h = height
        self.image = image
        self.img_w = img_w
        self.img_h = img_h

    def draw(self):
        win_display.blit(pygame.transform.scale(pygame.image.load('image/other/'+self.image), (self.img_w, self.img_h)), (self.x-self.img_w-10, self.y))
        pygame.draw.rect(win_display, (0,0,0), (self.x-3, self.y-3, self.w+6, self.h+6))
        pygame.draw.rect(win_display, self.color, (self.x, self.y, self.w, self.h))

class Button():
    def __init__(self, text, x, y, w, h, color):
        self.text = text
        self.w = w
        self.h = h
        self.color = color
        
        self.sc = pygame.Surface([self.w, self.h], pygame.SRCALPHA, 32)
        self.sc = self.sc.convert_alpha()
        
        self.rect = self.sc.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.txt_image = font4.render(self.text, True, self.color)

    def draw(self):
        win_display.blit(self.sc, (self.rect.x, self.rect.y))
        win_display.blit(self.txt_image, (self.rect.x, self.rect.y))

#уровни        
def levels_1():
    enemys = pygame.sprite.Group() 
    fon = "image/bg/fon1.png"
    #1 волна
    for i in range(2):
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
        enemys.add(type1_ru)
        
    #2 волна
    for i in range(2):
        x = randint(int(1000 * increase_width), int(1025 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(725 * increase_width), int(745 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
        enemys.add(type1_ru)
    
    return enemys, fon

def levels_2():
    enemys = pygame.sprite.Group() 
    fon = "image/bg/fon2.png"
    #1 волна
    for i in range(2):
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
        enemys.add(type1_ru)
        
    x = randint(int(765 * increase_width), int(785 * increase_width))
    y = randint(int(340 * increase_height), int(400 * increase_height))
    x_ep = randint(int(700 * increase_width), int(750 * increase_width))
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 50, 1, 90, 10, "other/bullet.png", 5, 5, 450 * increase_width, 6, 50, walk_type2_ru, enemyStand_t2, x_ep, shoot_sniper)
    enemys.add(type2_ru)
    
    #2 волна
    for i in range(2):    
        x = randint(int(1000 * increase_width), int(1025 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(725 * increase_width), int(745 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
        enemys.add(type1_ru)
        
    x = randint(int(1000 * increase_width), int(1025 * increase_width))
    y = randint(int(340 * increase_height), int(400 * increase_height))
    x_ep = randint(int(725 * increase_width), int(745 * increase_width))
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 50, 1, 90, 10, "other/bullet.png", 5, 5, 450 * increase_width, 6, 50, walk_type2_ru, enemyStand_t2, x_ep, shoot_sniper)
    enemys.add(type2_ru)
    
    
    return enemys, fon

def levels_3():
    enemys = pygame.sprite.Group()
    fon = "image/bg/fon3.png"
    #1 волна
    for i in range(2):
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 50, 1, 90, 10, "other/bullet.png", 5, 5, 450 * increase_width, 6, 50, walk_type2_ru, enemyStand_t2, x_ep, shoot_sniper)
        enemys.add(type2_ru)
    
    #2 волна
    for i in range(2):
        x = randint(int(1000 * increase_width), int(1025 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(725 * increase_width), int(745 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
        enemys.add(type1_ru)
    

    return enemys, fon

def levels_4():
    enemys = pygame.sprite.Group()
    fon = "image/bg/fon4.png"
    #1 волна
    for i in range(2):
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 50, 1, 90, 10, "other/bullet.png", 5, 5, 450 * increase_width, 6, 50, walk_type2_ru, enemyStand_t2, x_ep, shoot_sniper)
        enemys.add(type2_ru)
    x = randint(int(765 * increase_width), int(785 * increase_width))
    y = randint(int(340 * increase_height), int(400 * increase_height))
    x_ep = randint(int(700 * increase_width), int(750 * increase_width))
    type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
    enemys.add(type1_ru)
    enemys.add(type2_ru)

    #2 волна
    for i in range(2):
        x = randint(int(1000 * increase_width), int(1025 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(725 * increase_width), int(745 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
        enemys.add(type1_ru)
    

    return enemys, fon

def levels_5():
    enemys = pygame.sprite.Group()
    fon = "image/bg/fon5.png"
    #1 волна
    for i in range(2):
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
        enemys.add(type1_ru)
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 50, 1, 90, 10, "other/bullet.png", 5, 5, 450 * increase_width, 6, 50, walk_type2_ru, enemyStand_t2, x_ep, shoot_sniper)
        enemys.add(type2_ru)
        
        
    #2 волна
    for i in range(3):
        x = randint(int(1000 * increase_width), int(1025 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(725 * increase_width), int(745 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
        enemys.add(type1_ru)

    return enemys, fon

def levels_final():
    list_enemy_room = list()
    #корридор
        #1 волна
    enemys_corridor = pygame.sprite.Group()
    for i in range(2):
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
        enemys_corridor.add(type1_ru)
        
    x = randint(int(765 * increase_width), int(785 * increase_width))
    y = randint(int(340 * increase_height), int(400 * increase_height))
    x_ep = randint(int(700 * increase_width), int(750 * increase_width))
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 50, 1, 90, 10, "other/bullet.png", 5, 5, 450 * increase_width, 6, 50, walk_type2_ru, enemyStand_t2, x_ep, shoot_sniper)
    enemys_corridor.add(type2_ru)
    
        #2 волна
    for i in range(2):    
        x = randint(int(1000 * increase_width), int(1025 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(725 * increase_width), int(745 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
        enemys_corridor.add(type1_ru)
        
    x = randint(int(1000 * increase_width), int(1025 * increase_width))
    y = randint(int(340 * increase_height), int(400 * increase_height))
    x_ep = randint(int(725 * increase_width), int(745 * increase_width))
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 50, 1, 90, 10, "other/bullet.png", 5, 5, 450 * increase_width, 6, 50, walk_type2_ru, enemyStand_t2, x_ep, shoot_sniper)
    enemys_corridor.add(type2_ru)

    list_enemy_room.append(enemys_corridor)
    #кабинет
    enemys_cabinet = pygame.sprite.Group()
    for i in range(4):
        x = randint(int(470), int(win_width-350))
        y = randint(int(488), int(600))
        x_ep = 9999
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
        type1_ru.step = 0
        enemys_cabinet.add(type1_ru)
        
    list_enemy_room.append(enemys_cabinet)

    #у входу в бункер
    x_ep = 9999
    enemys_bunker_input = pygame.sprite.Group()
    type1_ru = Enemy("ru/type1_ru.png", 350, 500, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
    type1_ru.step = 0
    enemys_bunker_input.add(type1_ru)
    type1_ru = Enemy("ru/type1_ru.png", 990, 500, 3, 80, 100, fire_gun_type1, 100, 50, 30, 90, 6, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_t1, x_ep, shoot_machine)
    type1_ru.step = 0
    enemys_bunker_input.add(type1_ru)
    list_enemy_room.append(enemys_bunker_input)
    
    #внутри бункера
    x_ep = 9999
    enemys_bunker_inside = pygame.sprite.Group()
    boss = Enemy("ru/boss.png", 1000, 500, 3, 80, 100, fire_gun_type1, 500, 250, 40, 90, 5, "other/bullet.png", 5, 5, 325 * increase_width, 4, 1.5, walk_type1_ru, enemyStand_boss, x_ep, shoot_machine)
    boss.step = 0
    enemys_bunker_inside.add(boss)
    list_enemy_room.append(enemys_bunker_inside)
    
    return list_enemy_room


#начальные заставки
def screensavers(time, level):
    global text1, text2, text3
    if level == 1:
        if int(time) == 0:
            text1 = "Буча"
        elif int(time) == 1:
            text2 = "07.06.2022"
        elif int(time) == 2:
            text3 = "Мейсон"
    elif level == 2:
        if int(time) == 0:
            text1 = "Одеса "
        elif int(time) == 1:
            text2 = "08.06.2022"
        elif int(time) == 2:
            text3 = "Мейсон"
    elif level == 3:
        if int(time) == 0:
            text1 = "Донецьк "
        elif int(time) == 1:
            text2 = "10.06.2022"
        elif int(time) == 2:
            text3 = "Мейсон"
    elif level == 4:
        if int(time) == 0:
            text1 = "Луганськ "
        elif int(time) == 1:
            text2 = "12.06.2022"
        elif int(time) == 2:
            text3 = "Мейсон"
    elif level == 5:
        if int(time) == 0:
            text1 = "Крим "
        elif int(time) == 1:
            text2 = "15.06.2022"
        elif int(time) == 2:
            text3 = "Мейсон"
    elif level > 5:
        if int(time) == 0:
            text1 = "Будинок парламенту"
        elif int(time) == 1:
            text2 = "20.06.2022"
        elif int(time) == 2:
            text3 = "Мейсон"
    

enemys = pygame.sprite.Group()

#инф.панель экземпляр класса
icon_info = GameSprite("other/icon_info.png", win_width-50, 10, 0, 25, 25)
panel_info = GameSprite("other/panel_info.png", 250, 105, 0, 720, 580)
cross = GameSprite("other/cross.png", 880, 225, 0, 25, 25)
circle = GameSprite("other/nothing.png", -500, -500, 0, 100, 100)

#картинка выстрела
fire_gun_type1 = fire_gun_type2 = pygame.transform.scale(pygame.image.load("image/other/fire_gun.png"), (25, 15))
fire_gun_type3 = pygame.transform.scale(pygame.image.load("image/other/fire_rpg.png"), (35, 20))

#размеры спрайтов разных типов
type1_uk_width, type1_uk_height = 120, 140
type2_uk_width, type2_uk_height = 140, 140

type1_ru_width, type1_ru_height = type1_uk_width, type1_uk_height
type2_ru_width, type2_ru_height = type2_uk_width, type2_uk_height

#списки с картинками для анимации
#анимация в правую сторону
walk_type1_uk = [pygame.transform.scale(pygame.image.load("image/ua/animation_type1/anim1.png"), (type1_uk_width, type1_uk_height)), 
pygame.transform.scale(pygame.image.load("image/ua/animation_type1/anim2.png"), (type1_uk_width, type1_uk_height))]
walk_type2_uk = [pygame.transform.scale(pygame.image.load("image/ua/animation_type2/anim1.png"), (type2_uk_width, type2_uk_height)), 
pygame.transform.scale(pygame.image.load("image/ua/animation_type2/anim2.png"), (type2_uk_width, type2_uk_height))]

#анимация в левую сторону
walk_type1_uk_left = list()
for w in walk_type1_uk:
    w = pygame.transform.flip(w, 1, 0)
    walk_type1_uk_left.append(w)

walk_type2_uk_left = list()
for w in walk_type2_uk:
    walk_type2_uk_left.append(w)

walk_r = walk_type1_uk
walk_l = walk_type1_uk_left

walk_ensign = [pygame.transform.scale(pygame.image.load("image/ua/animation_ensign/ensign1.png"), (150, 230)), 
pygame.transform.scale(pygame.image.load("image/ua/animation_ensign/ensign2.png"), (150, 230))]

rightStand_t1 = pygame.transform.scale(pygame.image.load("image/ua/type1_uk.png"), (type1_uk_width, type1_uk_height))
rightStand_t2 = pygame.transform.scale(pygame.image.load("image/ua/type2_uk.png"), (type2_uk_width, type2_uk_height))
vexillaryStand = pygame.transform.scale(pygame.image.load("image/ua/vexillary.png"), (150, 250))

leftStand_t1 = pygame.transform.flip(rightStand_t1, 1, 0)
leftStand_t2 = pygame.transform.flip(rightStand_t2, 1, 0)

stand_r = rightStand_t1
stand_l = leftStand_t1

walk_type1_ru = [pygame.transform.scale(pygame.image.load("image/ru/animation_type1/anim1.png"), (type1_ru_width, type1_ru_height)), 
pygame.transform.scale(pygame.image.load("image/ru/animation_type1/anim2.png"), (type1_ru_width, type1_ru_height))]
walk_type2_ru = [pygame.transform.scale(pygame.image.load("image/ru/animation_type2/anim1.png"), (type2_ru_width, type2_ru_height)), 
pygame.transform.scale(pygame.image.load("image/ru/animation_type2/anim2.png"), (type2_ru_width, type2_ru_height))]

enemyStand_t1 = pygame.transform.scale(pygame.image.load("image/ru/type1_ru.png"), (type1_ru_width, type1_ru_height))
enemyStand_t2 = pygame.transform.scale(pygame.image.load("image/ru/type2_ru.png"), (type2_ru_width, type2_ru_height))
enemyStand_boss = pygame.transform.scale(pygame.image.load("image/ru/boss.png"), (type1_ru_width, type1_ru_height))

type1_uk = Player("ua/type1_uk.png", 50 * increase_width, 385 * increase_height, 3, 80 * increase_width, 100 * increase_height, fire_gun_type1, 100, 50, 30, 90, 3, "other/bullet.png", 5, 5, 325 * increase_width, 4, 20, walk_type1_uk, rightStand_t1)
type2_uk = Player("ua/type2_uk.png", 50 * increase_width, 385 * increase_height, 3, 100 * increase_width, 100 * increase_height, fire_gun_type2, 100, 50, 1, 18, 2, "other/bullet.png", 5, 5, 450 * increase_width, 6,50, walk_type2_uk, rightStand_t2)
type3_uk = Player("ua/type3_uk.png", 50 * increase_width, 385 * increase_height, 0, 80 * increase_height, 100 * increase_height, fire_gun_type3, 100, 50, 1, 3, 6, "other/rocket.png", 25, 15, 435 * increase_width, 8,100, None, None)

#кнопки
button = GameSprite("other/button.png", win_width/2.5+10, win_height-250, 0, 150, 75)
button_r = GameSprite("other/button_r.png", win_width/2.25+25, win_height-250, 0, 150, 75)
button_play = GameSprite("other/button_play.png", win_width/2.25+25, win_height-250, 0, 150, 75)
button_menu = GameSprite("other/button_menu.png", win_width/2.25+25, win_height-150, 0, 150, 75)
button_con = GameSprite("other/button_con.png", win_width/2.5+10, win_height-150, 0, 150, 75)

button_kill = GameSprite("final/skit/kill_bn.png", 80, win_height-175, 0, 370, 125)
button_arest = GameSprite("final/skit/arest_bn.png", 750, win_height-170, 0, 450, 125)

#прилавок с оружием
counter = GameSprite("other/counter.png", win_width-400, win_height-325, 0, 200, 250)
exit = GameSprite("other/exit.png", 10, win_height-300, 0, 60,300)

#для сворачивания панелей
collapse = GameSprite("other/nothing.png", 980, 0, 0, win_width-980, win_height)

#двери на финале
close_door = GameSprite("final/door.png", win_width+450, win_height/2-38, 0, 200, 250)
door_cabinet = GameSprite("other/nothing.png", bg_width-25, 350, 0, 150, 350)
exit_cabinet = GameSprite("other/nothing.png", 25, 350, 0, 30, 350)
door_bunker = GameSprite("other/nothing.png", 400, 280, 0, 150, 250)
armchais1 = GameSprite("other/nothing.png", 50, 460, 0, 170, 200)
armchais2 = GameSprite("other/nothing.png", 1120, 460, 0, 170, 200)
entrance_Putin = GameSprite("other/nothing.png", win_width-100, 350, 0, 150, 350)

#полоса открытия бункера
width_progress = 0
progress = GameSprite("other/progress.png", 230, 100, 0, width_progress, 50)

#кнопки для кодовой панел
bn_code_panel = list()
bn_code_panel.append(GameSprite("final/bn/bn_0.png", 780, 430, 0, 50, 50))
bn_1 = GameSprite("final/bn/bn_1.png", 720, 255, 0, 50, 50)
bn_code_panel.append(bn_1)
bn_code_panel.append(GameSprite("final/bn/bn_2.png", 780, 255, 0, 50, 50))
bn_code_panel.append(GameSprite("final/bn/bn_3.png", 840, 255, 0, 50, 50))
bn_4 = GameSprite("final/bn/bn_4.png", 720, 310, 0, 50, 50)
bn_code_panel.append(bn_4)
bn_code_panel.append(GameSprite("final/bn/bn_5.png", 780, 310, 0, 50, 50))
bn_6 = GameSprite("final/bn/bn_6.png", 840, 310, 0, 50, 50)
bn_code_panel.append(bn_6)
bn_code_panel.append(GameSprite("final/bn/bn_7.png", 720, 370, 0, 50, 50))
bn_code_panel.append(GameSprite("final/bn/bn_8.png", 780, 370, 0, 50, 50))
bn_9 = GameSprite("final/bn/bn_9.png", 840, 370, 0, 50, 50)
bn_code_panel.append(bn_9)

bn_c = GameSprite("final/bn/bn_c.png", 720, 430, 0, 50, 50)
bn_ent = GameSprite("final/bn/bn_ent.png", 840, 430, 0, 50, 50) 

#звезды на панели
list_star = list()
x_star = 430
for i in range(4):
    list_star.append(GameSprite("final/star.png", x_star, 345, 0, 50, 50))
    x_star += 60

star_count = list()

#начальный спрайт-игрокаF
player = type1_uk
max_ammo = player.clip

player_y = player.rect.y

#панель хп и брони
width_hp_bar = player.hp * 2
width_arm_bar = player.armor * 3
healt_bar = Bar((156, 50, 0), 50, 85, width_hp_bar, 25, "icon_hp.png", 35,35)
armor_bar = Bar((75, 52, 172), 50, 120, width_arm_bar, 25, "icon_arm.png", 35, 45)

#подсвеченные вещи
newspaper = GameSprite('other/flash.png', 300, 480, 0, 50, 50)
figurine = GameSprite('other/flash.png', 580, 490, 0, 50, 50)
code = GameSprite('other/flash.png', 980, 530, 0, 50, 50)


#кастцены
#перед выбором
skit = [pygame.transform.scale(pygame.image.load("image/final/skit/skit1.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/skit1.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/skit2.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/skit3.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/skit4.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/skit5.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/skit6.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/skit7.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/skit8.png"), (win_width, win_height))]
#убийства
turn_kill = [pygame.transform.scale(pygame.image.load("image/final/skit/kill/skit1.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/kill/skit2.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/kill/skit3.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/kill/skit4.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/kill/skit5.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/kill/skit6.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/kill/skit7.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/kill/skit8.png"), (win_width, win_height))]
#ареста
turn_arest =[pygame.transform.scale(pygame.image.load("image/final/skit/arest/skit1.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/arest/skit2.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/arest/skit3.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/arest/skit4.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/arest/skit5.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/arest/skit6.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/arest/skit7.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/arest/skit8.png"), (win_width, win_height)),
pygame.transform.scale(pygame.image.load("image/final/skit/arest/skit9.png"), (win_width, win_height))]
 

#начальное положения игрока для анимации выхоа из предел

x_animation = -100

clock = pygame.time.Clock()
FPS = 30

moneys = list()
bullets_ua = pygame.sprite.Group()
bullets_ru = pygame.sprite.Group()

invaders = list()

WHITE = (250,250,250)
GREEN = (0, 180, 0)
RED = (150, 25, 40)

not_ammo = font1.render("Not ammo!!" , True, (215, 64, 94))
point_capture = font3.render("Триває захоплення зони!", True, (135, 200, 50))
e_tap = font3.render("Натисніть 'Е' для взаємодії", True, (250,0,250))
died = font3.render("YOU DIED!", True, (176, 16, 48))
rest = font3.render("PAUSED!", True, WHITE)

buy_type1_txt = "Автомат - 300₴"
buy_type2_txt = "Снайперка - 1500₴"
buy_type3_txt = "РПГ - 3000₴"
buy_armor_txt = "Броня - 500₴"
buy_salo_txt = "Сало - 500₴"

access_panel = font5.render("ACCESS", True, GREEN)
error_panel = font5.render("ERROR", True, RED)

thanks_game = font3.render("Дякую за гру!", True, (124,252,0)) 

buy_type1 = Button(buy_type1_txt, 100, 200, 250, 30, WHITE)
buy_type2 = Button(buy_type2_txt, 100, 250, 250, 30, WHITE)
buy_type3 = Button(buy_type3_txt, 100, 300, 250, 30, WHITE)
buy_armor = Button(buy_armor_txt, 100, 350, 250, 30, WHITE)
buy_salo = Button(buy_salo_txt, 100, 350, 250, 30, WHITE)


pygame.mixer.init()

#menu_music = pygame.mixer.Sound("sound/music_menu.ogg")
#menu_music.set_volume(0.2)
#final_music = pygame.mixer.Sound("sound/final_music.ogg")
#final_music.set_volume(0.2)

march = pygame.mixer.Sound("sound/march.ogg")
march.set_volume(0.5)
boom = pygame.mixer.Sound("sound/boom.ogg")
boom.set_volume(0.7)
recharge = pygame.mixer.Sound("sound/recharge.ogg")
recharge.set_volume(0.5)
shoot_machine = pygame.mixer.Sound("sound/machine_sound.ogg")
shoot_machine.set_volume(0.4)
shoot_sniper = pygame.mixer.Sound("sound/sniper_sound.ogg")
shoot_sniper.set_volume(0.4)
shoot_rpg = pygame.mixer.Sound("sound/shoot_rpg.ogg")
shoot_rpg.set_volume(0.4)

shoot_gun  = shoot_machine





text1 = text2 = text3 = ""



fon_armory = "image/bg/armory.png"

#фоны для финала
corridor = "image/final/corridor.png"
office = "image/final/office.png"
hopper_input = "image/final/bunker_input.png"
hopper_inside = "image/final/bunker_inside.png"
fon = "image/bg/fon_menu.png"
boom_img = pygame.transform.scale(pygame.image.load("image/other/boom.png"), (250, 250))


def turn():
    global game, menu
    start_skit = True
    skit_start = True 
    choise = False
    skit_kill = False
    skit_arest = False
    thx_game = False
    count_skit = 0
   
    while start_skit:
        mouse = pygame.mouse.get_pressed()
        for e in pygame.event.get(): # закриваємо вікно гри
            if e.type == pygame.QUIT: 
                start_skit = False
                game = False

        win_display.fill((0,0,0))
        if skit_start:
            if count_skit + 100 >= 3600:
                count_skit = 0
                skit_start = False
                choise = True
            else:
                bg = skit[count_skit//400]
                win_display.blit(bg, (0,0))
                count_skit += 1
        if choise:
            win_display.blit(pygame.transform.scale(pygame.image.load("image/final/skit/choice.png"), (win_width, win_height)), (0,0))
            button_arest.reset()
            button_kill.reset()
            if mouse[0]:
                x_pos, y_pos = pygame.mouse.get_pos()
                if button_kill.rect.collidepoint(x_pos, y_pos):
                    skit_kill = True
                    choise = False
                if button_arest.rect.collidepoint(x_pos, y_pos):
                    skit_arest = True
                    choise = False

        if skit_kill:
            if count_skit + 1 >= 3200:
                count_skit = 0
                skit_kill = False
                thx_game = True
            else:
                bg = turn_kill[count_skit//400]
                win_display.blit(bg, (0,0))
                count_skit += 1

        if skit_arest:
            if count_skit + 1 >= 3600:
                count_skit = 0
                skit_kill = False
                thx_game = True
            else:
                bg = turn_arest[count_skit//400]
                win_display.blit(bg, (0,0))
                count_skit += 1

        
        if thx_game:
            win_display.fill((0,0,0))
            win_display.blit(thanks_game, (550, 350))
            button_menu.reset()

            if mouse[0]:
                x_pos, y_pos = pygame.mouse.get_pos()
                if button_menu.rect.collidepoint(x_pos, y_pos):
                    menu = True
                    start_skit = False
        
        pygame.display.update()

def pause():
    global finish, menu, game, on_pause, level, final
    on_pause = True
    stop_g = True
    while stop_g:
        mouse = pygame.mouse.get_pressed()

        for e in pygame.event.get(): # закриваємо вікно гри
            if e.type == pygame.QUIT: 
                stop_g = False
                game = False
    
        win_display.fill((0,0,0))
        win_display.blit(rest, (550, 250))
        button_play.reset()
        button_menu.reset()

        if mouse[0]:
            x_pos, y_pos = pygame.mouse.get_pos()
            if button_menu.rect.collidepoint(x_pos, y_pos):
                menu = True
                stop_g = False
            if button_play.rect.collidepoint(x_pos, y_pos):
                if level > 5:
                    final = True
                else:
                    finish = False
                stop_g = False
        
        pygame.display.update()

def reset_everything():
    global cash, x_bg, level, last_cash, amount_armor, amount_medecine, last_ammo_type3
    global last_amount_arm, last_amount_med, last_ammo_type1, last_ammo_type2
    global entrance_zone, border_bg, healing, cd_tap, cd_use_med, cd_use_arm
    global cd_use_arm, count_error, count_access, end_progress, max_lvl
    global finish, info, space, rel_time, screensav, headband, level_change
    global exit_animation, capture, armory, loge, have_type1, have_type2, have_type3
    global pin_access, pin_error, open_door, open_bunker, on_pause, open_code, take_statuette
    global open_newspaper, code_entry, final, hole, cabinet, bunker_input, hp_player, arm_player
    global tap_bn1, tap_bn4, tap_bn6, tap_bn9, bunker_inside, count_boom, blit_boom
    #счетчики
    max_lvl = 5
    level = 1
    entrance_zone = 0 #зона выхода для захватчиков точек
    cash = 0 #деньги
    border_bg = 0 #граница фона
    amount_armor = 2 #кол-во брони
    amount_medecine = 2 #кол-во аптечек
    healing = 70 #лечение на N едениц
    cd_tap = 0 #кд на нажатие кнопки кода и покупки
    cd_use_med = 0 #кд на использования хилки (10)
    cd_use_arm = 0 #кд на использования хилки (10)
    count_boom = 50
    hp_player = player.hp
    arm_player = player.armor

    #последние значение перед началом уровнем
    #используется для рестарта 
    last_cash = cash
    last_ammo_type1 = type1_uk.ammo
    last_ammo_type2 = type2_uk.ammo
    last_ammo_type3 = type3_uk.ammo
    last_amount_arm = amount_armor
    last_amount_med = amount_medecine


    count_access = 50
    count_error = 50

    end_progress = 700


    #флашки
    finish = True #финишь
   
    info = False #инф. панель
    space = True #нажатие на пробел  
    rel_time = False #перезарядка

    screensav = False # 
    headband = False # заставка между уровнями

    level_change = False #настрояка уровня

    exit_animation = False #точка выхода анимации
    capture = False #выход захватчиков точек
    armory = False #оружейная
    loge = False #ларек оружейки
    have_type1 = True #имение автомата
    have_type2 = False #имение снайперки
    have_type3 = True #имение РПГ

    blit_boom = False

    pin_access = False
    pin_error = False

    open_door = False
    open_bunker = False

    on_pause = False

    open_code = False
    take_statuette = False
    open_newspaper = False

    code_entry = False #кодовая панель

    final = False #финальная часть
    hole = False #корридор
    cabinet = False #кабинет
    bunker_input = False #бункер
    bunker_inside = False

    tap_bn1 = False
    tap_bn4 = False
    tap_bn6 = False
    tap_bn9 = False


def reset_parameters():
    global x_bg, player, x_animation, rpgStand, invaders
    global enemys, bullets_ua, player, enemys, cash, last_cash
    global last_ammo_type1, last_ammo_type2, last_ammo_type3
    global type1_uk, type2_uk, type3_uk, last_amount_med, last_amount_arm
    global amount_medecine, amount_armor, walk_r, walk_l, stand_r, rightStand_t1
    #сброс параметров перед новым уровнем
    x_bg = 0
    cash = last_cash
    last_cash = cash
    
    type1_uk.ammo = last_ammo_type1
    type2_uk.ammo = last_ammo_type2
    type3_uk.ammo = last_ammo_type3
    amount_armor = last_amount_arm
    amount_medecine = last_amount_med

    last_ammo_type1 = type1_uk.ammo
    last_ammo_type2 = type2_uk.ammo
    last_ammo_type3 = type3_uk.ammo
    last_amount_arm = amount_armor
    last_amount_med = amount_medecine
    

    player = type1_uk
    walk_r = walk_type1_uk
    walk_l = walk_type1_uk_left
    stand_r = rightStand_t1
    player.anim_walk = walk_r
    player.stand = stand_r
    player.clip = 30
    player.hp = 100
    player.armor = 50
    x_animation = -100
    player.rect.x = x_animation
    player.rect.y = player_y
    rpgStand = False
    
    for enemy in enemys:
        for b in enemy.bullets:
            b.kill()
    for e in enemys:
        e.kill()

    for b in bullets_ua:
        b.kill()
    invaders.clear()
    invaders.append(Invader("ua/type1_uk.png", -260, 500, 3, 75, 100, walk_type1_uk, rightStand_t1))
    invaders.append(Invader("ua/vexillary.png", -200, 430, 3, 150, 230, walk_ensign, vexillaryStand))
    invaders.append(Invader("ua/type2_uk.png", -300, 550, 3, 85, 100, walk_type2_uk, rightStand_t2))
        

def restart():
    global headband, level_change, game
    lose = True
    while lose:
        for e in pygame.event.get(): # закриваємо вікно гри
            if e.type == pygame.QUIT: 
                lose = False
                game = False

        mouse = pygame.mouse.get_pressed()
        win_display.fill((0,0,0))
        button_r.reset()
        win_display.blit(died, (550, 250))
        if mouse[0]:
            x_pos, y_pos = pygame.mouse.get_pos()
            if button_r.rect.collidepoint(x_pos, y_pos):
                
                level_change = True
                lose = False
                
        pygame.display.update()
def screen_display():
    global player, amount_medecine, amount_armor, cash, moneys
    
    #отображение bar
    width_hp_bar = player.hp * 2.5
    width_arm_bar = player.armor * 3
    healt_bar = Bar((156, 50, 0), 50, 85, width_hp_bar, 25, "icon_hp.png", 20, 20)
    armor_bar = Bar((25, 52, 172), 50, 120, width_arm_bar, 25, "icon_arm.png", 20, 30)
    healt_bar.draw()
    armor_bar.draw()

    #отображение кол-во сала и брони
    medecine = font6.render(str(amount_medecine), True, (250,250,250))
    armor = font6.render(str(amount_armor), True, (250,250,250))
    win_display.blit(pygame.transform.scale(pygame.image.load("image/other/armor.png"), (50,50)), (25, 170))
    win_display.blit(armor, (30, 207))
    win_display.blit(pygame.transform.scale(pygame.image.load("image/other/salo.png"), (50,50)), (25, 230))
    win_display.blit(medecine, (30, 267))

    #отображение денег
    coin = font2.render(str(cash)+" UAH", True, (150, 250, 150))
    win_display.blit(coin, (50, 10))

    for money in moneys:
        money.reset()
   

    gun_drum = font2.render(str(player.clip)+"/"+ str(player.ammo), True, (0,0,0))
    win_display.blit(gun_drum, (win_width-140, win_height-40))


def collider():
    global player, enemys, x_bg, width_arm_bar, width_hp_bar, cash, walk_r
    global border_player, border_bg, final, hole, boost, code_entry, walk_l
    global have_type1, have_type2, have_type3, max_ammo, loge, finish, level
    global amount_armor, amount_medecine, healing, cd_use_med, cd_use_arm
    global stand_l, stand_r, moneys, space, rel_time, start_rel, finish_rel
    global shoot_gun, count_boom, blit_boom, hp_player, arm_player

    keys_pressed = pygame.key.get_pressed()

    #бег
    if keys_pressed[pygame.K_LSHIFT]:
        boost = 5
    else:
        boost = 2

    if len(enemys) == 0:
        border_bg = 0
        border_player = win_width-150
    else:
        border_bg = 300

    #условие границы ходьбы для игрока
    if bg_width + x_bg  >= win_width + border_bg:
        border_player = win_width/2.5+10      

    #перемещения заднего фона                    
    if keys_pressed[pygame.K_d] and player.rpg == False:
        player.anim_walk = walk_r
        player.stand = stand_r
        if bg_width + x_bg  >= win_width + border_bg:     
            if not code_entry:
                x_bg -= boost
            if final == True and hole == True:
                close_door.rect.x -= boost
                door_cabinet.rect.x -= boost
            if finish == False or (final == True and hole == True):
                if len(moneys) != 0 and player.rpg == False:
                    for m in moneys:
                        m.rect.x -= boost

    if keys_pressed[pygame.K_a]:
        if len(enemys) == 0 and final:
            player.anim_walk = walk_l
            player.stand = stand_l
        
        if x_bg < 0:
            if len(enemys) == 0:   
                if final == True and hole == True:
                    x_bg += boost
                    close_door.rect.x += boost
                    door_cabinet.rect.x += boost
                    
                    if len(moneys) != 0 and player.rpg == False:
                        for m in moneys:
                            m.rect.x += boost
                    
    if keys_pressed[pygame.K_ESCAPE]:
        if level > 5:
            final = False
        else:
            finish = True
        pause()

    #стрельба
    if space:
        if keys_pressed[pygame.K_SPACE]:
            #проверка наличия патронов в обойме
            if player.clip != 0:    
                #проверка налачия патронов в запасе               
                if player.ammo >= 0:
                    shoot_gun.play()

                    player.shoot()
                    player.clip -= 1
            #если патронов нету в обойме, но есть в запасе - перезарядка
            elif player.clip == 0 and player.ammo != 0:
                rel_time = True
                space = False
                start_rel = timer()
            #если патронов нигде нету - надпись "Нет патронов"
            elif player.clip == 0 and player.ammo == 0:
                win_display.blit(not_ammo, (win_width-150, win_height-60))

    #перезарядка 
    if rel_time:
        finish_rel = timer()
        if finish_rel - start_rel < player.reload:
            recharge.play()
            reload = font1.render("Wait, reload...", True, (125, 0, 0))
            win_display.blit(reload,(win_width-180, win_height-65))
        else:
            recharge.stop()
            rel_time = False
            space = True
            if player.ammo > 0:
                player.clip = max_ammo
                player.ammo -= player.clip
    
    #смена оружий
    if not(rel_time):
        if keys_pressed[pygame.K_1]:
            if have_type1 == True and player.clip != 0 or (player.clip == 0 and player.ammo == 0):
                x = player.rect.x
                y = player.rect.y

                hp_player = player.hp
                arm_player = player.armor
                shoot_gun = shoot_machine
                player = type1_uk
                player.hp = hp_player
                player.armor = arm_player
                if player.ammo != 0:         
                    player.ammo -= 30 - player.clip
                    player.clip += 30 - player.clip

                player.rect.x = x
                player.rect.y = y
                walk_r = walk_type1_uk
                walk_l = walk_type1_uk_left
                stand_r = rightStand_t1
                stand_l = leftStand_t1
                player.stand = stand_r
                player.anim_walk = walk_r

                max_ammo = player.clip

                player.rpg = False
            else:
                pass #возможно текст
        elif keys_pressed[pygame.K_2]:
            if have_type2 == True and player.clip != 0 or (player.clip == 0 and player.ammo == 0):
                shoot_gun = shoot_sniper
                x = player.rect.x
                y = player.rect.y

                hp_player = player.hp
                arm_player = player.armor
                player = type2_uk
                player.hp = hp_player
                player.armor = arm_player
                player.rect.x = x
                player.rect.y = y
                walk_r = walk_type2_uk
                walk_l = walk_type2_uk_left
                stand_r = rightStand_t2
                stand_l = leftStand_t2
                player.stand = stand_r
                player.anim_walk = walk_r

                max_ammo = player.clip

                player.rpg = False
            else:
                pass #возможно текст
        elif keys_pressed[pygame.K_3]:
            if have_type3 == True and player.clip != 0 or (player.clip == 0 and player.ammo == 0):
                shoot_gun = shoot_rpg
                x = player.rect.x
                y = player.rect.y

                hp_player = player.hp
                arm_player = player.armor
                player = type3_uk
                player.hp = hp_player
                player.armor = arm_player
                player.rect.x = x
                player.rect.y = y
                
                max_ammo = player.clip

                player.rpg = True
            else:
                pass #возможно тект
    for bullet in bullets_ua:
        if not bullet.move_to():
            bullet.kill()
    
    #проверка поражения пулей врага
    if player == type3_uk:
        for b in bullets_ua:
            circle.rect.x = b.rect.right
            circle.rect.y = b.rect.centery
        
        if pygame.sprite.groupcollide(enemys, bullets_ua, False, True):
            boom.play()
            blit_boom = True
            for enemy in enemys:
                if pygame.sprite.spritecollide(circle, enemys, False):
                    enemy.hp -= player.damage
                    enemy.dead()

        if final == True:
            if hole == True:
                enemys  = list_enemys[0]
            if cabinet == True:
                enemys  = list_enemys[1]
            if bunker_input == True:
                enemys  = list_enemys[2]
            if bunker_inside == True:
                enemys  = list_enemys[3]
            
            if pygame.sprite.groupcollide(enemys, bullets_ua, False, True):
                for enemy in enemys:
                    if pygame.sprite.spritecollide(circle, enemys, False):
                        enemy.hp -= player.damage
                        enemy.dead()

    else:
        for enemy in enemys:
            if pygame.sprite.spritecollide(enemy, bullets_ua, True):
                if enemy.armor > 0:
                    enemy.armor -= player.damage
                else:
                    if enemy.hp >= 0:
                        enemy.hp -= player.damage
                        enemy.dead()
        
        if final == True:
            if hole == True:
                enemys  = list_enemys[0]
            if cabinet == True:
                enemys  = list_enemys[1]
            if bunker_input == True:
                enemys  = list_enemys[2]
            if bunker_inside == True:
                enemys  = list_enemys[3]
            
            for enemy in enemys:
                if pygame.sprite.spritecollide(enemy, bullets_ua, True):
                    if enemy.armor > 0:
                        enemy.armor -= player.damage
                    else:
                        if enemy.hp >= 0:
                            enemy.hp -= player.damage
                            enemy.dead()
    
    if blit_boom:
        if count_boom != 0:
            win_display.blit(boom_img, (circle.rect.x, circle.rect.y-150))
            count_boom -= 1
        else:
            blit_boom = False

    #проверка поражения пулей игрока
    for enemy in enemys:
        if pygame.sprite.spritecollide(player, enemy.bullets, True):
            if player.armor > 0:
                player.armor -= enemy.damage
            else:
                if player.hp > 0:
                    player.hp -= enemy.damage
                else:
                    restart()
                    finish = True

    #подбор денег   
    for money in moneys:
        if pygame.sprite.collide_rect(player, money):
            moneys.remove(money)
            cash += randint(100, 500)

    #лечение, смена брони
    if cd_use_med == 0:
        if keys_pressed[pygame.K_x]:
            if amount_medecine > 0:
                if player.hp < 100:
                    if player.hp + healing > 100:
                        player.hp += 100 - player.hp           
                    else:
                        player.hp += healing 
                    amount_medecine -= 1
                    cd_use_med = 50
    else:
        cd_use_med -= 1

    if cd_use_arm == 0:            
        if keys_pressed[pygame.K_c]:
            if amount_armor > 0:
                if player.armor < 50:
                    player.armor = 50
                    amount_armor -= 1
                cd_use_arm = 50
    else:
        cd_use_arm -= 1
    
menu = True #игровое меню

reset_everything()
#игровой цикл
game = True
while game:
    #окно-меню
    if menu:
        fon = "image/bg/fon_menu.png"
        background = pygame.transform.scale(pygame.image.load(fon), (win_width, win_height))
        win_display.blit(background, (0,0))
        button.reset()
        if on_pause:
            button_con.reset()
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                x, y = e.pos
                if button.rect.collidepoint(x,y):
                    menu = False
                    reset_everything()
                    level_change = True
                if on_pause:
                    if button_con.rect.collidepoint(x, y):
                        menu = False
                        level_change = True
            if e.type == pygame.QUIT:
                game = False
    #запуск начальной заставки
    if headband:
        start_timer = timer()
        screensav = True
        headband = False
     
    #начальная заставка
    if screensav:
        finish_timer = timer()
        time = finish_timer - start_timer
        text = screensavers(time, level)
        
        if time <= 4:                
            win_display.fill((0,0,0))
            text1_sav = font1.render(text1, True, (250,250,250))
            text2_sav = font1.render(text2, True, (250,250,250))
            text3_sav = font1.render(text3, True, (250,250,250))

            win_display.blit(text1_sav, (win_width/2-25,win_height-420))
            win_display.blit(text2_sav, (win_width/2-50, win_height - 360))
            win_display.blit(text3_sav, (win_width/2-35, win_height - 300))
        elif time > 3.5:
            text1 = text2 = text3 = "" 
            screensav = False
            if level <= 5:
                finish = False
            elif level > 5:
                final = True
                hole = True
    #переход на след. уровень
    if level_change: 
        reset_parameters()
        if level == 1: 
            level_char = levels_1()
            enemys = level_char[0]
            fon = level_char[1]
            height_lim1 = 491 
            height_lim2 = 575

        elif level == 2:
            level_char = levels_2()
            enemys = level_char[0]
            fon = level_char[1]
            height_lim1 = 491 
            height_lim2 = 575

        elif level == 3:
            level_char = levels_3()
            enemys = level_char[0]
            fon = level_char[1]
            height_lim1 = 491 
            height_lim2 = 575

        elif level == 4:
            level_char = levels_4()
            enemys = level_char[0]
            fon = level_char[1]
            height_lim1 = 491 
            height_lim2 = 575

        elif level == 5:
            level_char = levels_5()
            enemys = level_char[0]
            fon = level_char[1]
            height_lim1 = 491 
            height_lim2 = 575
        elif level > 5:
            list_enemys = levels_final()
        
        headband = True
        level_change = False
        

    if armory:
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        background = pygame.transform.scale(pygame.image.load(fon_armory), (win_width, win_height))
        win_display.blit(background, (0,0))
        counter.reset()
        player.reset()
        exit.reset()
        height_lim1 = 491 
        height_lim2 = 575
        
        coin = font2.render(str(cash)+" UAH", True, (150, 250, 150))
        win_display.blit(coin, (50, 10))
        
        border_player = win_width-200
        if not loge:
            player.update(border_player, 5, height_lim1, height_lim2)

        if pygame.sprite.collide_rect(player, counter):
            win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
            if keys[pygame.K_e]:
                loge = True
        if pygame.sprite.collide_rect(player, exit):
            win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
            if keys[pygame.K_e]:
                level_change = True
                armory = False
                last_ammo_type1 = type1_uk.ammo
                last_ammo_type2 = type2_uk.ammo
                last_ammo_type3 = type3_uk.ammo
                last_amount_arm = amount_armor
                last_amount_med = amount_medecine
                last_cash = cash
                
        if keys[pygame.K_d]:
            player.anim_walk = walk_r
            player.stand = stand_r
        if keys[pygame.K_a]:
            player.anim_walk = walk_l
            player.stand = stand_l

        if loge:
            win_display.blit(pygame.image.load("image/other/sheer_black.png"), (0,0))
            win_display.blit(pygame.transform.scale(pygame.image.load("image/other/stall.png"), (640, 360)), (320, 180))
            buy_type1.draw()
            buy_type2.draw()
            buy_type3.draw()
            buy_armor.draw()
            buy_salo.draw()

            x_pos, y_pos = pygame.mouse.get_pos()
            if cd_tap != 0:
                if mouse[0]:
                    if collapse.rect.collidepoint(x_pos, y_pos):
                        loge = False
                    if buy_type1.rect.collidepoint(x_pos, y_pos):
                        if cash >= 300:
                            if have_type1 == True:
                                type1_uk.ammo += 30
                            else:
                                have_type1 = True
                            cash -= 300

                    if buy_type2.rect.collidepoint(x_pos, y_pos):
                        if cash >= 1500:
                            if have_type2 == True:
                                type2_uk.ammo += 10
                            else:
                                have_type2 = True
                            cash -= 1500

                    if buy_type3.rect.collidepoint(x_pos, y_pos):
                        if cash >= 3000:
                            if have_type3 == True:
                                type3_uk.ammo += 3
                            else:
                                have_type3 = True
                            cash -= 3000

                    if buy_armor.rect.collidepoint(x_pos, y_pos):
                        if cash >= 500:
                            amount_armor += 1
                            cash -= 500
                            
                    if buy_salo.rect.collidepoint(x_pos, y_pos):
                        if cash >= 500:
                            amount_medecine += 1
                            cash -= 500
                cd_tap -= 1
            elif cd_tap == 0:
                cd_tap = 5  

            if buy_type1.rect.collidepoint(x_pos, y_pos):
                buy_type1 = Button(buy_type1_txt, 100, 200, 250, 30, GREEN)
            else:
                buy_type1 = Button(buy_type1_txt, 100, 200, 250, 30, WHITE)
            
            if buy_type2.rect.collidepoint(x_pos, y_pos):
                buy_type2 = Button(buy_type2_txt, 100, 250, 250, 30, GREEN)
            else:
                buy_type2 = Button(buy_type2_txt, 100, 250, 250, 30, WHITE)
            
            if buy_type3.rect.collidepoint(x_pos, y_pos):
                buy_type3 = Button(buy_type3_txt, 100, 300, 250, 30, GREEN)
            else:
                buy_type3 = Button(buy_type3_txt, 100, 300, 250, 30, WHITE)
            
            if buy_armor.rect.collidepoint(x_pos, y_pos):
                buy_armor = Button(buy_armor_txt, 100, 350, 250, 30, GREEN)
            else:
                buy_armor = Button(buy_armor_txt, 100, 350, 250, 30, WHITE)
            
            if buy_salo.rect.collidepoint(x_pos, y_pos):
                buy_salo = Button(buy_salo_txt, 100, 400, 250, 30, GREEN)
            else:
                buy_salo = Button(buy_salo_txt, 100, 400, 250, 30, WHITE)
    if not(finish):
        keys_pressed = pygame.key.get_pressed()
        #заливка фона
        background = pygame.transform.scale(pygame.image.load(fon), (bg_width, bg_height))
        win_display.blit(background, (x_bg,0))
        
        collider()  
        

        #создания спрайта-игрока
        player.reset()
        player.update(border_player, boost, height_lim1, height_lim2)


        enemys.draw(win_display)
        enemys.update()
        
        #отображение пуль
        bullets_ua.draw(win_display)
        bullets_ua.update()
        
        #иконка с инфой
        icon_info.reset()

        #выход пихоты с прапорщиком
        if player.rect.x >= 450 * increase_width and entrance_zone == 0:
           exit_animation = True 

        for i in invaders:
            i.reset()

        if exit_animation:
            march.play()
            entrance_zone = 1
            for i in invaders:
                i.update()
            if invaders[0].step <= 0 and invaders[1].step <= 0 and invaders[2].step <= 0:
                capture = True
                exit_animation = False
                start_anim = timer()

        if capture:
            finish_anim = timer()
            difference = int(finish_anim - start_anim)
            win_display.blit(point_capture, (200 * increase_width, 250))
    
            if difference >= 3:
                if len(enemys) == 0: 
                    finish = True
                    entrance_zone = 0
                    capture = False
                    armory = True
                    player = type1_uk
                    player.rect.x, player.rect.y= 50 * increase_width, 385 * increase_height
                    level += 1

                    last_cash = cash
                    last_ammo_type1 = type1_uk.ammo
                    last_ammo_type2 = type2_uk.ammo
                    last_ammo_type3 = type3_uk.ammo
                    last_amount_arm = amount_armor
                    last_amount_med = amount_medecine
        screen_display()

    if final:
        keys_pressed = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        if hole:
            win_display.blit(pygame.transform.scale(pygame.image.load(corridor), (bg_width, bg_height)), (x_bg,0))
            close_door.reset()
            door_cabinet.reset()
            list_enemys[0].draw(win_display)
            list_enemys[0].update()

            
            collider()
            player.reset()
            
            
            height_lim1 = 491 
            height_lim2 = 575
            
            if not code_entry:
                player.update(border_player, boost, height_lim1, height_lim2)
            screen_display()

            if player.rect.y == close_door.rect.centery+41 and player.rect.x >= close_door.rect.left-50 and player.rect.x <= close_door.rect.right-50:
                win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
                if keys_pressed[pygame.K_e]:
                    if open_door == False:
                        code_entry = True
                    else:
                        player.rect.x = 70
                        player.rect.y = 554
                        moneys.clear()
                        bunker_input = True
                        hole = False

            if pygame.sprite.collide_rect(player, door_cabinet):
                win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
                if keys_pressed[pygame.K_e]:
                    hole = False
                    cabinet = True
                    moneys.clear()
                    player.rect.x = 70
                    player.rect.y = 554
                
            if code_entry:
                mouse = pygame.mouse.get_pressed()
                win_display.blit(pygame.image.load("image/other/sheer_black.png"), (0,0))
                win_display.blit(pygame.transform.scale(pygame.image.load("image/final/code_panel.png"), (640, 435)), (320, 150))
                
                for i in range(len(star_count)):
                    list_star[i].reset()
                if mouse[0]:
                    
                    x_pos, y_pos = pygame.mouse.get_pos()
                    if cd_tap == 0:
                        if len(star_count) != 4:
                            for b in bn_code_panel:
                                if b.rect.collidepoint(x_pos, y_pos):
                                    star_count.append(0)

                            if bn_1.rect.collidepoint(x_pos, y_pos): 
                                tap_bn1 = True
                            if bn_4.rect.collidepoint(x_pos, y_pos):
                                tap_bn4 = True
                            if bn_6.rect.collidepoint(x_pos, y_pos):
                                tap_bn6 = True
                            if bn_9.rect.collidepoint(x_pos, y_pos):
                                tap_bn9 = True
                        cd_tap = 5

                    if bn_c.rect.collidepoint(x_pos, y_pos):
                        star_count.clear()
                        tap_bn1 = tap_bn4 = tap_bn6 = tap_bn9 = False

                    if bn_ent.rect.collidepoint(x_pos, y_pos):
                        star_count.clear()
                        if tap_bn1 == True and tap_bn4 == True and tap_bn6 == True and tap_bn9 == True:  
                            open_door = True
                            pin_access = True    
                        else:
                            pin_error = True     
                    
                    if collapse.rect.collidepoint(x_pos, y_pos):
                        code_entry = False
                    
                if pin_access:
                    if count_access != 0:
                        if (count_access % 20 == 0 or count_access % 20 == 1 or count_access % 20 == 2 or 
                            count_access % 20 == 3 or count_access % 20 == 4 or count_access % 20 == 5 or
                            count_access % 20 == 6 or count_access % 20 == 7 or count_access % 20 == 8 or 
                            count_access % 20 == 9):
                            
                            win_display.blit(access_panel, (430, 345))
                    if count_access == 0:
                        pin_access = False
                        code_entry = False
                    count_access -= 1

                if pin_error:
                    if count_error != 0:
                        if (count_error % 20 == 0 or count_error % 20 == 1 or count_error % 20 == 2 or 
                            count_error % 20 == 3 or count_error % 20 == 4 or count_error % 20 == 5 or
                            count_error % 20 == 6 or count_error % 20 == 7 or count_error % 20 == 8 or 
                            count_error % 20 == 9):
                            win_display.blit(error_panel, (430, 345))
                            
                    if count_error <= 0:
                        pin_error = False
                        count_error = 50
                    count_error -= 1

                if cd_tap != 0:
                    cd_tap -= 1
        #кабинет        
        if cabinet:

            win_display.blit(pygame.transform.scale(pygame.image.load(office), (win_width, win_height)), (0,0))
            code.reset()
            exit_cabinet.reset()
            newspaper.reset()
            figurine.reset()
            armchais1.reset()
            armchais2.reset()
            

            height_lim1 = 515 
            height_lim2 = 575
            list_enemys[1].draw(win_display)
            list_enemys[1].update()
            
            
            collider()
            border_player = win_width - 200
            player.reset()
            player.update(border_player, boost, height_lim1, height_lim2)
            screen_display()
            
            if pygame.sprite.collide_rect(exit_cabinet, player):
                win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
                if keys_pressed[pygame.K_e]:
                    moneys.clear()
                    hole = True
                    cabinet = False
                    player.rect.x = 1100
                    player.rect.y = 554
          #контакт с креслами
            if pygame.sprite.collide_rect(armchais1, player):
                if player.rect.bottom <= armchais1.rect.bottom + 20:
                    player.rect.y += 5
            
            if pygame.sprite.collide_rect(armchais2, player):
                if player.rect.bottom <= armchais2.rect.bottom + 20:
                    player.rect.y += 5
          #взаимодействие с подсвеченными предметами
            #газета
            if pygame.sprite.collide_rect(newspaper, player):
                win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
                if keys_pressed[pygame.K_e]:
                    open_newspaper = True
                
            #фигурка
            if pygame.sprite.collide_rect(figurine, player):
                win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
                if keys_pressed[pygame.K_e]:
                    take_statuette = True
                
            #код
            if pygame.sprite.collide_rect(code, player):
                win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
                if keys_pressed[pygame.K_e]:
                    open_code = True
            
            #открытие газеты
            if open_newspaper:
                win_display.blit(pygame.image.load("image/other/sheer_black.png"), (0,0))
                win_display.blit(pygame.transform.scale(pygame.image.load("image/final/newspaper.png"), (920, 650)), (150, 50))
                collapse.reset()
            #взятия татуэтки
            if take_statuette:
                win_display.blit(pygame.image.load("image/other/sheer_black.png"), (0,0))
                win_display.blit(pygame.transform.scale(pygame.image.load("image/final/figurine.png"), (360, 640)), (400, 50))
                collapse.reset()
            #открытие листа с кодом
            if open_code:
                win_display.blit(pygame.image.load("image/other/sheer_black.png"), (0,0))
                win_display.blit(pygame.transform.scale(pygame.image.load("image/final/code.png"), (640, 360)), (320, 180))
                collapse.reset()
            #возможно изменить
            if mouse[0]:
                x_pos, y_pos = pygame.mouse.get_pos()
                if collapse.rect.collidepoint(x_pos, y_pos):
                    open_newspaper = open_code = take_statuette = False
        if bunker_input:
            win_display.blit(pygame.transform.scale(pygame.image.load(hopper_input), (win_width, win_height)), (0,0))
            door_bunker.reset()

            height_lim1 = 470
            height_lim2 = 575
            enemys = list_enemys[2] 
            enemys.draw(win_display)
            enemys.update()
            
            collider()
            border_player = win_width - 200
            player.reset()
            if not keys_pressed[pygame.K_e]:
                player.update(border_player, boost, height_lim1, height_lim2)
            
            if player.rect.y <= 488 and player.rect.x >= door_bunker.rect.left-50 and player.rect.x <= door_bunker.rect.right-50:
                win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
                if len(enemys) == 0:
                    if keys_pressed[pygame.K_e]:
                        if open_bunker == False:
                            progress.reset()
                            if width_progress <= end_progress:
                                width_progress += 3
                                progress = GameSprite("other/progress.png", 290, 100, 0, width_progress, 50)
                            if width_progress >= end_progress:
                                open_bunker = True
                        if open_bunker == True:
                            player.rect.x = 70
                            player.rect.y = 554
                            moneys.clear()
                            
                            bunker_input = False
                            bunker_inside = True
                        
            screen_display()
        
        if bunker_inside:
            win_display.blit(pygame.transform.scale(pygame.image.load(hopper_inside), (win_width, win_height)), (0,0))
            list_enemys[3].draw(win_display)
            list_enemys[3].update()
            
            collider()
            border_player = win_width-200
            height_lim1 = 491 
            height_lim2 = 575
            player.reset()
            player.update(border_player, boost, height_lim1, height_lim2)
            screen_display()

            if pygame.sprite.collide_rect(player, entrance_Putin):
                win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
                if keys_pressed[pygame.K_e]:
                    bunker_inside = False
                    turn()
    

    #информационная панель      
    if info:
        panel_info.reset()
        cross.reset()

       
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            game = False
            
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            x, y = e.pos
            if icon_info.rect.collidepoint(x,y):
                info = True
                finish = True
            if cross.rect.collidepoint(x,y):
                info = False  
                finish = False
            
    clock.tick(FPS)
    pygame.display.update()
