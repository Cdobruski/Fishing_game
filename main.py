import pygame
import random
import time
import csv

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
# --- Difficulty Settings ---
DIFFICULTY_SETTINGS = {
    "easy": {"words_to_catch": 5, "time_limit": 60},
    "medium": {"words_to_catch": 7, "time_limit": 45, "money_multiplier": 2},
    "hard": {"words_to_catch": 10, "time_limit": 30, "money_multiplier": 3}
}

def save_data():
    with open('player_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['score', 'money', 'boat_level', 'rod_level'])
        writer.writerow([score, money, boat_level, rod_level])

def load_data():
    global score, money, boat_level, rod_level
    try:
        with open('player_data.csv', 'r') as file:
            reader = csv.reader(file)
            header = next(reader)
            data = next(reader)
            score = int(data[0])
            money = int(data[1])
            boat_level = int(data[2])
            rod_level = int(data[3])
    except (FileNotFoundError, StopIteration):
        score = 0
        money = 0
        boat_level = 1
        rod_level = 1

# --- Game assets ---
WORDS_EASY = ["sol", "mar", "rio", "peixe", "barco", "isca", "rede", "agua"]
WORDS_MEDIUM = ["pescador", "anzol", "oceano", "praia", "areia", "vento", "nuvem", "onda"]
WORDS_HARD = ["horizonte", "profundeza", "tempestade", "maritimo", "nadadeira", "escama", "pescaria", "molinete"]

class Fish(pygame.sprite.Sprite):
    def __init__(self):
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
        self.new_word()

    def new_word(self):
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

# --- Game State Manager ---
game_state = "main_menu"
difficulty = "easy"

def main_menu_screen():
    global game_state
    screen.fill((0, 100, 200))
    title_font = pygame.font.SysFont(FONT_NAME, 70)
    option_font = pygame.font.SysFont(FONT_NAME, 50)

    title_text = title_font.render("Typing Fishing Game", True, WHITE)
    play_text = option_font.render("Press P to Play", True, WHITE)
    upgrades_text = option_font.render("Press U for Upgrades", True, WHITE)
    quit_text = option_font.render("Press Q to Quit", True, WHITE)

    screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 100))
    screen.blit(play_text, (SCREEN_WIDTH/2 - play_text.get_width()/2, 300))
    screen.blit(upgrades_text, (SCREEN_WIDTH/2 - upgrades_text.get_width()/2, 400))
    screen.blit(quit_text, (SCREEN_WIDTH/2 - quit_text.get_width()/2, 500))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                game_state = "difficulty_select"
            elif event.key == pygame.K_u:
                game_state = "upgrades"
            elif event.key == pygame.K_q:
                return False
    return True

def difficulty_select_screen():
    global game_state, difficulty
    screen.fill((0, 100, 200))
    title_font = pygame.font.SysFont(FONT_NAME, 70)
    option_font = pygame.font.SysFont(FONT_NAME, 50)

    title_text = title_font.render("Select Difficulty", True, WHITE)
    easy_text = option_font.render("Press E for Easy", True, WHITE)
    medium_text = option_font.render("Press M for Medium", True, WHITE)
    hard_text = option_font.render("Press H for Hard", True, WHITE)
    back_text = option_font.render("Press B to go Back", True, WHITE)

    screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 100))
    screen.blit(easy_text, (SCREEN_WIDTH/2 - easy_text.get_width()/2, 250))
    screen.blit(medium_text, (SCREEN_WIDTH/2 - medium_text.get_width()/2, 350))
    screen.blit(hard_text, (SCREEN_WIDTH/2 - hard_text.get_width()/2, 450))
    screen.blit(back_text, (SCREEN_WIDTH/2 - back_text.get_width()/2, 550))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                difficulty = "easy"
                reset_game()
                game_state = "playing"
            elif event.key == pygame.K_m:
                difficulty = "medium"
                reset_game()
                game_state = "playing"
            elif event.key == pygame.K_h:
                difficulty = "hard"
                reset_game()
                game_state = "playing"
            elif event.key == pygame.K_b:
                game_state = "main_menu"
    return True

