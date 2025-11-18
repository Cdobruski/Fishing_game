import pygame
import time
import csv
from src.settings import *
from src.sprites import *
from src.settings import resource_path

class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
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
        self.main_menu_background = pygame.image.load(resource_path("images/cenario/menu.png")).convert()
        self.main_menu_background = pygame.transform.scale(self.main_menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.water = Water()
        self.boat = Boat(self.boat_level)
        self.fisherman = Fisherman(self.rod_level, self.boat)
        self.fish = Fish(self.difficulty, self.float_level)
        self.all_sprites.add(self.boat, self.fisherman)
        self.current_typed_word = ""
        self.word_start_time = time.time()
        self.load_sounds()
        self.play_music()

    def load_sounds(self):
        self.sounds = {
            "button": pygame.mixer.Sound(resource_path("audio/Botão.mp3")),
            "catch": pygame.mixer.Sound(resource_path("audio/Som de pesca concluida.mp3")),
            "fail": pygame.mixer.Sound(resource_path("audio/falha_pesca.mp3")),
            "cast": pygame.mixer.Sound(resource_path("audio/jogou a vara.mp3")),
            "vendor": pygame.mixer.Sound(resource_path("audio/Som vendedor 1.mp3")),
        }

    def play_music(self):
        pygame.mixer.music.stop()
        area_name_map = {
            "river": "Rio",
            "beach": "Praia"
        }
        area_name = area_name_map.get(self.background.area, "Rio")

        music_map = {
            "main_menu": "audio/Rio_dia.mp3",
            "playing": f"audio/{area_name}_{self.background.time_of_day}.mp3"
        }
        music_file = music_map.get(self.game_state, "audio/Rio_dia.mp3")
        try:
            pygame.mixer.music.load(resource_path(music_file))
            pygame.mixer.music.play(-1)
        except pygame.error:
            print(f"Could not load music file: {music_file}")

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
            elif self.game_state == "store":
                running = self.store_screen()
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
                self.play_music()
        return True

    def main_menu_screen(self):
        self.screen.blit(self.main_menu_background, (0, 0))
        option_font = pygame.font.SysFont(FONT_NAME, 50)

        play_text = option_font.render("Jogar", True, WHITE)
        store_text = option_font.render("Loja", True, WHITE)
        quit_text = option_font.render("Sair", True, WHITE)

        self.screen.blit(play_text, (SCREEN_WIDTH/2 - play_text.get_width()/2, 290))
        self.screen.blit(store_text, (SCREEN_WIDTH/2 - store_text.get_width()/2, 390))
        self.screen.blit(quit_text, (SCREEN_WIDTH/2 - quit_text.get_width()/2, 490))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.sounds["button"].play()
                if event.key == pygame.K_j:
                    self.game_state = "area_select"
                elif event.key == pygame.K_l:
                    self.game_state = "store"
                    self.sounds["vendor"].play()
                    pygame.mixer.music.stop()
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
                self.sounds["button"].play()
                if event.key in [pygame.K_f, pygame.K_m, pygame.K_d]:
                    if event.key == pygame.K_f:
                        self.difficulty = "easy"
                    elif event.key == pygame.K_m:
                        self.difficulty = "medium"
                    elif event.key == pygame.K_d:
                        self.difficulty = "hard"
                    self.reset_game()
                    self.game_state = "playing"
                    self.play_music()
                elif event.key == pygame.K_v:
                    self.game_state = "main_menu"
                    self.play_music()
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
            beach_text = option_font.render("Pressione P para Praia", True, WHITE)
            self.screen.blit(beach_text, (SCREEN_WIDTH/2 - beach_text.get_width()/2, 350))

        back_text = option_font.render("Pressione V para Voltar", True, WHITE)
        self.screen.blit(back_text, (SCREEN_WIDTH/2 - back_text.get_width()/2, 550))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                self.sounds["button"].play()
                if event.key == pygame.K_r:
                    self.background = Scenario("river")
                    self.game_state = "difficulty_select"
                elif event.key == pygame.K_p and self.boat_level >= 2:
                    self.background = Scenario("beach")
                    self.game_state = "difficulty_select"
                elif event.key == pygame.K_v:
                    self.background = Scenario("river", "day")
                    self.game_state = "main_menu"
        return True

    def store_screen(self):
        store_background = pygame.image.load(resource_path("images/misc/store_background.png")).convert()
        store_background = pygame.transform.scale(store_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.screen.blit(store_background, (0, 0))
        font = pygame.font.SysFont(FONT_NAME, 40)

        # --- Texts ---
        title_text = font.render("Loja", True, WHITE)
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
                        self.sounds["vendor"].play()
                elif event.key == pygame.K_2:
                    if self.money >= self.rod_level * 10 and self.rod_level < 3:
                        self.money -= self.rod_level * 10
                        self.rod_level += 1
                        self.fisherman.rod_level = self.rod_level
                        self.fisherman.load_image()
                        self.rod.rod_level = self.rod_level
                        self.rod.load_image()
                        self.save_data()
                        self.sounds["vendor"].play()
                elif event.key == pygame.K_3:
                    if self.money >= self.float_level * 10 and self.float_level < 4:
                        self.money -= self.float_level * 10
                        self.float_level += 1
                        self.float.float_level = self.float_level
                        self.float.load_image()
                        self.save_data()
                        self.sounds["vendor"].play()
                elif event.key == pygame.K_v:
                    self.game_state = "main_menu"
                    self.play_music()
        return True

    def reset_game(self):
        self.sounds["cast"].play()
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
                            self.sounds["catch"].play()
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
            self.sounds["fail"].play()
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
