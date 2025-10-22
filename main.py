import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Typing Fishing Game")

# --- Game constants ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
FONT_NAME = "arial"
FONT_SIZE = 30
STARTING_CATCH_TIME = 10

# --- Game assets ---
WORDS = ["python", "pygame", "fishing", "coding", "challenge", "developer"]

class Fish(pygame.sprite.Sprite):
    def __init__(self, catch_time):
        super().__init__()
        try:
            self.image = pygame.image.load("images/fishes/fish.png").convert_alpha()
        except pygame.error:
            self.image = pygame.Surface([100, 50])
            self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(100, SCREEN_HEIGHT - self.rect.height)
        self.word = random.choice(WORDS)
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.text_surface = self.font.render(self.word, True, BLACK)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)
        self.spawn_time = time.time()
        self.catch_time = catch_time

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        surface.blit(self.text_surface, self.text_rect)
        self.draw_timer_bar(surface)

    def draw_timer_bar(self, surface):
        time_left = self.catch_time - (time.time() - self.spawn_time)
        if time_left < 0:
            time_left = 0
        fill_ratio = time_left / self.catch_time
        bar_width = self.rect.width * fill_ratio
        timer_bar_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_width, 5)
        pygame.draw.rect(surface, GREEN, timer_bar_rect)


class Fisherman(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("images/fisherman/fisherman.png").convert_alpha()
        except pygame.error:
            self.image = pygame.Surface([50, 100])
            self.image.fill(GREEN)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

class Boat(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("images/boat/boat.png").convert_alpha()
        except pygame.error:
            self.image = pygame.Surface([200, 100])
            self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

class Scenario(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load("images/cenario/background.png").convert()
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            self.image = pygame.Surface([SCREEN_WIDTH, SCREEN_HEIGHT])
            self.image.fill((135, 206, 235)) # Sky blue
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

# --- Game setup ---
score = 0
time_to_catch = STARTING_CATCH_TIME
all_sprites = pygame.sprite.Group()
fish = Fish(time_to_catch)
current_typed_word = ""
font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
background = Scenario()
boat = Boat()
fisherman = Fisherman()
all_sprites.add(boat, fisherman)

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                current_typed_word = current_typed_word[:-1]
            elif event.key == pygame.K_RETURN:
                if current_typed_word == fish.word:
                    score += 1
                    time_to_catch *= 0.95 # Decrease time to catch by 5%
                    fish = Fish(time_to_catch)
                    current_typed_word = ""
            else:
                current_typed_word += event.unicode

    # Check if fish escaped
    if time.time() - fish.spawn_time > fish.catch_time:
        fish = Fish(time_to_catch)


    # Drawing code here
    screen.blit(background.image, background.rect)
    all_sprites.draw(screen)
    fish.draw(screen)

    # Draw the typed word
    typed_text_surface = font.render(current_typed_word, True, WHITE)
    screen.blit(typed_text_surface, (10, 10))

    # Draw the score
    score_surface = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surface, (SCREEN_WIDTH - score_surface.get_width() - 10, 10))


    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
