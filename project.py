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
pygame.display.set_caption("project")

x_bg = 0
bg_width = 2000 * increase_width
bg_height = 500 * increase_height

pygame.font.init()
font1 = pygame.font.SysFont("Arial", 30)
font2 = pygame.font.SysFont("Arial", 35)
font3 = pygame.font.SysFont("Arial", 50)

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
    player_height, fire_gun, player_health_point, player_gun_clip, player_total_ammo, 
    gun_reload, image_ammo_gun, ammo_width, ammo_height, bullet_distance, damage_gun, anim_walk, playerStand):
        super().__init__(player_image, player_x, player_y, player_speed, player_width, player_height)
        self.blink = fire_gun
        self.hp = player_health_point
        self.clip = player_gun_clip
        self.ammo = player_total_ammo
        self.reload = gun_reload
        self.image_ammo = image_ammo_gun
        self.ammo_width = ammo_width
        self.ammo_height = ammo_height
        self.b_distance = bullet_distance
        self.damage = damage_gun

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
    def update(self):
        keys_pressed = pygame.key.get_pressed()
        global x_bg
        global border_bg
        #анимация выхода в начале
        if self.rect.x < 50:
            self.rect.x += self.speed
            self.run = True
        else:
            #передвижение в лево
            if keys_pressed[pygame.K_a]:
                if self.rect.x >= 5:
                    self.rect.x -= self.speed
                    self.run = True

            #передвижение в право
            elif keys_pressed[pygame.K_d]:
                if len(moneys) != 0 and self.rpg == False:
                    for m in moneys:
                        m.rect.x -= 2  
                #условие границы ходьбы для игрока
                if len(enemys) != 0:
                    border_bg = 300
                    border_player = win_width/2.5+10
                if len(enemys) == 0:
                    border_bg = 0
                    border_player = win_width-200           
                #перемещения заднего фона                    
                if self.speed:
                    if bg_width + x_bg  >= win_width + border_bg:     
                        x_bg -= 2
                        self.run = True
                        
                    if self.rect.x <= border_player:              
                        self.rect.x += self.speed
                                      
            #перемещение вверх
            elif keys_pressed[pygame.K_w] and self.rect.y >= int(340 * increase_height):
                self.rect.y -= self.speed
                self.run = True
            #перемещение вниз
            elif keys_pressed[pygame.K_s] and self.rect.y <= int(400 * increase_height):
                self.rect.y += self.speed
                self.run = True
            
            else:
                self.run = False

        self.animation()
      
    #стрельба
    def shoot(self):
        new_bullet = Bullet(self.image_ammo, self.rect.right-20, self.rect.centery - 45, 3, self.ammo_width, self.ammo_height, self.b_distance)
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
    player_height, fire_gun, player_health_point, player_gun_clip, player_total_ammo, gun_reload, image_ammo_gun, ammo_width, ammo_height, bullet_distance, damage_gun, anim_walk, enemyStand, player_exit_point):
        super().__init__(player_image, player_x, player_y, player_speed, player_width, 
        player_height, fire_gun, player_health_point, player_gun_clip, player_total_ammo, gun_reload, image_ammo_gun, ammo_width, ammo_height, bullet_distance, damage_gun, anim_walk, enemyStand)

        self.x_ep = player_exit_point
        self.step = 100
        self.cd_shoot = 0
        
    #перемещение врага
    def update(self):
        keys_pressed = pygame.key.get_pressed()
        if self.rect.x >= self.x_ep: 
            if keys_pressed[pygame.K_d]:
                self.rect.x -= 1
            if keys_pressed[pygame.K_a]:
                self.rect.x += 1
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
            money = GameSprite("money.png", self.rect.centerx, self.rect.bottom-50, 0, 50, 25)
            moneys.add(money)
    #выстрел
    def shoot(self):
        if not self.cd_shoot:
            new_bullet = Bullet(self.image_ammo, self.rect.left, self.rect.top+23, 3, self.ammo_width, self.ammo_height, self.b_distance)
            new_bullet.find_path(player.rect.x + player.width // 2, player.rect.y + player.height // 2)
            bullets_ru.add(new_bullet)
            blink = pygame.transform.flip(self.blink, 1, 0)
            win_display.blit(blink, (self.rect.left-6, self.rect.top+23))
            self.cd_shoot = 100
        else:
            self.cd_shoot -= 1
        
        for bullet in bullets_ru:
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
#уровни        
def levels_1():
    enemys = pygame.sprite.Group() 
    fon = "image/fon1.png"
    #1 волна
    for i in range(2):
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325 * increase_width, 20, walk_type1_ru, enemyStand_t1, x_ep)
        enemys.add(type1_ru)
        
    #2 волна
    x = randint(int(1000 * increase_width), int(1025 * increase_width))
    y = randint(int(340 * increase_height), int(400 * increase_height))
    x_ep = randint(int(725 * increase_width), int(745 * increase_width))
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 30, 90, 3, "bullet.png", 5, 5, 450 * increase_width, 40, walk_type2_ru, enemyStand_t2, x_ep)
    enemys.add(type2_ru)
    
    return enemys, fon

