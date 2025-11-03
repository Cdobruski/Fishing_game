import pygame
import random
import os
from src.settings import *

class Fish(pygame.sprite.Sprite):
    def __init__(self, difficulty, float_level):
        super().__init__()
        self.float_level = float_level
        self.rarity = self.determine_rarity()

        # This approach might not be ideal for PyInstaller. A better way would be to have a predefined list.
        # However, we'll stick to this for now and adjust if needed.
        try:
            all_fish_images = [f for f in os.listdir(resource_path("images/fishes")) if f.endswith(".png")]
        except FileNotFoundError:
            all_fish_images = []

        self.legendary_fish_names = ["truta lendaria.png", "peixe_fantasma.png", "narval.png"] # Assuming ghost and narwhal are legendary
        self.common_fish_names = [f for f in all_fish_images if f not in self.legendary_fish_names]

        if not self.common_fish_names:
            self.common_fish_names.append("placeholder.png")

        self.load_image()
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(100, SCREEN_HEIGHT - self.rect.height)
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.new_word(difficulty)

    def determine_rarity(self):
        legendary_chance = self.float_level * 0.05
        if random.random() < legendary_chance:
            return "legendary"
        return "common"

    def new_word(self, difficulty):
        if difficulty == "easy":
            self.word = random.choice(WORDS_EASY)
        elif difficulty == "medium":
            self.word = random.choice(WORDS_MEDIUM)
        else:
            self.word = random.choice(WORDS_HARD)
        self.text_surface = self.font.render(self.word, True, BLACK)
        self.text_rect = self.text_surface.get_rect(midleft=self.rect.midright)

    def load_image(self):
        if self.rarity == "legendary":
            fish_image_name = random.choice(self.legendary_fish_names)
        else:
            fish_image_name = random.choice(self.common_fish_names)

        try:
            image = pygame.image.load(resource_path(f"images/fishes/{fish_image_name}")).convert_alpha()
            self.image = pygame.transform.scale(image, (150, 80))
        except pygame.error:
            self.image = pygame.Surface([150, 80])
            if self.rarity == "legendary":
                self.image.fill(GOLD)
            else:
                self.image.fill(WHITE)

    def draw(self, surface, typed_word=""):
        surface.blit(self.image, self.rect)
        x_offset = 0
        for i, char in enumerate(self.word):
            color = BLACK
            if i < len(typed_word) and typed_word[i] == char:
                color = GREEN

            char_surface = self.font.render(char, True, color)
            char_rect = char_surface.get_rect(topleft=(self.text_rect.x + x_offset, self.text_rect.y))
            surface.blit(char_surface, char_rect)
            x_offset += char_surface.get_width()

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
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 250)
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 100 # milliseconds
        self.rod_offsets = [
            (20, -30), (22, -32), (24, -34), (26, -36), (28, -38),
            (30, -40), (28, -38), (26, -36), (24, -34), (22, -32)
        ]

    def load_animation_frames(self):
        self.animation_frames = []
        # The user's screenshot shows pixil-frame-1.png to pixil-frame-10.png
        # The loop should be from 1 to 10.
        for i in range(1, 11):
            try:
                # Correcting the filename format based on the screenshot.
                frame = pygame.image.load(resource_path(f"images/fisherman/pixil-frame-{i}.png")).convert_alpha()
                self.animation_frames.append(frame)
            except pygame.error:
                # Create a placeholder if the image is not found
                frame = pygame.Surface([50, 100])
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
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200)

    def load_image(self):
        try:
            image = pygame.image.load(resource_path(f"images/boat/boat_lvl_{self.boat_level}.png")).convert_alpha()
            self.image = pygame.transform.scale(image, (300, 150))
        except pygame.error:
            self.image = pygame.Surface([300, 150])
            self.image.fill(RED)

class Scenario(pygame.sprite.Sprite):
    def __init__(self, area="river", time_of_day=None):
        super().__init__()
        self.area = area
        if time_of_day:
            self.time_of_day = time_of_day
        else:
            self.time_of_day = random.choice(["day", "night"])
        self.load_image()
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, 0)

    def load_image(self):
        filename_map = {
            ("river", "day"): "river_day.png",
            ("river", "night"): "cenario rio noite.png",
            ("beach", "day"): "cenario praia dia.png",
            ("beach", "night"): "cenario praia noite.png",
        }

        filename = filename_map.get((self.area, self.time_of_day), "river_day.png") # Default to river_day

        try:
            self.image = pygame.image.load(resource_path(f"images/cenario/{filename}")).convert()
            self.image = pygame.transform.scale(self.image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except pygame.error:
            self.image = pygame.Surface([SCREEN_WIDTH, SCREEN_HEIGHT])
            if self.time_of_day == "day":
                self.image.fill((135, 206, 235)) # Sky blue
            else:
                self.image.fill((0, 0, 50)) # Dark blue

class Float(pygame.sprite.Sprite):
    def __init__(self, float_level):
        super().__init__()
        self.float_level = float_level
        self.load_image()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2 + 100, SCREEN_HEIGHT - 150)

    def load_image(self):
        try:
            self.image = pygame.image.load(resource_path(f"images/misc/boia ({self.float_level}).png")).convert_alpha()
        except pygame.error:
            self.image = pygame.Surface([20, 20])
            self.image.fill(WHITE)

class Rod(pygame.sprite.Sprite):
    def __init__(self, rod_level):
        super().__init__()
        self.rod_level = rod_level
        self.load_image()
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 150)

    def load_image(self):
        try:
            self.image = pygame.image.load(resource_path(f"images/misc/vara ({self.rod_level}).png")).convert_alpha()
        except pygame.error:
            self.image = pygame.Surface([10, 100])
            self.image.fill(BLACK)
