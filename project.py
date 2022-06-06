import pygame
#окно игры
win_width = 700
win_height = 500
win_display = pygame.display.set_mode((win_width, win_height))
pygame.display.set_caption("project")


#создание игрового класса
class GameSprite(pygame.sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, player_speed, player_width, player_height):
        super().__init__()
        self.player = player_image
        self.width = player_width
        self.height = player_height
        self.image = pygame.transform.scale(pygame.image.load(self.player), (self.width, self.height)) 
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y
        self.speed = player_speed
        

    def reset(self):
        win_display.blit(self.image, (self.rect.x, self.rect.y))
#класс игрока
class Player(GameSprite):
    #передвижение спрайта
    def update(self):
        keys_pressed = pygame.key.get_pressed()
        if keys_pressed[pygame.K_a] and self.rect.x > 5:
            self.rect.x -= self.speed
        elif keys_pressed[pygame.K_d] and self.rect.x < win_width - 80:
            self.rect.x += self.speed
    #стрельба
    def fire(self):
        bullet = Bullet("bullet.png", self.rect.centerx, self.rect.top, 3, 10, 10)
        

#класс пули
class Bullet(GameSprite):
    #перемещение пули
    def update(self):
        self.rect.y -= self.speed
        if self.rect.y < 0:
            self.kill()
            

#класс врага
class Enemy(GameSprite):
    #перемещение врага
    def update(self,*args):
        if  self.rect.y < args[0]:     
            self.rect.y += self.speed
        else:
            pass



#свойства бета-спрайта-игрока
x = 50
y = 415
speed = 3


b_x = 0
clock = pygame.time.Clock()
FPS = 60
    
#игровой цикл
game = True
while game:
    #заливка фона
    win_display.fill((230, 230, 230))
    keys_pressed = pygame.key.get_pressed()

    #создания спрайта-игрока
    player = pygame.draw.rect(win_display, (0,0,0),(x, y, 50, 75))
    
    #передвижение грока
    if keys_pressed[pygame.K_a] and x > 10:
        x -= speed
    if keys_pressed[pygame.K_d] and x < win_width-50:
        x += speed
   
    

    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            game = False

    clock.tick(FPS)
    pygame.display.update()