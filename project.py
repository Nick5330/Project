from time import monotonic as timer
from time import sleep
import pygame
from random import randint

import screensavers

#окно игры
win_width = 700
win_height = 500
win_display = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("project")

x_bg = 0
bg_width = 2000
bg_height = 500

pygame.font.init()
font1 = pygame.font.SysFont("Arial", 20)
font2 = pygame.font.SysFont("Arial", 25)

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
    player_height, fire_gun, player_health_point, player_gun_clip, player_total_ammo, gun_reload, image_ammo_gun, ammo_width, ammo_height, bullet_distance, damage_gun, anim_walk, playerStand):
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
        

#класс игрока
class Player(Warrior):
    #передвижение спрайта
    def update(self):
        keys_pressed = pygame.key.get_pressed()
        global x_bg
        if self.rect.x < 50:
            self.rect.x += self.speed
            self.run = True
        else:
            if keys_pressed[pygame.K_a]:
                if self.rect.x > 5:
                    self.rect.x -= self.speed
                if self.speed:
                    self.run = True
                    if x_bg + bg_width < 2000:
                        x_bg += 2
                    
            elif keys_pressed[pygame.K_d]:
                if self.rect.x < win_width/2.5+10:
                    self.rect.x += self.speed
                if self.speed:
                    self.run = True
                    if bg_width + x_bg  > win_width :
                        x_bg -= 2
            elif keys_pressed[pygame.K_w] and self.rect.y >= 285:
                self.rect.y -= self.speed
                self.run = True
            elif keys_pressed[pygame.K_s] and self.rect.y <= 385:
                self.rect.y += self.speed
                self.run = True
            else:
                self.run = False
        self.animation()

        
    #стрельба
    def shoot(self):
        new_bullet = Bullet(self.image_ammo, self.rect.right, self.rect.top+16, 3, self.ammo_width, self.ammo_height, self.b_distance)
        bullets_ua.add(new_bullet)               
        win_display.blit(self.blink, (self.rect.right-3, self.rect.top+12))

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
        self.step = 50
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
            
    
               

    
    def dead(self):
        if self.hp <= 0:
            self.kill()

    def shoot(self):
        if not self.cd_shoot:
            new_bullet = Bullet(self.image_ammo, self.rect.left, self.rect.top+16, 3, self.ammo_width, self.ammo_height, self.b_distance)
            new_bullet.find_path(player.rect.x + player.width // 2, player.rect.y + player.height // 2)
            bullets_ru.add(new_bullet)
            self.blink = pygame.transform.flip(self.blink, 1, 0)
            win_display.blit(self.blink, (self.rect.left-6, self.rect.top+16))
            self.cd_shoot = 200
        else:
            self.cd_shoot -= 1
        
        for bullet in bullets_ru:
            if not bullet.move_to(reverse=True):
                bullet.kill()
              

        
def levels_1():
    enemys = pygame.sprite.Group() 
    fon = "image/fon1.png"
    #1 волна
    for i in range(2):
        x = randint(765, 785)
        y = randint(285, 385)
        x_ep = randint(700, 750)
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325, 20, walk_type1_ru, enemyStand_t1, x_ep)
        enemys.add(type1_ru)
        
    #2 волна
    x = randint(1000, 1025)
    y = randint(285, 385)
    x_ep = randint(725, 745)
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 30, 90, 3, "bullet.png", 5, 5, 450, 40, walk_type2_ru, enemyStand_t2, x_ep)
    enemys.add(type2_ru)
    
    return enemys, fon

def levels_2():
    enemys = pygame.sprite.Group()
    fon = "image/fon2.jpg"
    #1 волна
    #пулеметчики
    for i in range(2):
        x = randint(765, 785)
        y = randint(285, 385)
        x_ep = randint(700, 750)
        
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325, 20, walk_type1_ru, enemyStand_t1, x_ep)
        enemys.add(type1_ru)
    #снайпер
    x = randint(765, 785)
    y = randint(285, 385)
    x_ep = randint(700, 750)
    
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 30, 90, 3, "bullet.png", 5, 5, 450, 40, walk_type2_ru, enemyStand_t2, x_ep)
    enemys.add(type2_ru)

    #2 этап
    #2 снайпера
    for i in range(2):
        x = randint(1000, 1025)
        y = randint(285, 385)
        x_ep = randint(725, 745)

        type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 80, 100, fire_gun_type2, 100, 30, 90, 3, "bullet.png", 5, 5, 450, 20,walk_type2_ru, enemyStand_t2, x_ep)
        enemys.add(type2_ru)

    #пулеметчик   
    x = randint(1000, 1025)
    y = randint(285, 385)
    x_ep = randint(725, 745)
    
    type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 100, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325, 40, walk_type1_ru, enemyStand_t1, x_ep)
    enemys.add(type1_ru)

    return enemys, fon

