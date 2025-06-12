"""Constants used throughout the Face Invaders game."""

class GameState:
    """Enumerates the possible game states as integers."""

    START_MENU = 0
    ACTIVE_GAME = 1
    OPTIONS_MENU = 2
    CONTROLS_MENU = 3
    GAME_OVER = 4
    SCORE_INPUT = 5
    HIGH_SCORES = 6


# Game settings
HIGH_SCORES_FNAME = 'face_invaders/scores.json'
NUM_HIGH_SCORES = 5
MAX_LIVES = 3

# Points awarded for destroying faces
FACE_POINTS = {
    1: 20,  # Large face
    2: 50,  # Medium face
    3: 100  # Small face
}

# Player input characters
CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

# Timing constants
SHIP_RESET_SECONDS = 2.5
GAME_OVER_SECONDS = 2
CREATE_BULLET_SECONDS = 0.25