def levels_2():
    enemys = pygame.sprite.Group() 
    fon = "image/fon2.png"
    #1 волна
    for i in range(2):
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325 * increase_width, 20, walk_type1_ru, enemyStand_t1, x_ep)
        enemys.add(type1_ru)
        
    #2 волна
    x = randint(int(1000 * increase_width), int(1025 * increase_width))
    y = randint(int(340 * increase_height), int(400 * increase_height))
    x_ep = randint(int(725 * increase_width), int(745 * increase_width))
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 30, 90, 3, "bullet.png", 5, 5, 450 * increase_width, 40, walk_type2_ru, enemyStand_t2, x_ep)
    enemys.add(type2_ru)
    
    return enemys, fon

def levels_3():
    enemys = pygame.sprite.Group()
    fon = "image/fon3.png"
    #1 волна
    for i in range(2):
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325 * increase_width, 20, walk_type1_ru, enemyStand_t1, x_ep)
        enemys.add(type1_ru)
        
    #2 волна
    x = randint(int(1000 * increase_width), int(1025 * increase_width))
    y = randint(int(340 * increase_height), int(400 * increase_height))
    x_ep = randint(int(725 * increase_width), int(745 * increase_width))
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 30, 90, 3, "bullet.png", 5, 5, 450 * increase_width, 40, walk_type2_ru, enemyStand_t2, x_ep)
    enemys.add(type2_ru)

    return enemys, fon

def levels_4():
    enemys = pygame.sprite.Group()
    fon = "image/fon4.png"
   #1 волна
    for i in range(2):
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325 * increase_width, 20, walk_type1_ru, enemyStand_t1, x_ep)
        enemys.add(type1_ru)
        
    #2 волна
    x = randint(int(1000 * increase_width), int(1025 * increase_width))
    y = randint(int(340 * increase_height), int(400 * increase_height))
    x_ep = randint(int(725 * increase_width), int(745 * increase_width))
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 30, 90, 3, "bullet.png", 5, 5, 450 * increase_width, 40, walk_type2_ru, enemyStand_t2, x_ep)
    enemys.add(type2_ru)

    return enemys, fon

def levels_5():
    enemys = pygame.sprite.Group()
    fon = "image/fon5.png"
   #1 волна
    for i in range(2):
        x = randint(int(765 * increase_width), int(785 * increase_width))
        y = randint(int(340 * increase_height), int(400 * increase_height))
        x_ep = randint(int(700 * increase_width), int(750 * increase_width))
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325 * increase_width, 20, walk_type1_ru, enemyStand_t1, x_ep)
        enemys.add(type1_ru)
        
    #2 волна
    x = randint(int(1000 * increase_width), int(1025 * increase_width))
    y = randint(int(340 * increase_height), int(400 * increase_height))
    x_ep = randint(int(725 * increase_width), int(745 * increase_width))
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 30, 90, 3, "bullet.png", 5, 5, 450 * increase_width, 40, walk_type2_ru, enemyStand_t2, x_ep)
    enemys.add(type2_ru)

    return enemys, fon

