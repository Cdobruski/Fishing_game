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

        self.legendary_fish_names = ["truta lendária.png"]
        self.epic_fish_names = ["Narval.png", "peixe_fantasma.png"]
        self.common_fish_names = [f for f in all_fish_images if f not in self.legendary_fish_names and f not in self.epic_fish_names]

        if not self.common_fish_names:
            self.common_fish_names.append("placeholder.png")

        self.load_image()
        self.rect = self.image.get_rect()
        self.original_pos = (random.randint(0, SCREEN_WIDTH - self.rect.width),
                             random.randint(WATERLINE_Y, SCREEN_HEIGHT - self.rect.height))
        self.rect.topleft = self.original_pos
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.new_word(difficulty)

    def update(self):
        self.rect.x = self.original_pos[0] + random.randint(-2, 2)
        self.rect.y = self.original_pos[1] + random.randint(-2, 2)

    def determine_rarity(self):
        rand = random.random()
        if rand < RARITY_CHANCES["legendary"]:
            return "legendary"
        elif rand < RARITY_CHANCES["legendary"] + RARITY_CHANCES["epic"]:
            return "epic"
        else:
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
        elif self.rarity == "epic":
            fish_image_name = random.choice(self.epic_fish_names)
        else:
            fish_image_name = random.choice(self.common_fish_names)

        try:
            image = pygame.image.load(resource_path(f"images/fishes/{fish_image_name}")).convert_alpha()
            self.image = pygame.transform.scale(image, (75, 40))
        except pygame.error:
            self.image = pygame.Surface([75, 40])
            if self.rarity == "legendary":
                self.image.fill(GOLD)
            elif self.rarity == "epic":
                self.image.fill((128, 0, 128))
            else:
                self.image.fill(WHITE)

    def draw(self, surface, typed_word=""):
        surface.blit(self.image, self.rect)
        x_offset = 0
        for i, char in enumerate(self.word):
            # Black outline
            outline_color = BLACK
            char_outline = self.font.render(char, True, outline_color)
            for dx in [-1, 1]:
                for dy in [-1, 1]:
                    outline_rect = char_outline.get_rect(topleft=(self.text_rect.x + x_offset + dx, self.text_rect.y + dy))
                    surface.blit(char_outline, outline_rect)

            # White fill
            color = WHITE
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
    def __init__(self, rod_level, boat):
        super().__init__()
        self.rod_level = rod_level
        self.boat = boat
        self.animation_frames = []
        self.load_animation_frames()
        self.current_frame = 0
        self.image = self.animation_frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 100 # milliseconds
        self.animation_done = False
        self.rod_offsets = [
            (20, -30), (22, -32), (24, -34), (26, -36), (28, -38),
            (30, -40), (28, -38), (26, -36), (24, -34), (22, -32)
        ]
        self.rod_end_offset = (0, 80) # an approximation

    def reset_animation(self):
        self.current_frame = 0
        self.animation_done = False

    def load_animation_frames(self):
        self.animation_frames = []
        # The user's screenshot shows pixil-frame-1.png to pixil-frame-10.png
        # The loop should be from 1 to 10.
        for i in range(1, 11):
            try:
                # Correcting the filename format based on the screenshot.
                frame = pygame.image.load(resource_path(f"images/fisherman/pixil-frame-{i}.png")).convert_alpha()
                frame = pygame.transform.scale(frame, (180, 150))
                self.animation_frames.append(frame)
            except pygame.error:
                # Create a placeholder if the image is not found
                frame = pygame.Surface([180, 150])
                frame.fill(GREEN)
                self.animation_frames.append(frame)

    def update(self):
        if not self.animation_done:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.animation_speed:
                self.last_update = now
                self.current_frame += 1
                if self.current_frame == len(self.animation_frames):
                    self.animation_done = True
                    self.current_frame -= 1 # Stay on last frame
                self.image = self.animation_frames[self.current_frame]
        self.rect.centerx = self.boat.rect.centerx + 50
        self.rect.bottom = self.boat.rect.top + 65

    def load_image(self):
        self.load_animation_frames()

class Boat(pygame.sprite.Sprite):
    def __init__(self, boat_level):
        super().__init__()
        self.boat_level = boat_level
        self.load_image()
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = WATERLINE_Y + 75

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


class Water(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT - WATERLINE_Y), pygame.SRCALPHA)
        self.image.fill((0, 0, 50, 100)) # Dark blue with alpha
        self.rect = self.image.get_rect()
        self.rect.topleft = (0, WATERLINE_Y)

class ScorePopup(pygame.sprite.Sprite):
    def __init__(self, x, y, score):
        super().__init__()
        self.font = pygame.font.SysFont(FONT_NAME, 24)
        self.image = self.font.render(f"+{score}", True, GOLD)
        self.rect = self.image.get_rect(center=(x, y))
        self.alpha = 255
        self.y_velocity = -1
        self.fade_rate = 5
        self.creation_time = pygame.time.get_ticks()

    def update(self):
        self.rect.y += self.y_velocity
        self.alpha -= self.fade_rate
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)
