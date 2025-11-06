import pygame
import time
import csv
from src.settings import *
from src.sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Typing Fishing Game")
        self.font = pygame.font.SysFont(FONT_NAME, FONT_SIZE)
        self.game_state = "main_menu"
        self.difficulty = "easy"
        self.score = 0
        self.money = 0
        self.boat_level = 1
        self.rod_level = 1
        self.float_level = 1
        self.words_caught_count = 0
        self.fishing_start_time = time.time()
        self.last_score = 0
        self.last_money = 0
        self.load_data()
        self.all_sprites = pygame.sprite.Group()
        self.background = Scenario("river", "day")
        self.water = Water()
        self.boat = Boat(self.boat_level)
        self.fisherman = Fisherman(self.rod_level, self.boat)
        self.fish = Fish(self.difficulty, self.float_level)
        self.all_sprites.add(self.boat, self.fisherman)
        self.current_typed_word = ""

    def load_data(self):
        try:
            with open('player_data.csv', 'r') as file:
                reader = csv.reader(file)
                header = next(reader)
                data = next(reader)
                self.score = int(data[0])
                self.money = int(data[1])
                self.boat_level = int(data[2])
                self.rod_level = int(data[3])
                self.float_level = int(data[4])
        except (FileNotFoundError, StopIteration):
            self.score = 0
            self.money = 0
            self.boat_level = 1
            self.rod_level = 1
            self.float_level = 1

    def save_data(self):
        with open('player_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['score', 'money', 'boat_level', 'rod_level', 'float_level'])
            writer.writerow([self.score, self.money, self.boat_level, self.rod_level, self.float_level])

    def run(self):
        running = True
        while running:
            if self.game_state == "main_menu":
                running = self.main_menu_screen()
            elif self.game_state == "area_select":
                running = self.area_select_screen()
            elif self.game_state == "difficulty_select":
                running = self.difficulty_select_screen()
            elif self.game_state == "playing":
                running = self.game_loop()
            elif self.game_state == "upgrades":
                running = self.upgrades_screen()
            elif self.game_state == "conclusion":
                running = self.conclusion_screen()

            pygame.display.flip()

        pygame.quit()

    def conclusion_screen(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(FONT_NAME, 50)
        title_text = font.render("Fim de Jogo", True, WHITE)
        score_text = font.render(f"Pontuação: {self.last_score}", True, WHITE)
        money_text = font.render(f"Dinheiro: R${self.last_money}", True, WHITE)
        continue_text = font.render("Pressione qualquer tecla para continuar", True, WHITE)

        self.screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 100))
        self.screen.blit(score_text, (SCREEN_WIDTH/2 - score_text.get_width()/2, 250))
        self.screen.blit(money_text, (SCREEN_WIDTH/2 - money_text.get_width()/2, 350))
        self.screen.blit(continue_text, (SCREEN_WIDTH/2 - continue_text.get_width()/2, 500))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.game_state = "main_menu"
        return True

    def main_menu_screen(self):
        self.screen.blit(self.background.image, self.background.rect)
        title_font = pygame.font.SysFont(FONT_NAME, 70)
        option_font = pygame.font.SysFont(FONT_NAME, 50)

        title_text = title_font.render("Jogo de Pesca com Digitação", True, WHITE)
        play_text = option_font.render("Pressione J para Jogar", True, WHITE)
        upgrades_text = option_font.render("Pressione M para Melhorias", True, WHITE)
        quit_text = option_font.render("Pressione S para Sair", True, WHITE)

        self.screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 100))
        self.screen.blit(play_text, (SCREEN_WIDTH/2 - play_text.get_width()/2, 300))
        self.screen.blit(upgrades_text, (SCREEN_WIDTH/2 - upgrades_text.get_width()/2, 400))
        self.screen.blit(quit_text, (SCREEN_WIDTH/2 - quit_text.get_width()/2, 500))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_j:
                    self.game_state = "area_select"
                elif event.key == pygame.K_m:
                    self.game_state = "upgrades"
                elif event.key == pygame.K_s:
                    return False
        return True

    def difficulty_select_screen(self):
        self.screen.fill((0, 100, 200))
        title_font = pygame.font.SysFont(FONT_NAME, 70)
        option_font = pygame.font.SysFont(FONT_NAME, 50)

        title_text = title_font.render("Selecione a Dificuldade", True, WHITE)
        easy_text = option_font.render("Pressione F para Fácil", True, WHITE)
        medium_text = option_font.render("Pressione M para Médio", True, WHITE)
        hard_text = option_font.render("Pressione D para Difícil", True, WHITE)
        back_text = option_font.render("Pressione V para Voltar", True, WHITE)

        self.screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 100))
        self.screen.blit(easy_text, (SCREEN_WIDTH/2 - easy_text.get_width()/2, 250))
        self.screen.blit(medium_text, (SCREEN_WIDTH/2 - medium_text.get_width()/2, 350))
        self.screen.blit(hard_text, (SCREEN_WIDTH/2 - hard_text.get_width()/2, 450))
        self.screen.blit(back_text, (SCREEN_WIDTH/2 - back_text.get_width()/2, 550))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_f:
                    self.difficulty = "easy"
                    self.reset_game()
                    self.game_state = "playing"
                elif event.key == pygame.K_m:
                    self.difficulty = "medium"
                    self.reset_game()
                    self.game_state = "playing"
                elif event.key == pygame.K_d:
                    self.difficulty = "hard"
                    self.reset_game()
                    self.game_state = "playing"
                elif event.key == pygame.K_v:
                    self.background = Scenario("river", "day")
                    self.game_state = "main_menu"
        return True

    def area_select_screen(self):
        self.screen.fill((0, 100, 200))
        title_font = pygame.font.SysFont(FONT_NAME, 70)
        option_font = pygame.font.SysFont(FONT_NAME, 50)

        title_text = title_font.render("Selecione a Área", True, WHITE)
        river_text = option_font.render("Pressione R para Rio", True, WHITE)

        self.screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 100))
        self.screen.blit(river_text, (SCREEN_WIDTH/2 - river_text.get_width()/2, 250))

        if self.boat_level >= 2:
            lake_text = option_font.render("Pressione L para Lago", True, WHITE)
            self.screen.blit(lake_text, (SCREEN_WIDTH/2 - lake_text.get_width()/2, 350))
        if self.boat_level >= 3:
            beach_text = option_font.render("Pressione P para Praia", True, WHITE)
            self.screen.blit(beach_text, (SCREEN_WIDTH/2 - beach_text.get_width()/2, 450))

        back_text = option_font.render("Pressione V para Voltar", True, WHITE)
        self.screen.blit(back_text, (SCREEN_WIDTH/2 - back_text.get_width()/2, 550))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.background = Scenario("river")
                    self.game_state = "difficulty_select"
                elif event.key == pygame.K_l and self.boat_level >= 2:
                    self.background = Scenario("lake")
                    self.game_state = "difficulty_select"
                elif event.key == pygame.K_p and self.boat_level >= 3:
                    self.background = Scenario("beach")
                    self.game_state = "difficulty_select"
                elif event.key == pygame.K_v:
                    self.game_state = "main_menu"
        return True

    def upgrades_screen(self):
        self.screen.fill((50, 50, 50))
        font = pygame.font.SysFont(FONT_NAME, 40)

        # --- Texts ---
        title_text = font.render("Melhorias", True, WHITE)
        money_text = font.render(f"Dinheiro: R${self.money}", True, WHITE)
        boat_text = font.render(f"Nível do Barco: {self.boat_level} (Custo: R${self.boat_level*10}) - Pressione 1", True, WHITE)
        rod_text = font.render(f"Nível da Vara: {self.rod_level} (Custo: R${self.rod_level*10}) - Pressione 2", True, WHITE)
        float_text = font.render(f"Nível da Boia: {self.float_level} (Custo: R${self.float_level*10}) - Pressione 3", True, WHITE)
        back_text = font.render("Pressione V para Voltar", True, WHITE)

        # --- Blitting ---
        self.screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 50))
        self.screen.blit(money_text, (20, 20))
        self.screen.blit(boat_text, (50, 200))
        self.screen.blit(rod_text, (50, 300))
        self.screen.blit(float_text, (50, 400))
        self.screen.blit(back_text, (50, 500))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    if self.money >= self.boat_level * 10 and self.boat_level < 3:
                        self.money -= self.boat_level * 10
                        self.boat_level += 1
                        self.boat.boat_level = self.boat_level
                        self.boat.load_image()
                        self.save_data()
                elif event.key == pygame.K_2:
                    if self.money >= self.rod_level * 10 and self.rod_level < 3:
                        self.money -= self.rod_level * 10
                        self.rod_level += 1
                        self.fisherman.rod_level = self.rod_level
                        self.fisherman.load_image()
                        self.rod.rod_level = self.rod_level
                        self.rod.load_image()
                        self.save_data()
                elif event.key == pygame.K_3:
                    if self.money >= self.float_level * 10 and self.float_level < 4:
                        self.money -= self.float_level * 10
                        self.float_level += 1
                        self.float.float_level = self.float_level
                        self.float.load_image()
                        self.save_data()
                elif event.key == pygame.K_v:
                    self.game_state = "main_menu"
        return True

    def reset_game(self):
        self.words_caught_count = 0
        self.fish.kill()
        self.fish = Fish(self.difficulty, self.float_level)
        self.all_sprites.add(self.fish)
        self.current_typed_word = ""
        self.fishing_start_time = time.time()

    def game_loop(self):
        settings = DIFFICULTY_SETTINGS[self.difficulty]
        words_needed = settings["words_to_catch"] - (self.rod_level - 1)

        if self.fish.rarity == "legendary":
            words_needed += 5

        time_limit = settings["time_limit"]

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = "main_menu"
                elif event.key == pygame.K_BACKSPACE:
                    self.current_typed_word = self.current_typed_word[:-1]
                elif event.key == pygame.K_RETURN:
                    if self.current_typed_word == self.fish.word:
                        self.words_caught_count += 1
                        if self.words_caught_count >= words_needed:
                            score_earned = RARITY_REWARDS[self.fish.rarity] * settings.get("score_multiplier", 1)
                            money_earned = RARITY_REWARDS[self.fish.rarity] * settings.get("money_multiplier", 1)

                            self.score += score_earned
                            self.money += money_earned
                            self.last_score = score_earned
                            self.last_money = money_earned
                            self.save_data()
                            self.game_state = "conclusion"
                        else:
                            self.fish.new_word(self.difficulty)
                        self.current_typed_word = ""
                else:
                    self.current_typed_word += event.unicode

        time_elapsed = time.time() - self.fishing_start_time
        if time_elapsed > time_limit:
            self.last_score = 0
            self.last_money = 0
            self.game_state = "conclusion"

        # Update
        self.all_sprites.update()

        # Drawing code here
        self.screen.blit(self.background.image, self.background.rect)
        self.screen.blit(self.water.image, self.water.rect)
        self.all_sprites.draw(self.screen)
        self.fish.draw(self.screen, self.current_typed_word)
        self.fish.draw_progress_bar(self.screen, self.words_caught_count, words_needed)

        typed_text_surface = self.font.render(self.current_typed_word, True, WHITE)
        self.screen.blit(typed_text_surface, (10, 10))

        score_surface = self.font.render(f"Pontuação: {self.score}", True, WHITE)
        self.screen.blit(score_surface, (SCREEN_WIDTH - score_surface.get_width() - 10, 10))

        time_left = time_limit - time_elapsed
        timer_surface = self.font.render(f"Tempo: {int(time_left)}s", True, WHITE)
        self.screen.blit(timer_surface, (SCREEN_WIDTH/2 - timer_surface.get_width()/2, 10))

        return True