#начальные заставки
def screensavers(time, level):
    global text1, text2, text3
    if level == 1:
        if int(time) == 0:
            text1 = "Бучи"
        elif int(time) == 1:
            text2 = "07.06.2022"
        elif int(time) == 2:
            text3 = "Мейсон"
    elif level == 2:
        if int(time) == 0:
            text1 = "Одесcа"
        elif int(time) == 1:
            text2 = "08.06.2022"
        elif int(time) == 2:
            text3 = "Мейсон"
    elif level == 3:
        if int(time) == 0:
            text1 = "Донецк"
        elif int(time) == 1:
            text2 = "10.06.2022"
        elif int(time) == 2:
            text3 = "Мейсон"
    elif level == 4:
        if int(time) == 0:
            text1 = "Луганск"
        elif int(time) == 1:
            text2 = "12.06.2022"
        elif int(time) == 2:
            text3 = "Мейсон"
    elif level == 5:
        if int(time) == 0:
            text1 = "Крым"
        elif int(time) == 1:
            text2 = "15.06.2022"
        elif int(time) == 2:
            text3 = "Мейсон"
    

enemys = pygame.sprite.Group()

#инф.панель экземпляр класса
icon_info = GameSprite("icon_info.png", win_width-50, 10, 0, 25, 25)
panel_info = GameSprite("panel_info.png", 125, 50, 0, 450 * increase_width, 350)
cross = GameSprite("cross.png", 515, 125, 0, 25, 25)
circle = GameSprite("nothing.png", -500, -500, 0, 100, 100)

#картинка выстрела
fire_gun_type1 = fire_gun_type2 = pygame.transform.scale(pygame.image.load("image/fire_gun.png"), (25, 15))
fire_gun_type3 = pygame.transform.scale(pygame.image.load("image/fire_rpg.png"), (35, 20))

#размеры спрайтов разных типов
type1_uk_width, type1_uk_height = 120, 140
type2_uk_width, type2_uk_height = 140, 140

type1_ru_width, type1_ru_height = type1_uk_width, type1_uk_height
type2_ru_width, type2_ru_height = type2_uk_width, type2_uk_height

#списки с картинками для анимации
walk_type1_uk = [pygame.transform.scale(pygame.image.load("image/ua/animation_type1/anim1.png"), (type1_uk_width, type1_uk_height)), 
pygame.transform.scale(pygame.image.load("image/ua/animation_type1/anim2.png"), (type1_uk_width, type1_uk_height))]
walk_type2_uk = [pygame.transform.scale(pygame.image.load("image/ua/animation_type2/anim1.png"), (type2_uk_width, type2_uk_height)), 
pygame.transform.scale(pygame.image.load("image/ua/animation_type2/anim2.png"), (type2_uk_width, type2_uk_height))]

walk_ensign = [pygame.transform.scale(pygame.image.load("image/ua/animation_ensign/ensign1.png"), (115, 150)), 
pygame.transform.scale(pygame.image.load("image/ua/animation_ensign/ensign2.png"), (115, 150))]

playerStand_t1 = pygame.transform.scale(pygame.image.load("image/ua/type1_uk.png"), (type1_uk_width, type1_uk_height))
playerStand_t2 = pygame.transform.scale(pygame.image.load("image/ua/type2_uk.png"), (type2_uk_width, type2_uk_height))
vexillaryStand = pygame.transform.scale(pygame.image.load("image/ua/vexillary.png"), (115, 150))

walk_type1_ru = [pygame.transform.scale(pygame.image.load("image/ru/animation_type1/anim1.png"), (type1_ru_width, type1_ru_height)), 
pygame.transform.scale(pygame.image.load("image/ru/animation_type1/anim2.png"), (type1_ru_width, type1_ru_height))]
walk_type2_ru = [pygame.transform.scale(pygame.image.load("image/ru/animation_type2/anim1.png"), (type2_ru_width, type2_ru_height)), 
pygame.transform.scale(pygame.image.load("image/ru/animation_type2/anim2.png"), (type2_ru_width, type2_ru_height))]

