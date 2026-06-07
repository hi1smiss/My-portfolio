import pygame
import random
from time import *

pygame.init()

width, height = 800, 400
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Dino")

pygame.mixer.init()

dino_img = pygame.image.load("dino.png")
cactus_img = pygame.image.load("cactus.png")
ground_img = pygame.image.load("ground.png")

dino_img = pygame.transform.scale(dino_img,(60,60))
cactus_img = pygame.transform.scale(cactus_img,(30,60))
ground_img = pygame.transform.scale(ground_img,(width,90))

jump_sound = pygame.mixer.Sound("dinojumpsound.mp3")
levelup_sound = pygame.mixer.Sound("dinolevelupsound.mp3")
loose_sound = pygame.mixer.Sound("dinoloosesound.mp3")
pygame.mixer.music.load("3d20874f20174bd.mp3")
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1)


dino_width = 50
dino_height = 50
dino_x = height - dino_height-20
dino_y = height - dino_height-20
dino_vel_y = 0
gravity = 1
jump_height =- 15
is_jumping = False

obstacle_width, obstacle_height = 20, 50
obstacle_x = width
obstacle_y = height - 50
obstacle_vel = 10

black = (0, 0, 0)
white = (255, 255, 255)
green = (0, 255, 0)

score = 0
font = pygame.font.SysFont("Arial", 20)

clock = pygame.time.Clock()
fps = 60


class Dino:
    def __init__(self):
        self.image = dino_img
        self.x = 50
        self.ground_y = height - self.image.get_height() - 50
        self.y = self.ground_y

        self.vel_y = 0
        self.gravity = 0.9
        self.jump_force = -15
        self.is_jumping = False

        self.jump_count_total = 0

    def jump(self):
        if self.is_jumping:
            self.vel_y += self.gravity
            self.y += self.vel_y

            if self.y >= self.ground_y:
                self.y = self.ground_y
                self.vel_y = 0
                self.is_jumping = False

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))


class Obstacle:
    def __init__(self):
        data = random.choice(OBSTACLE_TYPES)

        self.image = data["image"]
        self.speed = data["speed"]

        self.x = width
        self.y = height - self.image.get_height() - data["y_offset"]

    def update(self):
        self.x -= self.speed
        if self.x < -self.image.get_width():
            self.reset()

    def reset(self):
        data = random.choice(OBSTACLE_TYPES)
        self.image = data["image"]
        self.speed = game_speed
        self.x = width
        self.y = height - self.image.get_height() - data["y_offset"]

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

class Ground:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.speed = 8
        self.image = pygame.image.load("ground.png")
        self.image = pygame.transform.scale(self.image,(800,20))
        self.rect = pygame.Rect(self.x, height-100, width, 50)

    def update(self):
        self.x -= self.speed
        if self.x <= -width:
            self.x = 0
        self.rect.topleft = (self.x, height-100)

    def draw(self, screen):
        screen.blit(self.image, (self.x, height-53))
        screen.blit(self.image, (self.x+width, height-53))

def display_score(score, screen):
    score_text = font.render(f"Score: {score}", True, black)
    screen.blit(score_text, (10, 10))
    if score % 100 == 0:
        levelup_sound.play()


def draw_menu(screen):
    screen.fill(white)

    title_font = pygame.font.SysFont("Arial", 50, bold=True)
    title_text = title_font.render("DINO RUN", True, black)

    site_font = pygame.font.SysFont("Arial", 15)
    site_text = site_font.render("Music from: zvukipro.com", True, (100, 100, 100))

    hint_font = pygame.font.SysFont("Arial", 25)
    hint_text = hint_font.render("Нажми SPACE чтобы начать", True, black)

    screen.blit(title_text, (width // 2 - title_text.get_width() // 2, 100))
    screen.blit(site_text, (width // 2 - site_text.get_width() // 2, 160))
    screen.blit(hint_text, (width // 2 - hint_text.get_width() // 2, 250))

OBSTACLE_TYPES = [
    {"image": cactus_img, "y_offset": 50, "speed": 10},
    {"image": pygame.transform.scale(cactus_img, (40, 80)), "y_offset": 50, "speed": 10},
    {"image": pygame.transform.scale(cactus_img, (25, 94)), "y_offset": 50, "speed": 10},
]


# ИНИЦИАЛИЗАЦИЯ
game_speed = 8
speed_step = 2
last_score_threshold = 0
dino = Dino()
obstacle = Obstacle()
ground = Ground()
running = True
game_over = False
show_menu = True
score = 1
SCORE_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(SCORE_EVENT, 1000)


# ИГРОВОЙ ЦИКЛ
while running:
    if show_menu:
        draw_menu(window)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    show_menu = False
                    pygame.mixer.music.play(-1)
        pygame.display.update()
        continue
    window.fill(white)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == SCORE_EVENT and not game_over:
            score += 2
        if score > 0 and score // 100 > last_score_threshold:
            game_speed += speed_step
            last_score_threshold = score // 100

            obstacle.speed = game_speed

            ground_speed = game_speed

            print(f"Сложность повышена! Скорость: {game_speed}")
        if event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_SPACE:
                dino = Dino()
                obstacle = Obstacle()
                score = 1
                game_over = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_SPACE] and not dino.is_jumping and not game_over:
        dino.is_jumping = True
        dino.vel_y = dino.jump_force
        jump_sound.play()

        dino.jump_count_total += 1
        print(f"Прыжков выполнено: {dino.jump_count_total}")

    if not game_over:
        dino.jump()
        obstacle.update()
        ground.update()

        dino_rect = pygame.Rect(
            dino.x, dino.y,
            dino.image.get_width(),
            dino.image.get_height()
        )
        obs_rect = pygame.Rect(
            obstacle.x, obstacle.y,
            obstacle.image.get_width(),
            obstacle.image.get_height()
        )

        if dino_rect.colliderect(obs_rect):
            game_over = True
            loose_sound.play()

        if obstacle.x + obstacle.image.get_width() < dino.x:
            score += 1

    ground.draw(window)
    dino.draw(window)
    obstacle.draw(window)
    display_score(score, window)

    if game_over:
        text = font.render("GAME OVER — нажми на Space", True, black)
        window.blit(text, (250, 180))

    pygame.display.update()
    clock.tick(fps)

pygame.quit()