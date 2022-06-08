from time import monotonic as timer 
import pygame
#окно игры
win_width = 700
win_height = 500
win_display = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("project")

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
    player_height, fire_gun, player_health_point, player_gun_clip, player_total_ammo, gun_reload, image_ammo_gun, ammo_width, ammo_height):
        super().__init__(player_image, player_x, player_y, player_speed, player_width, player_height)
        self.blink = fire_gun
        self.hp = player_health_point
        self.clip = player_gun_clip
        self.ammo = player_total_ammo
        self.reload = gun_reload
        self.image_ammo = image_ammo_gun
        self.ammo_width = ammo_width
        self.ammo_height = ammo_height

#класс игрока
class Player(Warrior):
    #передвижение спрайта
    def update(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        elif keys_pressed[pygame.K_d] and self.rect.x < win_width - 90:
            self.rect.x += self.speed
        elif keys_pressed[pygame.K_w] and self.rect.y > 285:
            self.rect.y -= self.speed
        elif keys_pressed[pygame.K_s] and self.rect.y <= 385:
            self.rect.y += self.speed
    #стрельба
    def fire(self):
        bullet = Bullet(self.image_ammo, self.rect.right, self.rect.top+16, 3, self.ammo_width, self.ammo_height)
        bullets_uk.add(bullet)
        win_display.blit(self.blink, (self.rect.right-3, self.rect.top+12))
        

#класс пули
class Bullet(GameSprite):
    #перемещение пули
    def update(self):
        self.rect.x += self.speed
        if self.rect.x > win_width:
            self.kill()
            

#класс врага
class Enemy(Warrior):
    #перемещение врага
    def update(self,*args):
        if  self.rect.y < args[0]:     
            self.rect.y += self.speed
        else:
            pass

icon_info = GameSprite("icon_info.png", win_width-50, 10, 0, 25, 25)
panel_info = GameSprite("panel_info.png", 125, 50, 0, 450, 350)
cross = GameSprite("cross.png", 515, 125, 0, 25, 25)

fire_gun_type1 = fire_gun_type2 = pygame.transform.scale(pygame.image.load("image/fire_gun.png"), (25, 15))
fire_gun_type3 = pygame.transform.scale(pygame.image.load("image/fire_rpg.png"), (35, 20))

type1_uk = Player("type1_uk.png", 50, 385, 3, 80, 100, fire_gun_type1, 100, 30, 90, 3, "bullet.png", 5, 5)
type2_uk = Player("type2_uk.png", 50, 385, 3, 100, 100, fire_gun_type2, 100, 1, 18, 2, "bullet.png", 5, 5)
type3_uk = Player("type3_uk.png", 50, 385, 0, 80, 100, fire_gun_type3, 100, 1, 3, 6, "rocket.png", 25, 15)

player = type1_uk
max_ammo = player.clip


clock = pygame.time.Clock()
FPS = 60

bullets_uk = pygame.sprite.Group()
bullets_ru = pygame.sprite.Group()

not_ammo = font1.render("Not ammos!!" , True, (215, 64, 94))


#игровой цикл
finish = False
game = True
menu = True
info = False
space = True
rel_time = False
while game:
    
    if menu:
        pass
    
    if not(finish):
        #заливка фона
        win_display.fill((230, 230, 230))
        keys_pressed = pygame.key.get_pressed()

        #создания спрайта-игрока
        player.reset()
        player.update()
        
        #отображение пуль
        bullets_uk.draw(win_display)
        bullets_uk.update()
        
        #иконка с инфой
        icon_info.reset()
        if not(rel_time):
            if keys_pressed[pygame.K_1]:
                player = type1_uk
                max_ammo = player.clip
            elif keys_pressed[pygame.K_2]:
                player = type2_uk
                max_ammo = player.clip
            if keys_pressed[pygame.K_3]:
                player = type3_uk
                max_ammo = player.clip
                
            
        #стрельба
        if space:
            if keys_pressed[pygame.K_SPACE]:
                #проверка наличия патронов в обойме
                if player.clip != 0:    
                    #проверка налачия патронов в запасе               
                    if player.ammo >= 0:
                        player.fire()
                        player.clip -= 1
                #если патронов нету в обойме, но есть в запасе - перезарядка
                elif player.clip == 0 and player.ammo != 0:
                    rel_time = True
                    space = False
                    start_rel = timer()
                #если патронов нигде нету - надпись "Нет патронов"
                elif player.clip == 0 and player.ammo == 0:
                    win_display.blit(not_ammo, (win_width-150, win_height-60))
    
    #инфармационная панель     
    if info:
        panel_info.reset()
        cross.reset()

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


    gun_drum = font2.render(str(player.clip)+"/"+ str(player.ammo), True, (0,0,0))
    win_display.blit(gun_drum, (win_width-140, win_height-40))

    clock.tick(FPS)
    pygame.display.update()
