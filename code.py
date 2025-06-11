import board
from neopixel import NeoPixel
from keypad import ShiftRegisterKeys
from face_invaders.face_invaders import FaceInvadersGame

# Show display
display = board.DISPLAY
display.root_group.hidden = False

# Turn off display auto refresh
display.auto_refresh = False

# Turn off PyBadge LC led
led = NeoPixel(board.NEOPIXEL, 1, auto_write=True)
led.brightness = 0.0

# Create instance of Asteroids game
face_invaders_game = FaceInvadersGame(board)

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
            face_invaders_game.b_button_event(pressed=key.pressed)

        # A button event
        elif key.key_number == 1:
            face_invaders_game.a_button_event(pressed=key.pressed)

        # Start button event
        elif key.key_number == 2:
            face_invaders_game.start_button_event(pressed=key.pressed)

        # Select button event
        elif key.key_number == 3:
            face_invaders_game.select_button_event(pressed=key.pressed)

        # Right button event
        elif key.key_number == 4:
            face_invaders_game.right_button_event(pressed=key.pressed)

        # Down button event
        elif key.key_number == 5:
            face_invaders_game.down_button_event(pressed=key.pressed)

        # Up button event
        elif key.key_number == 6:
            face_invaders_game.up_button_event(pressed=key.pressed)

        # Left button event
        elif key.key_number == 7:
            face_invaders_game.left_button_event(pressed=key.pressed)

    # Tick game forward and refresh display
    face_invaders_game.tick()
    display.refresh()
