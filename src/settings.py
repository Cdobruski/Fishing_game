import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# --- Game constants ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)
FONT_NAME = "arial"
FONT_SIZE = 30

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
WATERLINE_Y = 240

# --- Difficulty Settings ---
DIFFICULTY_SETTINGS = {
    "easy": {"words_to_catch": 5, "time_limit": 60, "score_multiplier": 1, "money_multiplier": 1},
    "medium": {"words_to_catch": 7, "time_limit": 45, "score_multiplier": 2, "money_multiplier": 2},
    "hard": {"words_to_catch": 10, "time_limit": 30, "score_multiplier": 3, "money_multiplier": 3}
}

# --- Game assets ---
WORDS_EASY = ["sol", "mar", "rio", "peixe", "barco", "isca", "rede", "agua", "lua", "ceu", "sal", "luz", "cor", "ver", "ler", "fim", "bom", "mau", "rei", "lei", "pai", "mae", "filho", "irma", "amor", "paz", "vida"]
WORDS_MEDIUM = ["pescador", "anzol", "oceano", "praia", "areia", "vento", "nuvem", "onda", "barranco", "castelo", "floresta", "montanha", "cachoeira", "orvalho", "neblina", "tempestade", "relampago", "trovao", "estrela", "planeta", "galaxia", "universo", "natureza", "animal", "planta", "flor", "fruta"]
WORDS_HARD = ["horizonte", "profundeza", "tempestade", "maritimo", "nadadeira", "escama", "pescaria", "molinete", "constelacao", "astronomia", "biologia", "geografia", "historia", "filosofia", "literatura", "matematica", "portugues", "psicologia", "sociologia", "tecnologia", "arquitetura", "engenharia", "medicina", "advocacia", "economia", "politica"]