enemyStand_t1 = pygame.transform.scale(pygame.image.load("image/ru/type1_ru.png"), (type1_ru_width, type1_ru_height))
enemyStand_t2 = pygame.transform.scale(pygame.image.load("image/ru/type2_ru.png"), (type2_ru_width, type2_ru_height))

type1_uk = Player("ua/type1_uk.png", 50 * increase_width, 385 * increase_height, 3, 80 * increase_width, 100 * increase_height, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325 * increase_width, 30, walk_type1_uk, playerStand_t1)
type2_uk = Player("ua/type2_uk.png", 50 * increase_width, 385 * increase_height, 3, 100 * increase_width, 100 * increase_height, fire_gun_type2, 100, 1, 18, 2, "bullet.png", 5, 5, 450 * increase_width, 50, walk_type2_uk, playerStand_t2)
type3_uk = Player("ua/type3_uk.png", 50 * increase_width, 385 * increase_height, 0, 80 * increase_height, 100 * increase_height, fire_gun_type3, 100, 1, 3, 6, "rocket.png", 25, 15, 435 * increase_width, 100, None, None)

#кнопка старта
button = GameSprite("button.png", win_width/2.5+10, win_height-250, 0, 150, 75)

#прилавок с оружием
counter = GameSprite("counter.png", win_width-250, win_height-200, 0, 100, 150)
exit = GameSprite("exit.png", 10, win_height-300, 0, 60,300)

#начальный спрайт-игрока
player = type1_uk
max_ammo = player.clip

player_y = player.rect.y
#начальное положения игрока для анимации выхоа из предел
x_animation = -100



clock = pygame.time.Clock()
FPS = 30

moneys = pygame.sprite.Group()
bullets_ua = pygame.sprite.Group()
bullets_ru = pygame.sprite.Group()

invaders = list()

not_ammo = font1.render("Not ammo!!" , True, (215, 64, 94))
point_capture = font3.render("Zone capture in progress!", True, (135, 200, 50))
e_tap = font3.render("Нажмите 'Е' для взаимодействия", True, (250,0,250))

text1 = text2 = text3 = ""

max_lvl = 5
level = 0
entrance_zone = 0
cash = 0
border_bg = 0


finish = True
menu = True
info = False
space = True
rel_time = False

screensav = False
headband = False
level_change = False 

exit_animation = False
capture = False
armory = False

fon_armory = "image/armory.png"
fon = "image/menu_fon.png"

