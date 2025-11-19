import pygame
import random
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
        self.words_history = []
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
        self.words_history.append(self.word)
        self.text_surface = self.font.render(self.word, True, BLACK)
        self.text_rect = self.text_surface.get_rect(midleft=self.rect.midright)
        if self.text_rect.right > SCREEN_WIDTH:
            self.text_rect.midright = self.rect.midleft

    def load_image(self):
        if self.rarity == "legendary":
            fish_image_name = random.choice(self.legendary_fish_names)
        elif self.rarity == "epic":
            fish_image_name = random.choice(self.epic_fish_names)
        else:
            fish_image_name = random.choice(self.common_fish_names)

        self.name = fish_image_name.split('.')[0]

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
        self.state = "casting" # casting, hooked, reeling
        self.animation_complete = False
        self.rod_offsets = [
            (20, -30), (22, -32), (24, -34), (26, -36), (28, -38),
            (30, -40), (28, -38), (26, -36), (24, -34), (22, -32)
        ]
        self.rod_end_offset = (0, 80) # an approximation

    def reset_animation(self):
        self.current_frame = 0
        self.state = "casting"
        self.animation_complete = False

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
        now = pygame.time.get_ticks()
        if now - self.last_update > self.animation_speed:
            self.last_update = now
            if self.state == "casting" and self.current_frame < 6:
                self.current_frame += 1
            elif self.state == "reeling":
                if self.current_frame < len(self.animation_frames) - 1:
                    self.current_frame += 1
                else:
                    self.animation_complete = True
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

class Rod(pygame.sprite.Sprite):
    def __init__(self, rod_level):
        super().__init__()
        self.rod_level = rod_level
        self.load_image()
        self.rect = self.image.get_rect()

    def load_image(self):
        try:
            image_path = resource_path(f"images/misc/vara ({self.rod_level}).png")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (120, 60))
        except pygame.error:
            self.image = pygame.Surface([120, 60])
            self.image.fill(BROWN)

class Float(pygame.sprite.Sprite):
    def __init__(self, float_level):
        super().__init__()
        self.float_level = float_level
        self.load_image()
        self.rect = self.image.get_rect()

    def load_image(self):
        try:
            image_path = resource_path(f"images/misc/boia ({self.float_level}).png")
            self.image = pygame.image.load(image_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
        except pygame.error:
            self.image = pygame.Surface([60, 60])
            self.image.fill(BLUE)

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
    def __init__(self, score, x, y):
        super().__init__()
        self.font = pygame.font.SysFont(FONT_NAME, 50)
        self.image = self.font.render(f"+{score}", True, GOLD)
        rand_x = random.randint(100, SCREEN_WIDTH - 100)
        rand_y = random.randint(100, SCREEN_HEIGHT - 100)
        self.rect = self.image.get_rect(center=(rand_x, rand_y))
        self.creation_time = pygame.time.get_ticks()
        self.speed_y = -2
        self.alpha = 255

    def update(self):
        self.rect.y += self.speed_y
        self.alpha -= 2
        if self.alpha <= 0:
            self.kill()
        else:
            self.image.set_alpha(self.alpha)

class Button(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, text, font_size=50, image_path="images/button/botao.png"):
        super().__init__()
        self.image = pygame.image.load(resource_path(image_path)).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(center=(x, y))
        self.font = pygame.font.SysFont(FONT_NAME, font_size)
        self.text = text
        self.text_surface = self.font.render(text, True, WHITE)
        self.text_rect = self.text_surface.get_rect(center=self.rect.center)

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        surface.blit(self.text_surface, self.text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False