def upgrades_screen():
    global game_state, money, boat_level, rod_level
    screen.fill((50, 50, 50))
    font = pygame.font.SysFont(FONT_NAME, 40)

    # --- Texts ---
    title_text = font.render("Upgrades", True, WHITE)
    money_text = font.render(f"Money: ${money}", True, WHITE)
    boat_text = font.render(f"Boat Level: {boat_level} (Cost: ${boat_level*10}) - Press 1", True, WHITE)
    rod_text = font.render(f"Rod Level: {rod_level} (Cost: ${rod_level*10}) - Press 2", True, WHITE)
    back_text = font.render("Press B to go Back", True, WHITE)

    # --- Blitting ---
    screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 50))
    screen.blit(money_text, (20, 20))
    screen.blit(boat_text, (50, 200))
    screen.blit(rod_text, (50, 300))
    screen.blit(back_text, (50, 500))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:
                if money >= boat_level * 10 and boat_level < 3:
                    money -= boat_level * 10
                    boat_level += 1
                    save_data()
            elif event.key == pygame.K_2:
                if money >= rod_level * 10 and rod_level < 3:
                    money -= rod_level * 10
                    rod_level += 1
                    save_data()
            elif event.key == pygame.K_b:
                game_state = "main_menu"
    return True

def reset_game():
    global words_caught_count, fish, current_typed_word, fishing_start_time
    words_caught_count = 0
    fish = Fish()
    current_typed_word = ""
    fishing_start_time = time.time()

def game_loop():
    global game_state, score, money, current_typed_word, words_caught_count, fishing_start_time

    settings = DIFFICULTY_SETTINGS[difficulty]
    words_needed = settings["words_to_catch"] - (rod_level - 1)
    time_limit = settings["time_limit"] + ((boat_level - 1) * 10)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            return False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state = "main_menu"
            elif event.key == pygame.K_BACKSPACE:
                current_typed_word = current_typed_word[:-1]
            elif event.key == pygame.K_RETURN:
                if current_typed_word == fish.word:
                    words_caught_count += 1
                    if words_caught_count >= words_needed:
                        score += 1
                        money += 1 * settings.get("money_multiplier", 1)
                        save_data()
                        reset_game()
                    else:
                        fish.new_word()
                    current_typed_word = ""
            else:
                current_typed_word += event.unicode

    time_elapsed = time.time() - fishing_start_time
    if time_elapsed > time_limit:
        reset_game()

    # Drawing code here
    screen.blit(background.image, background.rect)
    all_sprites.draw(screen)
    fish.draw(screen)
    fish.draw_progress_bar(screen, words_caught_count, words_needed)

    typed_text_surface = font.render(current_typed_word, True, WHITE)
    screen.blit(typed_text_surface, (10, 10))

    score_surface = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_surface, (SCREEN_WIDTH - score_surface.get_width() - 10, 10))

    time_left = time_limit - time_elapsed
    timer_surface = font.render(f"Time: {int(time_left)}s", True, WHITE)
    screen.blit(timer_surface, (SCREEN_WIDTH/2 - timer_surface.get_width()/2, 10))

    return True

# --- Game setup ---
score = 0
money = 0
boat_level = 1
rod_level = 1
load_data()
words_caught_count = 0
all_sprites = pygame.sprite.Group()
fish = Fish()
current_typed_word = ""
fishing_start_time = time.time()
font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
background = Scenario()
boat = Boat()
fisherman = Fisherman()
all_sprites.add(boat, fisherman)

# Main Loop
running = True
while running:
    if game_state == "main_menu":
        running = main_menu_screen()
    elif game_state == "difficulty_select":
        running = difficulty_select_screen()
    elif game_state == "playing":
        running = game_loop()
    elif game_state == "upgrades":
        running = upgrades_screen()

    pygame.display.flip()

# Quit Pygame
pygame.quit()
