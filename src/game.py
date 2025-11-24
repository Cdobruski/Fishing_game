import pygame
import time
import csv
from src.settings import *
from src.sprites import *

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Type Fishing")
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
        self.current_session_score = 0
        self.total_typing_time = 0.0
        self.run_history = []
        self.total_fish_caught = 0
        self.total_money_earned = 0
        self.session_start_time = time.time()
        self.load_data()
        self.all_sprites = pygame.sprite.Group()
        self.popups = pygame.sprite.Group()
        self.background = Scenario("river", "day")
        self.water = Water()
        self.boat = Boat(self.boat_level)
        self.fisherman = Fisherman(self.rod_level, self.boat)
        self.fish = Fish(self.difficulty, self.float_level)
        self.all_sprites.add(self.boat, self.fisherman)
        self.current_typed_word = ""
        self.word_start_time = time.time()
        self.init_menus()

    def init_menus(self):
        # Area Select
        try:
            self.area_bg = pygame.image.load(resource_path("images/cenario/menu_cenario.png")).convert()
            self.area_bg = pygame.transform.scale(self.area_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load area background: {e}")
            self.area_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.area_bg.fill((0, 0, 0))

        # Position buttons nicely
        button_width = 300
        button_height = 200
        # Rio button (left side)
        self.btn_rio = Button(SCREEN_WIDTH//3, SCREEN_HEIGHT//2, button_width, button_height, "", image_path="images/cenario/quadro_cenario_rio.png")
        # Praia button (right side)
        self.btn_praia = Button(2*SCREEN_WIDTH//3, SCREEN_HEIGHT//2, button_width, button_height, "", image_path="images/cenario/quadro_cenario_praia.png")
        # Lake button (text based, using default image)
        self.btn_lago = Button(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 150, button_width, 60, "Lago", font_size=30)

        # Difficulty Select
        try:
            self.diff_bg = pygame.image.load(resource_path("images/cenario/menu_dificuldade.png")).convert()
            self.diff_bg = pygame.transform.scale(self.diff_bg, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Could not load difficulty background: {e}")
            self.diff_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            self.diff_bg.fill((0, 0, 0))

        # Store buttons (creating them here so we can reuse them, but text might need update)
        # Adjusted positions to be closer and at the bottom
        button_width = 661
        button_height = 60
        center_x = 393

        self.btn_buy_boat = Button(center_x, 350, button_width, button_height, "")
        self.btn_buy_rod = Button(center_x, 420, button_width, button_height, "")
        self.btn_buy_float = Button(center_x, 490, button_width, button_height, "")
        self.btn_store_back = Button(center_x, 560, 200, 40, "Voltar", font_size=30)
        self.update_store_buttons()

    def update_store_buttons(self):
        # Update Boat Button
        if self.boat_level >= 3:
            boat_text = "Barco Maximo"
        else:
            boat_text = f"Barco Nvl {self.boat_level} -> {self.boat_level+1} (R${self.boat_level*10})"
        self.btn_buy_boat.update_text(boat_text)

        # Update Rod Button
        if self.rod_level >= 3:
            rod_text = "Vara Maxima"
        else:
            rod_text = f"Vara Nvl {self.rod_level} -> {self.rod_level+1} (R${self.rod_level*10})"
        self.btn_buy_rod.update_text(rod_text)

        # Update Float Button
        if self.float_level >= 4:
            float_text = "Boia Maxima"
        else:
            float_text = f"Boia Nvl {self.float_level} -> {self.float_level+1} (R${self.float_level*10})"
        self.btn_buy_float.update_text(float_text)

    def load_data(self):
        try:
            with open('player_data.csv', 'r') as file:
                reader = csv.reader(file)
                player_header = next(reader)
                player_data = next(reader)

                data_map = {header: value for header, value in zip(player_header, player_data)}

                self.money = int(data_map.get('money', 0))
                self.boat_level = int(data_map.get('boat_level', 1))
                self.rod_level = int(data_map.get('rod_level', 1))
                self.float_level = int(data_map.get('float_level', 1))
                self.total_fish_caught = int(data_map.get('total_fish_caught', 0))
                self.total_money_earned = int(data_map.get('total_money_earned', 0))

                history_header = next(reader)
                for row in reader:
                    run_data = {
                        "timestamp": float(row[0]),
                        "difficulty": row[1],
                        "score": int(row[2]),
                        "average_typing_time": float(row[3]),
                        "play_time": float(row[4]) if len(row) > 4 else 0
                    }
                    self.run_history.append(run_data)
        except (FileNotFoundError, StopIteration):
            self.money = 0
            self.boat_level = 1
            self.rod_level = 1
            self.float_level = 1
            self.total_fish_caught = 0
            self.total_money_earned = 0
            self.run_history = []

    def save_data(self):
        with open('player_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            player_header = ['money', 'boat_level', 'rod_level', 'float_level', 'total_fish_caught', 'total_money_earned']
            player_data = [self.money, self.boat_level, self.rod_level, self.float_level, self.total_fish_caught, self.total_money_earned]
            writer.writerow(player_header)
            writer.writerow(player_data)

            history_header = ['timestamp', 'difficulty', 'score', 'average_typing_time', 'play_time']
            writer.writerow(history_header)
            for run in self.run_history:
                writer.writerow([run['timestamp'], run['difficulty'], run['score'], run['average_typing_time'], run.get('play_time', 0)])

    def append_run_data(self):
        play_time = time.time() - self.session_start_time
        if self.words_caught_count > 0:
            average_typing_time = self.total_typing_time / self.words_caught_count
            average_typing_speed = sum(len(word) for word in self.fish.words_history) / self.total_typing_time if self.total_typing_time > 0 else 0
        else:
            average_typing_time = 0
            average_typing_speed = 0

        run_data = {
            "timestamp": time.time(),
            "difficulty": self.difficulty,
            "score": self.current_session_score,
            "average_typing_time": average_typing_time,
            "average_typing_speed": average_typing_speed,
            "play_time": play_time
        }
        self.run_history.append(run_data)

    def calculate_averages(self):
        if not self.run_history:
            return 0, 0
        total_score = sum(run['score'] for run in self.run_history)
        total_play_time = sum(run['play_time'] for run in self.run_history)
        average_score = total_score / len(self.run_history)
        average_play_time = total_play_time / len(self.run_history)
        return average_score, average_play_time

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
            elif self.game_state == "fish_caught":
                running = self.fish_caught_screen()
            elif self.game_state == "reeling_animation":
                running = self.reeling_animation_screen()
            elif self.game_state == "conclusion":
                running = self.conclusion_screen()

            pygame.display.flip()

        pygame.quit()

    def fish_caught_screen(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(self.background.image, self.background.rect)
        self.screen.blit(self.water.image, self.water.rect)
        self.screen.blit(overlay, (0, 0))

        # Fish animation
        if not hasattr(self, 'fish_animation_start_time'):
            self.fish_animation_start_time = time.time()

        animation_duration = 2.0 # seconds
        elapsed_time = time.time() - self.fish_animation_start_time

        if elapsed_time < animation_duration:
            scale = 1.0 + (elapsed_time / animation_duration) * 2.0
            new_width = int(self.fish.image.get_width() * scale)
            new_height = int(self.fish.image.get_height() * scale)
            scaled_fish = pygame.transform.scale(self.fish.image, (new_width, new_height))
            scaled_rect = scaled_fish.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            self.screen.blit(scaled_fish, scaled_rect)

            font = pygame.font.SysFont(FONT_NAME, 40)
            text = font.render(self.fish.name, True, WHITE)
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, scaled_rect.bottom + 30))
            self.screen.blit(text, text_rect)
        else:
            del self.fish_animation_start_time
            self.fisherman.state = "reeling"
            self.game_state = "reeling_animation"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def reeling_animation_screen(self):
        self.screen.blit(self.background.image, self.background.rect)
        self.screen.blit(self.water.image, self.water.rect)
        self.all_sprites.update()
        self.all_sprites.draw(self.screen)

        if self.fisherman.animation_complete:
            self.game_state = "conclusion"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        return True

    def conclusion_screen(self):
        self.screen.fill((0, 0, 0))
        font = pygame.font.SysFont(FONT_NAME, 40)
        title_text = font.render("Fim de Jogo", True, WHITE)

        average_score, average_play_time = self.calculate_averages()

        score_text = font.render(f"Pontuação: {self.last_score}", True, WHITE)
        money_text = font.render(f"Dinheiro: R${self.last_money}", True, WHITE)
        total_fish_text = font.render(f"Total de peixes pescados: {self.total_fish_caught}", True, WHITE)
        avg_score_text = font.render(f"Pontuação média: {average_score:.2f}", True, WHITE)
        avg_play_time_text = font.render(f"Tempo médio de jogo: {average_play_time:.2f}s", True, WHITE)

        continue_text = font.render("Pressione qualquer tecla para continuar", True, WHITE)

        self.screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 50))
        self.screen.blit(score_text, (50, 150))
        self.screen.blit(money_text, (50, 200))
        self.screen.blit(total_fish_text, (50, 250))
        self.screen.blit(avg_score_text, (50, 300))
        self.screen.blit(avg_play_time_text, (50, 350))
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
        self.screen.blit(self.diff_bg, (0, 0))
        title_font = pygame.font.SysFont(FONT_NAME, 70)
        option_font = pygame.font.SysFont(FONT_NAME, 50)

        # title_text = title_font.render("Selecione a Dificuldade", True, WHITE)
        easy_text = option_font.render("Pressione F para Fácil", True, WHITE)
        medium_text = option_font.render("Pressione M para Médio", True, WHITE)
        hard_text = option_font.render("Pressione D para Difícil", True, WHITE)
        back_text = option_font.render("Pressione V para Voltar", True, WHITE)

        # self.screen.blit(title_text, (SCREEN_WIDTH/2 - title_text.get_width()/2, 100))
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
        self.screen.blit(self.area_bg, (0, 0))

        # Draw buttons
        self.btn_rio.draw(self.screen)

        if self.boat_level >= 3:
            self.btn_praia.draw(self.screen)

        if self.boat_level >= 2:
            self.btn_lago.draw(self.screen)

        font = pygame.font.SysFont(FONT_NAME, 50)
        back_text = font.render("Pressione V para Voltar", True, WHITE)
        self.screen.blit(back_text, (SCREEN_WIDTH/2 - back_text.get_width()/2, 550))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            # Handle button clicks
            if self.btn_rio.is_clicked(event):
                self.background = Scenario("river")
                self.game_state = "difficulty_select"

            if self.boat_level >= 3 and self.btn_praia.is_clicked(event):
                self.background = Scenario("beach")
                self.game_state = "difficulty_select"

            if self.boat_level >= 2 and self.btn_lago.is_clicked(event):
                self.background = Scenario("lake")
                self.game_state = "difficulty_select"

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

    def store_screen(self):
        store_background = pygame.image.load(resource_path("images/Store/menu_venda.png")).convert()
        store_background = pygame.transform.scale(store_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(store_background, (0, 0))
        font = pygame.font.SysFont(FONT_NAME, 40)

        self.btn_buy_boat.draw(self.screen)
        self.btn_buy_rod.draw(self.screen)
        self.btn_buy_float.draw(self.screen)
        self.btn_store_back.draw(self.screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if self.btn_store_back.is_clicked(event):
                self.game_state = "main_menu"

            if self.btn_buy_boat.is_clicked(event):
                if self.money >= self.boat_level * 10 and self.boat_level < 3:
                    self.money -= self.boat_level * 10
                    self.boat_level += 1
                    self.boat.boat_level = self.boat_level
                    self.boat.load_image()
                    self.save_data()
                    self.update_store_buttons()

            if self.btn_buy_rod.is_clicked(event):
                if self.money >= self.rod_level * 10 and self.rod_level < 3:
                    self.money -= self.rod_level * 10
                    self.rod_level += 1
                    self.fisherman.rod_level = self.rod_level
                    self.fisherman.load_image()
                    self.rod.rod_level = self.rod_level
                    self.rod.load_image()
                    self.save_data()
                    self.update_store_buttons()

            if self.btn_buy_float.is_clicked(event):
                if self.money >= self.float_level * 10 and self.float_level < 4:
                    self.money -= self.float_level * 10
                    self.float_level += 1
                    self.float.float_level = self.float_level
                    self.float.load_image()
                    self.save_data()
                    self.update_store_buttons()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_v:
                    self.game_state = "main_menu"
        return True

    def reset_game(self):
        self.words_caught_count = 0
        self.current_session_score = 0
        self.total_typing_time = 0.0
        self.fish.kill()
        self.fish = Fish(self.difficulty, self.float_level)
        self.all_sprites.add(self.fish)
        self.current_typed_word = ""
        self.fishing_start_time = time.time()
        self.word_start_time = time.time()
        self.fisherman.reset_animation()

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

                        word_time = time.time() - self.word_start_time
                        self.total_typing_time += word_time
                        points = max(1, 10 - int(word_time)) * len(self.fish.word)
                        self.current_session_score += points
                        popup = ScorePopup(points, self.fish.rect.centerx, self.fish.rect.centery)
                        self.popups.add(popup)

                        if self.words_caught_count >= words_needed:
                            money_earned = RARITY_REWARDS[self.fish.rarity] * settings.get("money_multiplier", 1)
                            self.money += money_earned
                            self.total_money_earned += money_earned
                            self.total_fish_caught += 1
                            self.last_score = self.current_session_score
                            self.last_money = money_earned
                            self.append_run_data()
                            self.save_data()
                            self.fisherman.state = "hooked"
                            self.game_state = "fish_caught"
                        else:
                            self.fish.new_word(self.difficulty)
                            self.word_start_time = time.time()
                        self.current_typed_word = ""
                else:
                    self.current_typed_word += event.unicode

        time_elapsed = time.time() - self.fishing_start_time
        if time_elapsed > time_limit:
            self.last_score = self.current_session_score
            self.last_money = 0
            self.append_run_data()
            self.save_data()
            self.game_state = "conclusion"

        # Update
        self.all_sprites.update()
        self.popups.update()

        # Drawing code here
        self.screen.blit(self.background.image, self.background.rect)
        self.screen.blit(self.boat.image, self.boat.rect)
        self.fish.draw(self.screen, self.current_typed_word)
        self.screen.blit(self.water.image, self.water.rect)
        self.screen.blit(self.fisherman.image, self.fisherman.rect)
        self.popups.draw(self.screen)
        self.fish.draw_progress_bar(self.screen, self.words_caught_count, words_needed)

        typed_text_surface = self.font.render(self.current_typed_word, True, WHITE)
        self.screen.blit(typed_text_surface, (10, 10))

        score_surface = self.font.render(f"Pontuação: {self.current_session_score}", True, WHITE)
        self.screen.blit(score_surface, (SCREEN_WIDTH - score_surface.get_width() - 10, 10))

        time_left = time_limit - time_elapsed
        timer_surface = self.font.render(f"Tempo: {int(time_left)}s", True, WHITE)
        self.screen.blit(timer_surface, (SCREEN_WIDTH/2 - timer_surface.get_width()/2, 10))

        return True