def levels_3():
    enemys = pygame.sprite.Group()
    fon = "image/fon3.jpg"
    #
    for i in range(2):
        x = randint(765, 785)
        y = randint(285, 385)
        x_ep = randint(700, 750)
        
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325, 20, walk_type1_ru, enemyStand_t1, x_ep)
        enemys.add(type1_ru)
        

    x = randint(1245, 1265)
    y = randint(285, 385)
    x_ep = randint(725, 745)
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 30, 90, 3, "bullet.png", 5, 5, 450, 40, walk_type2_ru, enemyStand_t2, x_ep)
    enemys.add(type2_ru)

    #

    return enemys, fon

def levels_4():
    enemys = pygame.sprite.Group()
    fon = "image/fon4.jpg"
    #
    for i in range(2):
        x = randint(765, 785)
        y = randint(285, 385)
        x_ep = randint(700, 750)
        
        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325, 20, walk_type1_ru, enemyStand_t1, x_ep)
        enemys.add(type1_ru)
        

    x = randint(1245, 1265)
    y = randint(285, 385)
    x_ep = randint(725, 745)
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 30, 90, 3, "bullet.png", 5, 5, 450, 40, walk_type2_ru, enemyStand_t2,  x_ep)
    enemys.add(type2_ru)

    #

    return enemys, fon

def levels_5():
    enemys = pygame.sprite.Group()
    fon = "image/fon5.jpg"
    #
    for i in range(2):
        x = randint(765, 785)
        y = randint(285, 385)
        x_ep = randint(700, 750)

        type1_ru = Enemy("ru/type1_ru.png", x, y, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325, 20, walk_type1_ru, enemyStand_t1, x_ep)
        enemys.add(type1_ru)
        

    x = randint(1245, 1265)
    y = randint(285, 385)
    x_ep = randint(725, 745)
    type2_ru = Enemy("ru/type2_ru.png", x, y, 3, 100, 100, fire_gun_type2, 100, 30, 90, 3, "bullet.png", 5, 5, 450, 40, walk_type2_ru, enemyStand_t2, x_ep)
    enemys.add(type2_ru)

    #

    return enemys, fon

def screensav():
    if level == 1:
        txt = ""
        txt_l = screensavers.txt_lvl1()
        for t in txt_l:
            txt += t
            txt_screensavers = font2.render(txt, True, (250, 250, 250))
            win_display.fill((0,0,0))
            win_display.blit(txt_screensavers, (350, 250))
            sleep(0.5)
        sleep(1)
    else:
        pass


