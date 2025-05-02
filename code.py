import board
from neopixel import NeoPixel
from keypad import ShiftRegisterKeys
from asteroids import AsteroidsGame

# Show display
display = board.DISPLAY
display.root_group.hidden = False

# Turn off PyBadge LC led
led = NeoPixel(board.NEOPIXEL, 1, auto_write=True)
led.brightness = 0.0

# Create instance of Asteroids game
asteroids_game = AsteroidsGame(board)

# Pybadge key input object
keys = ShiftRegisterKeys(
    clock=board.BUTTON_CLOCK,
    data=board.BUTTON_OUT,
    latch=board.BUTTON_LATCH,
    key_count=8,
    value_when_pressed=True,
    max_events=2
)

# Main processing loop
while True:

    # Get user button input
    key = keys.events.get()

    # Process button event if one exits
    if key:

        # B button event
        if key.key_number == 0:
            asteroids_game.b_button_event(pressed=key.pressed)

        # A button event
        elif key.key_number == 1:
            asteroids_game.a_button_event(pressed=key.pressed)

        # Starte button event
        elif key.key_number == 2:
            asteroids_game.start_button_event(pressed=key.pressed)

        # Select button event
        elif key.key_number == 3:
            asteroids_game.select_button_event(pressed=key.pressed)

        # Right button event
        elif key.key_number == 4:
            asteroids_game.right_button_event(pressed=key.pressed)

        # Down button event
        elif key.key_number == 5:
            asteroids_game.down_button_event(pressed=key.pressed)

        # Up button event
        elif key.key_number == 6:
            asteroids_game.up_button_event(pressed=key.pressed)

        # Left button event
        elif key.key_number == 7:
            asteroids_game.left_button_event(pressed=key.pressed)

    # Call the game tick function
    asteroids_game.tick()
