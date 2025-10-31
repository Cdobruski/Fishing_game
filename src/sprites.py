import pygame
import random
from src.settings import *

class Fish(pygame.sprite.Sprite):
    def __init__(self, difficulty):
        super().__init__()
        try:
            self.image = pygame.image.load("images/fishes/fish.png").convert_alpha()
        except pygame.error:
            self.image = pygame.Surface([100, 50])
            self.image.fill(WHITE)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(100, SCREEN_HEIGHT - self.rect.height)
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.new_word(difficulty)

    def new_word(self, difficulty):
        if difficulty == "easy":
            self.word = random.choice(WORDS_EASY)
        elif difficulty == "medium":
            self.word = random.choice(WORDS_MEDIUM)
        else:
            self.word = random.choice(WORDS_HARD)
        self.text_surface = self.font.render(self.word, True, BLACK)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        surface.blit(self.text_surface, self.text_rect)

    def draw_progress_bar(self, surface, words_caught, words_needed):
        if words_needed > 0:
            fill_ratio = words_caught / words_needed
            bar_width = self.rect.width * fill_ratio
            progress_bar_rect = pygame.Rect(self.rect.x, self.rect.y - 10, bar_width, 5)
            pygame.draw.rect(surface, GREEN, progress_bar_rect)

class Fisherman(pygame.sprite.Sprite):
    def __init__(self, rod_level):
        super().__init__()
        self.rod_level = rod_level
        self.animation_frames = []
        self.load_animation_frames()
        self.current_frame = 0
        self.image = self.animation_frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 100 # milliseconds

    def load_animation_frames(self):
        self.animation_frames = []
        for i in range(10):
            try:
                frame = pygame.image.load(f"images/fisherman/level_{self.rod_level}_animation/{i}.png").convert_alpha()
                self.animation_frames.append(frame)
            except pygame.error:
                # Create a placeholder if the image is not found
                frame = pygame.Surface([50 + (self.rod_level - 1) * 10, 100 + (self.rod_level - 1) * 10])
                frame.fill(GREEN)
                self.animation_frames.append(frame)

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.image = self.animation_frames[self.current_frame]

    def load_image(self):
        self.load_animation_frames()

class Boat(pygame.sprite.Sprite):
    def __init__(self, boat_level):
        super().__init__()
        self.boat_level = boat_level
        self.load_image()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

    def load_image(self):
        try:
            self.image = pygame.image.load(f"images/boat/boat_lvl_{self.boat_level}.png").convert_alpha()
        except pygame.error:
            self.image = pygame.Surface([200 + (self.boat_level - 1) * 20, 100])
            self.image.fill(RED)

class Scenario(pygame.sprite.Sprite):
    def __init__(self, area="river"):
        super().__init__()
        self.area = area
        self.time_of_day = random.choice(["day", "night"])
        self.load_image()
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

    def load_image(self):
        try:
            self.image = pygame.image.load(f"images/cenario/{self.area}_{self.time_of_day}.png").convert()
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            self.image = pygame.Surface([SCREEN_WIDTH, SCREEN_HEIGHT])
            if self.time_of_day == "day":
                self.image.fill((135, 206, 235)) # Sky blue
            else:
                self.image.fill((0, 0, 50)) # Dark blue