def animation_pl():
    global animCount_pl
    
    if not rpgStand:
        if animCount_pl + 1 >= 10:
            animCount_pl = 0
        if run: 
            if type1_uk_walk:
                player.image = walk_type1_uk[animCount_pl//5]
                animCount_pl += 1
            elif type2_uk_walk:
                player.image = walk_type2_uk[animCount_pl//5]
                animCount_pl += 1
        elif not run:
            if type1_uk_walk:
                player.image = playerStand_t1
            elif type2_uk_walk:
                player.image = playerStand_t2




enemys = pygame.sprite.Group()


icon_info = GameSprite("icon_info.png", win_width-50, 10, 0, 25, 25)
panel_info = GameSprite("panel_info.png", 125, 50, 0, 450, 350)
cross = GameSprite("cross.png", 515, 125, 0, 25, 25)

fire_gun_type1 = fire_gun_type2 = pygame.transform.scale(pygame.image.load("image/fire_gun.png"), (25, 15))
fire_gun_type3 = pygame.transform.scale(pygame.image.load("image/fire_rpg.png"), (35, 20))

type1_uk_width, type1_uk_height = 80, 100
type2_uk_width, type2_uk_height = 100, 100

type1_ru_width, type1_ru_height = type1_uk_width, type1_uk_height
type2_ru_width, type2_ru_height = type2_uk_width, type2_uk_height

walk_type1_uk = [pygame.transform.scale(pygame.image.load("image/ua/animation_type1/anim1.png"), (type1_uk_width, type1_uk_height)), 
pygame.transform.scale(pygame.image.load("image/ua/animation_type1/anim2.png"), (type1_uk_width, type1_uk_height))]
walk_type2_uk = [pygame.transform.scale(pygame.image.load("image/ua/animation_type2/anim1.png"), (type2_uk_width, type2_uk_height)), 
pygame.transform.scale(pygame.image.load("image/ua/animation_type2/anim2.png"), (type2_uk_width, type2_uk_height))]

playerStand_t1 = pygame.transform.scale(pygame.image.load("image/ua/type1_uk.png"), (type1_uk_width, type1_uk_height))
playerStand_t2 = pygame.transform.scale(pygame.image.load("image/ua/type2_uk.png"), (type2_uk_width, type2_uk_height))

walk_type1_ru = [pygame.transform.scale(pygame.image.load("image/ru/animation_type1/anim1.png"), (type1_ru_width, type1_ru_height)), 
pygame.transform.scale(pygame.image.load("image/ru/animation_type1/anim2.png"), (type1_ru_width, type1_ru_height))]
walk_type2_ru = [pygame.transform.scale(pygame.image.load("image/ru/animation_type2/anim1.png"), (type2_ru_width, type2_ru_height)), 
pygame.transform.scale(pygame.image.load("image/ru/animation_type2/anim2.png"), (type2_ru_width, type2_ru_height))]

enemyStand_t1 = pygame.transform.scale(pygame.image.load("image/ru/type1_ru.png"), (type1_ru_width, type1_ru_height))
enemyStand_t2 = pygame.transform.scale(pygame.image.load("image/ru/type2_ru.png"), (type2_ru_width, type2_ru_height))

type1_uk = Player("ua/type1_uk.png", 50, 385, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5, 325, 30, walk_type1_uk, playerStand_t1)
type2_uk = Player("ua/type2_uk.png", 50, 385, 3, 100, 100, fire_gun_type2, 100, 1, 18, 2, "bullet.png", 5, 5, 450, 50, walk_type2_uk, playerStand_t2)
type3_uk = Player("ua/type3_uk.png", 50, 385, 0, 80, 100, fire_gun_type3, 100, 1, 3, 6, "rocket.png", 25, 15, 435, 100, None, None)

player = type1_uk
max_ammo = player.clip

player_y = player.rect.y
x_animation = -100


clock = pygame.time.Clock()
FPS = 30

bullets_ua = pygame.sprite.Group()
bullets_ru = pygame.sprite.Group()

not_ammo = font1.render("Not ammo!!" , True, (215, 64, 94))


max_lvl = 5
level = 0

animCount_pl = 0
animCount_en = 0

type1_uk_walk = True
type2_uk_walk = False
type1_ru_walk = False
type2_ru_walk = False
run = False
run_en = False

finish = True
menu = False
info = False
space = True
rel_time = False
rpgStand = False
headband = True
level_change = False 
        

#игровой цикл
game = True
while game:

    if menu:
        pass
    
    if headband:
        headband = False
        level_change = True

    if level_change: 
        level += 1
        if level == 1:
            level_char = levels_1()
            enemys = level_char[0]
            fon = level_char[1]
        elif level == 2:
            level_char = levels_2()
            enemy = level_char[0]
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
        level_change = False
        finish = False
        x_bg = 0
        player.rect.x = x_animation
        player.rect.y = player_y
        rpgStand = False
        for b in bullets_ru:
            b.kill
        for b in bullets_ua:
            b.kill()

    if len(enemys) == 0:
        headband = True 
        finish = False
    
    if not(menu):
        background = pygame.transform.scale(pygame.image.load(fon), (bg_width, bg_height))
        win_display.blit(background, (x_bg,0))
    
    if not(finish):
        #заливка фона
        
        keys_pressed = pygame.key.get_pressed()
 
        #создания спрайта-игрока
        player.reset()
        player.update()

        enemys.draw(win_display)
        enemys.update()
        
        #отображение пуль
        bullets_ua.draw(win_display)
        bullets_ua.update()
        
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

                type1_uk_walk = True
                type2_uk_walk = False
                rpgStand = False

            elif keys_pressed[pygame.K_2]:
                x = player.rect.x
                y = player.rect.y

                player = type2_uk
                player.rect.x = x
                player.rect.y = y

                max_ammo = player.clip

                type1_uk_walk = False
                type2_uk_walk = True
                rpgStand = False
                
            if keys_pressed[pygame.K_3]:
                x = player.rect.x
                y = player.rect.y

                player = type3_uk
                player.rect.x = x
                player.rect.y = y
                
                max_ammo = player.clip
                
                type1_uk_walk = False
                type2_uk_walk = False
                rpgStand = True
                
            
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
        for enemy in enemys:
            if pygame.sprite.spritecollide(enemy, bullets_ua, True):
                enemy.hp -= player.damage
                enemy.dead()
        
        gun_drum = font2.render(str(player.clip)+"/"+ str(player.ammo), True, (0,0,0))
        win_display.blit(gun_drum, (win_width-140, win_height-40))
        
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