#игровой цикл
game = True
while game:
    #окно-меню
    if menu:
        background = pygame.transform.scale(pygame.image.load(fon), (win_width, win_height))
        win_display.blit(background, (0,0))
        button.reset()
        for e in pygame.event.get():
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                x, y = e.pos
                if button.rect.collidepoint(x,y):
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
            finish = False
    #переход на след. уровень
    if level_change: 
        
        level += 1
        if level == 1:
            level_char = levels_1()
            enemys = level_char[0]
            fon = level_char[1]

        elif level == 2:
            level_char = levels_2()
            enemys = level_char[0]
            fon = level_char[1]

        elif level == 3:
            level_char = levels_3()
            enemys = level_char[0]
            fon = level_char[1]

        elif level == 4:
            level_char = levels_4()
            enemys = level_char[0]
            fon = level_char[1]

        elif level == 5:
            level_char = levels_5()
            enemys = level_char[0]
            fon = level_char[1]
        #сброс параметров перед новым уровнем
        headband = True
        x_bg = 0
        player = type1_uk
        player.clip = 30

        x_animation = -100
        player.rect.x = x_animation
        player.rect.y = player_y
        rpgStand = False
        
        for b in bullets_ru:
            b.kill
        for b in bullets_ua:
            b.kill()
        for i in invaders:
            i.kill()
        invaders.append(Invader("ua/type1_uk.png", -230, 370 * increase_height, 3, 75, 100, walk_type1_uk, playerStand_t1))
        invaders.append(Invader("ua/vexillary.png", -200, 390 * increase_height, 3, 115, 150, walk_ensign, vexillaryStand))
        invaders.append(Invader("ua/type2_uk.png", -260, 430 * increase_height, 3, 85, 100, walk_type2_uk, playerStand_t2))

        level_change = False

    if armory:
        keys = pygame.key.get_pressed()
        background = pygame.transform.scale(pygame.image.load(fon_armory), (win_width, win_height))
        win_display.blit(background, (0,0))
        counter.reset()
        player.reset()
        exit.reset()
        
        if not keys[pygame.K_e]:
            player.update()

        if pygame.sprite.collide_rect(player, counter):
            win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
            if keys[pygame.K_e]:
                pass
        
        if pygame.sprite.collide_rect(player, exit):
            win_display.blit(e_tap, (win_width/4-50, win_height/2.5-100))
            if keys[pygame.K_e]:
                level_change = True
                armory = False



    if not(finish):
       
        #заливка фона
        background = pygame.transform.scale(pygame.image.load(fon), (bg_width, bg_height))
        win_display.blit(background, (x_bg,0))
        
        keys_pressed = pygame.key.get_pressed()
 
        #создания спрайта-игрока
        player.reset()
        player.update()

        enemys.draw(win_display)
        enemys.update()
        
        #отображение пуль
        bullets_ua.draw(win_display)
        bullets_ua.update()
        
        moneys.draw(win_display)
        moneys.update()
        #иконка с инфой
        icon_info.reset()
        
        #смена оружий
        if not(rel_time):
            if keys_pressed[pygame.K_1]:
                x = player.rect.x
                y = player.rect.y

                player = type1_uk
                player.rect.x = x
                player.rect.y = y

                max_ammo = player.clip

                player.rpg = False

            elif keys_pressed[pygame.K_2]:
                x = player.rect.x
                y = player.rect.y

                player = type2_uk
                player.rect.x = x
                player.rect.y = y

                max_ammo = player.clip

                player.rpg = False
                
            if keys_pressed[pygame.K_3]:
                x = player.rect.x
                y = player.rect.y

                player = type3_uk
                player.rect.x = x
                player.rect.y = y
                
                max_ammo = player.clip

                player.rpg = True

        coin = font2.render(str(cash)+" UAH", True, (150, 250, 150))
        win_display.blit(coin, (50, 10))

        #стрельба
        if space:
            if keys_pressed[pygame.K_SPACE]:
                #проверка наличия патронов в обойме
                if player.clip != 0:    
                    #проверка налачия патронов в запасе               
                    if player.ammo >= 0:
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
                reload = font1.render("Wait, reload...", True, (125, 0, 0))
                win_display.blit(reload,(win_width-150, win_height-60))
            else:
                rel_time = False
                space = True
                if player.ammo > 0:
                    player.clip = max_ammo
                    player.ammo -= player.clip
        
        for bullet in bullets_ua:
            if not bullet.move_to():
                bullet.kill()
        
        #проверка поражения пулей врага
        if player == type3_uk:
            for b in bullets_ua:
                circle.rect.x = b.rect.right
                circle.rect.y = b.rect.centery
            if pygame.sprite.groupcollide(enemys, bullets_ua, False, True):
                for enemy in enemys:
                    if pygame.sprite.spritecollide(circle, enemys, False):
                        enemy.hp -= player.damage
                        enemy.dead()
        else:
            for enemy in enemys:
                if pygame.sprite.spritecollide(enemy, bullets_ua, True):
                    enemy.hp -= player.damage
                    enemy.dead()
                
        gun_drum = font2.render(str(player.clip)+"/"+ str(player.ammo), True, (0,0,0))
        win_display.blit(gun_drum, (win_width-140, win_height-40))


        #выход пихоты с прапорщиком
        if player.rect.x >= 450 * increase_width and entrance_zone == 0:
           exit_animation = True 

        for i in invaders:
            i.reset()

        if exit_animation:
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
                    player.rect.x, player.rect.y= 50 * increase_width, 385 * increase_height

        if pygame.sprite.spritecollide(player, moneys, True):
            cash += randint(100, 500)

    #информационная панель     
    if info:
        panel_info.reset()
        cross.reset()

    if level > max_lvl:
        finish = True
        rel_time = False               
        player.kill()
        for bullet in bullets_ua:
            bullet.kill()
        
        for bullet in bullets_ru:
            bullet.kill()
       
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
