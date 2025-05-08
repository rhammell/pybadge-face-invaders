from time import monotonic
from json import load as json_load
from json import dump as json_dump
from random import randrange, choice
from gc import collect as gc_collect
from gc import mem_free
from math import sin, cos, radians, pi, sqrt, atan2, degrees
from adafruit_imageload import load as imageload
from terminalio import FONT
from displayio import Group, TileGrid, OnDiskBitmap, Palette
from digitalio import DigitalInOut
from audiocore import WaveFile
from audioio import AudioOut
from audiomixer import Mixer
from adafruit_display_text import label, bitmap_label
from adafruit_display_shapes.line import Line
from adafruit_display_shapes.triangle import Triangle
from vectorio import Rectangle, Circle


class AsteroidsGame():
    '''
    This class
    '''

    # Game state variables
    STATE_START_MENU = 0
    STATE_ACTIVE_GAME = 1
    STATE_OPTIONS_MENU = 2
    STATE_CONTROLS_MENU = 3
    STATE_GAME_OVER = 4
    STATE_SCORE_INPUT = 5
    STATE_HIGH_SCORES = 6

    # High scores filename
    HIGH_SCORES_FNAME = 'scores.json'

    # Maximum number of saved scores
    NUM_HIGH_SCORES = 5

    # Maximum player lives
    MAX_LIVES = 3

    # Asteroid points
    ASTEROID_POINTS = {
        1: 20,
        2: 50,
        3: 100
    }

    # Player initial characters
    CHARACTERS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    def __init__(self, board):

        # Store board reference
        self.board = board
        
        # Display initialization
        self.display = self.board.DISPLAY
        self.display_center_x = self.display.width // 2
        self.display_center_y = self.display.height // 2

        # Initialize audio system
        self._init_audio()
        gc_collect()

        # Initialize game state variables
        self._init_game_state()
        gc_collect()
        
        # Load resources (images, sounds)
        self._load_game_assets()
        gc_collect()
        
        # Create UI elements and display groups
        self._create_ui_elements()
        gc_collect()
        
        # Create game ship
        self._create_ship_object()
        gc_collect()
        
        # Load high scores
        self.high_scores = self.load_high_scores()

        # Show start menu
        self.start_menu()

    def _init_audio(self):
        """Initialize audio hardware and mixer"""

        # Enable the PyBadge speaker
        speaker_enable = DigitalInOut(self.board.SPEAKER_ENABLE)
        speaker_enable.switch_to_output(value=True)

        # Create audio output object
        self.audio = AudioOut(self.board.SPEAKER, quiescent_value=0)

        # Create audio mixer object
        self.voice_count = 3
        self.mixer = Mixer(
            voice_count=self.voice_count,
            sample_rate=22050,
            channel_count=1,
            bits_per_sample=16,
            samples_signed=True,
            buffer_size=6144
        )
        self.audio.play(self.mixer)

    def _init_game_state(self):
        """Initialize game state variables"""

        # Set and apply initial brightness
        self.brightness = 100
        self.set_brightness()
        
        # Set and apply initial volume
        self.volume = 100
        self.set_volume()
        
        # Initialize game object tracking lists
        self.asteroids = []
        self.particles = []
        self.bullets = []
        
        # Game current level
        self.level = 1
        
        # Current player lives
        self.lives = AsteroidsGame.MAX_LIVES
        
        # Current game score
        self.score = 0
        
        # Initialize game state variables
        self.current_state = None
        self.prev_state = None
        
        # Time of last game tick used to calculate delta time
        self.last_tick_time = None
        
        # Track ship hit time
        self.ship_hit_time = None
        self.ship_reset_seconds = 2.5
        
        # Track game over pause time
        self.game_over_time = None
        self.game_over_seconds = 2
        
        # Track bullet create time
        self.create_bullet_time = None
        self.create_bullet_seconds = 0.25

    def _load_game_assets(self):
        """Load all game assets (sounds, images, sprites)"""

        # Load game sound effects and define audio channel
        self.sounds = {
            'continue': (2, WaveFile(open('snds/continue.wav','rb'))),
            'game_over': (2, WaveFile(open('snds/game_over.wav','rb'))),
            'new_ship': (2, WaveFile(open('snds/new_ship.wav','rb'))),
            'bullet': (0, WaveFile(open('snds/bullet.wav','rb'))),
            'click': (0, WaveFile(open('snds/click.wav','rb'))),
            'ship_thrust': (0, WaveFile(open('snds/ship_thrust.wav','rb'))),
            'ship_explosion': (1, WaveFile(open('snds/ship_explosion.wav','rb'))),
            'explosion_small': (1, WaveFile(open('snds/asteroid_explosion_small.wav','rb'))),
            'explosion_medium': (1, WaveFile(open('snds/asteroid_explosion_medium.wav','rb'))),
            'explosion_large': (1, WaveFile(open('snds/asteroid_explosion_large.wav','rb')))
        }

        # Load background image
        self.background_bitmap = OnDiskBitmap('img/background.bmp')
        self.background_pallete = self.background_bitmap.pixel_shader

        # Load logo image
        self.logo_bitmap = OnDiskBitmap('img/logo.bmp')
        self.logo_pallete = self.logo_bitmap.pixel_shader
        self.logo_pallete.make_transparent(0)
        
        # Load player lives sprite
        self.ship_small_bitmap = OnDiskBitmap('img/ship_small.bmp')
        self.ship_small_pallette = self.ship_small_bitmap.pixel_shader
        self.ship_small_pallette.make_transparent(0)
        self.ship_small_tile_width = self.ship_small_bitmap.width
        self.ship_small_tile_height = self.ship_small_bitmap.height

        # Load ship sprites
        self.ships_bitmap, self.ships_pallette = imageload('img/ships.bmp')
        self.ships_pallette.make_transparent(0)
        self.ships_tile_width = 20
        self.ships_tile_height = 20
        
        # Load large asteroid sprites
        self.asteroids_large_bitmap, self.asteroids_large_pallette = imageload('img/face_large.bmp')
        self.asteroids_large_pallette.make_transparent(0)
        self.asteroids_large_tile_width = 40
        self.asteroids_large_tile_height = 48

        # Load medium asteroid sprites
        self.asteroids_medium_bitmap, self.asteroids_medium_pallette = imageload('img/face_medium.bmp')
        self.asteroids_medium_pallette.make_transparent(0)
        self.asteroids_medium_tile_width = 30
        self.asteroids_medium_tile_height = 36

        # Load small asteroid sprites
        self.asteroids_small_bitmap, self.asteroids_small_pallette = imageload('img/face_small.bmp')
        self.asteroids_small_pallette.make_transparent(0)
        self.asteroids_small_tile_width = 20
        self.asteroids_small_tile_height = 24
        
        # Palette colors used for display objects
        self.palette = Palette(2)
        self.palette[0] = 0xEEEEEE
        self.palette[1] = 0x000000

    def _create_ui_elements(self):
        """Create all UI elements and display groups"""

        # Set up main display group
        self.main_group = Group()
        self.display.root_group = self.main_group

        # Background display group
        self.background_group = Group()
        self.main_group.append(self.background_group)

        # Display background image
        self.background_group.append(TileGrid(
            self.background_bitmap,
            pixel_shader=self.background_pallete
        ))
        
        # Game objects display group
        self.game_group = Group()
        self.main_group.append(self.game_group)
        
        # Create and initialize all UI groups (start menu, options, etc)
        self._create_start_menu()
        self._create_game_ui()
        self._create_game_over_ui()
        self._create_score_input_ui()
        self._create_high_scores_ui()
        self._create_options_menu()
        self._create_controls_menu()

    def _create_start_menu(self):
        """Create start menu UI elements"""

        # Start menu display group and hide
        self.start_menu_group = Group()
        self.main_group.append(self.start_menu_group)
        self.start_menu_group.hidden = True

        # Create start menu text and hide display group
        self.start_menu_group.append(bitmap_label.Label(
            FONT,
            text='Press A to Start',
            color=self.palette[0],
            anchor_point=(0.5, 1.0),
            anchored_position=(self.display_center_x, self.display.height-5)
        ))
        self.start_menu_group.append(TileGrid(
            self.logo_bitmap,
            pixel_shader=self.logo_pallete,
            x=self.display_center_x-self.logo_bitmap.width//2,
            y=self.display_center_y-self.logo_bitmap.height//2-10
        ))

    def _create_game_ui(self):
        """ Create game user interface elements """

        # UI display group and hide
        self.ui_group = Group()
        self.main_group.append(self.ui_group)
        self.ui_group.hidden = True

        # Create game UI elements and hide display group
        self.score_text = label.Label(
            FONT,
            text='0',
            color=self.palette[0],
            anchor_point=(1.0, 0.0),
            anchored_position=(self.display.width-3, 3)
        )
        self.ui_group.append(self.score_text)
        self.lives_tilegrids = []
        for i in range(3):
            live_tilegrid = TileGrid(
                self.ship_small_bitmap,
                pixel_shader=self.ship_small_pallette,
                tile_width=self.ship_small_tile_width,
                tile_height=self.ship_small_tile_height,
                x = 10 * i,
                y = 1
            )
            self.lives_tilegrids.append(live_tilegrid)
            self.ui_group.append(live_tilegrid)


    def _create_game_over_ui(self):
        """ Create game over user interface elements """

        # Game over display group and hide
        self.game_over_group = Group()
        self.main_group.append(self.game_over_group)
        self.game_over_group.hidden = True

        # Crate game over menu text
        self.game_over_text_group =Group()
        self.game_over_text_group.append(bitmap_label.Label(
            FONT,
            text='Press A to Continue',
            color=self.palette[0],
            anchor_point=(0.5, 1.0),
            anchored_position=(self.display_center_x, self.display.height-5)
        ))
        self.game_over_group.append(bitmap_label.Label(
            FONT,
            text='GAME OVER',
            color=self.palette[0],
            scale=2,
            anchor_point=(0.5, 0.5),
            anchored_position=(self.display_center_x, self.display_center_y-5)
        ))
        self.game_over_group.append(self.game_over_text_group)
        self.game_over_text_group.hidden = True

    def _create_score_input_ui(self):
        """ Create score input user interface elements """

        # Score entry display group and hide
        self.score_input_group = Group()
        self.main_group.append(self.score_input_group)
        self.score_input_group.hidden = True

        # Create score entry text elements
        self.score_input_group.append(bitmap_label.Label(
            FONT,
            text='New High Score!',
            color=self.palette[0],
            anchor_point=(0.5, 0.0),
            anchored_position=(self.display_center_x, 5)
        ))
        self.score_input_group.append( bitmap_label.Label(
            FONT,
            text='Enter player intials:',
            color=self.palette[0],
            anchor_point=(0.5, 0.0),
            anchored_position=(self.display_center_x, 21)
        ))
        self.score_input_group.append(bitmap_label.Label(
            FONT,
            text='Press A to Confirm',
            color=self.palette[0],
            anchor_point=(0.5, 1.0),
            anchored_position=(self.display_center_x, self.display.height-5)
        ))

        # Create score entry initials inputs
        self.num_initials = 3
        self.initial_inputs = []
        self.initial_spacing = 22
        for i in range(self.num_initials):
            initial_input = label.Label(
                FONT,
                text='_',
                color=self.palette[0],
                scale=2,
                anchor_point=(0.5, 0),
                anchored_position=(self.display_center_x - self.initial_spacing + i * self.initial_spacing, self.display_center_y-5)
            )
            self.score_input_group.append(initial_input)
            self.initial_inputs.append(initial_input)

        # Create initials cursor
        self.initials_cursor_group = Group(y=52)
        self.score_input_group.append(self.initials_cursor_group)
        self.initials_cursor_group.append(Triangle(0, 5, 4, 0, 8, 5, outline=self.palette[0]))
        self.initials_cursor_group.append(Triangle(0, 33, 4, 38, 8, 33, outline=self.palette[0]))
        self.current_initial = 0
        self.update_initials_cursor()

    def _create_high_scores_ui(self):
        """ Create high score interface elements """

        # High scores display group and hide
        self.high_scores_group = Group()
        self.main_group.append(self.high_scores_group)
        self.high_scores_group.hidden = True

        # Create high scores title and text
        self.high_scores_group.append(bitmap_label.Label(
            FONT,
            text='High Scores',
            color=self.palette[0],
            anchor_point=(0.5, 0.0),
            anchored_position=(self.display_center_x, 10)
        ))
        self.high_scores_group.append(bitmap_label.Label(
            FONT,
            text='Press A to Continue',
            color=self.palette[0],
            anchor_point=(0.5, 1.0),
            anchored_position=(self.display_center_x, self.display.height-5)
        ))

        # Create high scores table elements
        self.high_scores_names = []
        self.high_scores_numbers = []
        for i in range(AsteroidsGame.NUM_HIGH_SCORES):
            # Score rank
            self.high_scores_group.append(label.Label(
                FONT,
                text=str(i+1),
                color=self.palette[0],
                anchor_point=(1.0, 0.0),
                anchored_position=(self.display_center_x-35, 30 + i*13)
            ))

            # Score player initials
            score_name = label.Label(
                FONT,
                text="-",
                color=self.palette[0],
                anchor_point=(0.0, 0.0),
                anchored_position=(self.display_center_x-25, 30 + i*13)
            )
            self.high_scores_group.append(score_name)
            self.high_scores_names.append(score_name)

            # Score number
            score_number = label.Label(
                FONT,
                text="-",
                color=self.palette[0],
                anchor_point=(1.0, 0.0),
                anchored_position=(self.display_center_x+37, 30 + i*13)
            )
            self.high_scores_group.append(score_number)
            self.high_scores_numbers.append(score_number)

    def _create_options_menu(self):
        """ Create game options interface elements """

        # Options menu display group and hide
        self.options_menu_group = Group()
        self.main_group.append(self.options_menu_group)
        self.options_menu_group.hidden = True

        # Create options menu and title
        self.options_menu_group.append(Rectangle(
            x=10,
            y=10,
            width=self.display.width-20,
            height=self.display.height-20,
            pixel_shader=self.palette,
            color_index=0
        ))
        self.options_menu_group.append(Rectangle(
            x=12,
            y=12,
            width=self.display.width-24,
            height=self.display.height-24,
            pixel_shader=self.palette,
            color_index=1
        ))
        self.options_menu_group.append(bitmap_label.Label(
            FONT,
            text='Options',
            color=self.palette[0],
            anchor_point=(0.5, 0.0),
            anchored_position=(self.display_center_x, 17)
        ))

        # Create list of updatable options
        self.options_y_start = 45
        self.options_spacing = 20
        self.option_values = []
        options = [("Brightness", self.brightness), ("Volume", self.volume)]
        for i, option in enumerate(options):
            self.options_menu_group.append(bitmap_label.Label(
                FONT,
                text=option[0]+':',
                color=self.palette[0],
                anchor_point=(0.0, 0.0),
                anchored_position=(self.display_center_x-60, self.options_y_start+i*self.options_spacing)
            ))
            self.option_values.append(label.Label(
                FONT,
                text=str(option[1]),
                color=self.palette[0],
                anchor_point=(0.5, 0.0),
                anchored_position=(self.display_center_x+35, self.options_y_start+i*self.options_spacing)
            ))
            self.options_menu_group.append(self.option_values[i])

        # Create options cursor
        self.options_cursor_group = Group(x=self.display_center_x+17)
        self.options_menu_group.append(self.options_cursor_group)
        self.options_cursor_group.append(Triangle(0, 3, 5, 0, 5, 6, outline=self.palette[0]))
        self.options_cursor_group.append(Triangle(30, 0, 35, 3, 30, 6, outline=self.palette[0]))
        self.current_option = 0
        self.update_options_cursor()

    def _create_controls_menu(self):
        """ Create controls menu elements """

        # Controls menu display group and hide
        self.controls_menu_group = Group()
        self.main_group.append(self.controls_menu_group)
        self.controls_menu_group.hidden = True

        # Create controls menu and title
        self.controls_menu_group.append(Rectangle(
            x=10,
            y=10,
            width=self.display.width-20,
            height=self.display.height-20,
            pixel_shader=self.palette,
            color_index=0
        ))
        self.controls_menu_group.append(Rectangle(
            x=12,
            y=12,
            width=self.display.width-24,
            height=self.display.height-24,
            pixel_shader=self.palette,
            color_index=1
        ))
        self.controls_menu_group.append(label.Label(
            FONT,
            text='Controls',
            color=self.palette[0],
            anchor_point=(0.5, 0.0),
            anchored_position=(self.display_center_x, 17)
        ))

        # Create controls menu text
        controls = [('Fire','A'), ('Thrust', 'B [hold]'), ('Rotate', 'Left/Right')]
        for i, control in enumerate(controls):
            self.controls_menu_group.append(bitmap_label.Label(
                FONT,
                text=control[0]+':',
                color=self.palette[0],
                anchor_point=(0.0, 0.0),
                anchored_position=(self.display_center_x-55, 40+i*15)
            ))
            self.controls_menu_group.append(label.Label(
                FONT,
                text=str(control[1]),
                color=self.palette[0],
                anchor_point=(0.0, 0.0),
                anchored_position=(self.display_center_x-2, 40+i*15)
            ))


    def _create_ship_object(self):
        """Create game ship object"""

        # Create ship object and add to display group
        self.ship = Ship(
            TileGrid(
                self.ships_bitmap,
                pixel_shader=self.ships_pallette,
                tile_width=self.ships_tile_width,
                tile_height=self.ships_tile_height
            ),
            self.display,
            self.display_center_x,
            self.display_center_y,
            v=0,
            angle=radians(0),
            heading=radians(0)
        )
        self.game_group.append(self.ship.tilegrid)

        # Initially hide ship
        self.ship.hidden = True


    def create_sub_asteroids(self, asteroid):
        '''
        Create sub asteroids
        '''
        # Determine size of sub asteroids
        sub_asteroid_size = asteroid.size + 1

        # Determine asteroid sprites based on size
        if sub_asteroid_size == 2:
            asteroid_bitmap = self.asteroids_medium_bitmap
            asteroid_pallette = self.asteroids_medium_pallette
            asteroid_tile_width = self.asteroids_medium_tile_width
            asteroid_tile_height = self.asteroids_medium_tile_height
        elif sub_asteroid_size == 3:
            asteroid_bitmap = self.asteroids_small_bitmap
            asteroid_pallette = self.asteroids_small_pallette
            asteroid_tile_width = self.asteroids_small_tile_width
            asteroid_tile_height = self.asteroids_small_tile_height

        # Create two sub asteroids
        for i in range(2):

            # Define asteroid tilegrid
            sub_asteroid_tilegrid = TileGrid(
                asteroid_bitmap,
                pixel_shader=asteroid_pallette,
                tile_width=asteroid_tile_width,
                tile_height=asteroid_tile_height,
                default_tile=choice([0])
            )

            # Randomly flip tilegrid around x axis
            sub_asteroid_tilegrid.flip_x = choice([True, False])

            # Define settings based on input asteroid
            x = asteroid.x
            y = asteroid.y
            v = asteroid.v * (1.1 + self.level * .05)
            angle = asteroid.angle + (radians(randrange(15,70) * (-1 if i == 0 else 1)))

            # Create asteroid object and update
            sub_asteroid = Asteroid(
                sub_asteroid_tilegrid,
                self.display,
                x=x,
                y=y,
                v=v,
                angle=angle,
                size=sub_asteroid_size
            )
            sub_asteroid.update()

            # Track and display asteroid
            self.asteroids.append(sub_asteroid)
            self.game_group.append(sub_asteroid.tilegrid)

    def create_hit_particles(self, obj):
        '''
        Create particles
        '''

        # Flag if object is ship or asteroid
        is_ship = isinstance(obj, Ship)

        # Create 5 particles
        for i in range(5):

            # Define particle settings base on object
            x = obj.x + randrange(-obj.display_width//3, obj.display_width//3)
            y = obj.y + randrange(-obj.display_height//3, obj.display_height//3)
            v = randrange(10,15)
            max_age = randrange(2,4) / 2.
            angle = radians(randrange(360))
            if is_ship:
                palette = self.palette
                color_index = 0
            else:
                palette = obj.tilegrid.pixel_shader
                color_index = randrange(len(palette))

            # Create particle object and display
            particle = RectParticle(
                x=x,
                y=y,
                width=1,
                height=1,
                v=v,
                angle=angle,
                display=self.display,
                palette=palette,
                max_age=max_age,
                color_index=color_index
            )
            self.particles.append(particle)
            self.game_group.append(particle.shape)

        # Create line particles
        if is_ship:
            for i in range(3):

                # Define particle settings base on object
                length = 6
                rot_angle = radians(randrange(360))
                x0 = obj.x + randrange(-obj.display_width//10,obj.display_width//10)
                y0 = obj.y + randrange(-obj.display_height//10,obj.display_height//10)
                x1 = x0 + length * cos(rot_angle)
                y1 = y0 + length * sin(rot_angle)
                v = randrange(10,15)
                angle = radians(randrange(360))
                max_age = randrange(2,4) / 2.

                # Create particle object and track/display
                particle = LineParticle(x0=x0, y0=y0, x1=x1, y1=y1, v=v, angle=angle, display=self.display, palette=self.palette, max_age=max_age)
                self.particles.append(particle)
                self.game_group.append(particle.shape)

    def create_asteroid_wave(self, count):
        '''
        Create wave of asteroids
        '''

        # Loop through asteroid count
        for i in range(count):

            # Define astroid tilegrid using large asteroid sprites
            asteroid_tilegrid = TileGrid(
                self.asteroids_large_bitmap,
                pixel_shader=self.asteroids_large_pallette,
                tile_width=self.asteroids_large_tile_width,
                tile_height=self.asteroids_large_tile_height,
                default_tile=choice([0]),
            )

            # Randomly flip tilegrid around x axis
            asteroid_tilegrid.flip_x = choice([True, False])

            # Calculate random start position along the display border
            border_x = asteroid_tilegrid.width * asteroid_tilegrid.tile_width // 2
            border_y = asteroid_tilegrid.height * asteroid_tilegrid.tile_height // 2
            x_min = -border_x
            x_max = self.display.width + border_x
            y_min = -border_y
            y_max = self.display.height + border_y
            start_position = choice([
                (randrange(x_min,x_max), y_min),
                (randrange(x_min,x_max), y_max),
                (x_min, randrange(y_min,y_max)),
                (x_max, randrange(y_min,y_max))
            ])

            # Randomize asteroid velocity and angle
            v = randrange(10,30)
            angle = radians(randrange(360))

            # Create asteroid object
            asteroid = Asteroid(
                asteroid_tilegrid,
                self.display,
                x=start_position[0],
                y=start_position[1],
                v=v,
                angle=angle,
                size=1
            )

            # Track and display astreroid
            self.asteroids.append(asteroid)
            self.game_group.append(asteroid.tilegrid)

    def clear_game_elements(self):
        '''
        Clear asteroid/bullet/particle elements from tracking and display
        '''

        # Clear asteroids from display and tracking
        for asteroid in self.asteroids:
            self.game_group.remove(asteroid.tilegrid)
        self.asteroids.clear()

        # Clear particles from display and tracking
        for particle in self.particles:
            self.game_group.remove(particle.shape)
        self.particles.clear()

        # Clear bullets from display and tracking
        for bullet in self.bullets:
            self.game_group.remove(bullet.shape)
        self.bullets.clear()

    def start_menu(self):
        '''
        Show start menu graphics
        '''

        # Update current game state
        self.current_state = AsteroidsGame.STATE_START_MENU

        # Clear asteroid/particles/bullets
        self.clear_game_elements()

        # Create background asteroids
        self.create_asteroid_wave(4)

        # Show/hide required display groups
        self.ui_group.hidden = True
        self.game_over_group.hidden = True
        self.score_input_group.hidden = True
        self.high_scores_group.hidden = True
        self.start_menu_group.hidden = False

    def options_menu(self):
        '''
        Show options menu graphics.
        '''

        # Update current game state and show/hide options menu
        if self.current_state != AsteroidsGame.STATE_OPTIONS_MENU:
            self.prev_state = self.current_state
            self.current_state = AsteroidsGame.STATE_OPTIONS_MENU
            self.options_menu_group.hidden = False
        else:
            self.current_state = self.prev_state
            self.options_menu_group.hidden = True

    def controls_menu(self):
        '''
        Show controls menu graphics.
        '''

        # Update current game state and show/hide controls menu
        if self.current_state != AsteroidsGame.STATE_CONTROLS_MENU:
            self.prev_state = self.current_state
            self.current_state = AsteroidsGame.STATE_CONTROLS_MENU
            self.controls_menu_group.hidden = False
        else:
            self.current_state = self.prev_state
            self.controls_menu_group.hidden = True

    def new_game(self):
        '''
        New Game
        '''

        # Update current game state
        self.current_state = AsteroidsGame.STATE_ACTIVE_GAME

        # Show/hide required display groups
        self.start_menu_group.hidden = True
        self.ui_group.hidden = False
        self.game_over_group.hidden = True
        self.high_scores_group.hidden = True
        self.score_input_group.hidden = True

        # Reset ship position
        self.ship.reset(x=self.display_center_x, y=self.display_center_y)
        self.ship.hidden = False

        # Reset game over continue text
        self.game_over_text_group.hidden = True

        # Reset game settings
        self.level = 1
        self.lives = AsteroidsGame.MAX_LIVES
        self.score = 0

        # Clear asteroid/particles/bullets
        self.clear_game_elements()

        # Update UI elements
        self.display_score()
        self.display_lives()

        # Reset initials cursor
        self.current_initial = 0
        self.update_initials_cursor()

        # Create asteroids
        self.create_asteroid_wave(self.level)

    def score_input_menu(self):
        '''
        High scores menu
        '''

        # Update current game state
        self.current_state = AsteroidsGame.STATE_SCORE_INPUT

        # Show/hide required display groups
        self.start_menu_group.hidden = True
        self.ui_group.hidden = True
        self.game_over_group.hidden = True
        self.high_scores_group.hidden = True
        self.score_input_group.hidden = False

    def high_scores_menu(self):
        '''
        High scores menu
        '''

        # Update current game state
        self.current_state = AsteroidsGame.STATE_HIGH_SCORES

        # Update display elements with scores
        for i, high_score in enumerate(self.high_scores):
            self.high_scores_names[i].text = high_score[0]
            self.high_scores_numbers[i].text = str(high_score[1])

        # Show/hide required display groups
        self.start_menu_group.hidden = True
        self.ui_group.hidden = True
        self.game_over_group.hidden = True
        self.score_input_group.hidden = True
        self.high_scores_group.hidden = False

    def game_over(self):
        '''
        Game over menu
        '''

        # Update current game state
        self.current_state = AsteroidsGame.STATE_GAME_OVER

        # Show/hide required display groups
        self.start_menu_group.hidden = True
        self.ui_group.hidden = True
        self.score_input_group.hidden = True
        self.high_scores_group.hidden = True
        self.game_over_group.hidden = False

    def update_high_scores(self, ):
        '''
        Add high scores to list and save...
        '''

        # Get player initials from menu inputs
        initials = ''.join([input.text for input in self.initial_inputs])

        # Update high scores and sort list
        self.high_scores.append((initials, self.score))
        self.high_scores.sort(key=lambda x: x[1], reverse=True)

        # Reduce list to top five scores
        if len(self.high_scores) > 5:
            self.high_scores.pop()

        # Save high scores to storage
        self.save_high_scores()

    def load_high_scores(self):
        ''' Return high scores from saved file or initialize empty list '''

        # Load high scores json file
        try:
            with open(AsteroidsGame.HIGH_SCORES_FNAME, 'r') as file:
                high_scores = json_load(file)

        # If load fails (does not exist), create empty list
        except:
            high_scores = []

        return high_scores

    def save_high_scores(self):
        ''' Save high score list to local storage '''

        # Write high score list to output json file
        with open(AsteroidsGame.HIGH_SCORES_FNAME, 'w') as f:
            json_dump(self.high_scores, f)

    def check_high_score(self):
        '''
        Check if input score is higher than
        any other current high score and return True
        '''
        if len(self.high_scores) < AsteroidsGame.NUM_HIGH_SCORES:
            return True
        else:
            for _, high_score in self.high_scores:
                if self.score > high_score:
                    return True
        return False

    def update_initials_cursor(self):
        '''
        Update the position of the initials input cursor
        based on the current active initial number
        '''
        self.initials_cursor_group.x = self.display_center_x - self.initial_spacing + self.current_initial * self.initial_spacing - 5

    def update_options_cursor(self):
        '''
        Update the position of the initials input cursor
        based on the current active initial number
        '''
        self.options_cursor_group.y = self.options_y_start + self.current_option * self.options_spacing + 2


    def update_option(self, decrease=False):
        '''
        Update selected option value
        '''

        # Brightness option is selected
        if self.current_option == 0:

            # Incrase/decrease value
            self.brightness = max(10, min(self.brightness - 10 if decrease else self.brightness + 10, 100))

            # Update options menu text
            self.option_values[self.current_option].text = str(self.brightness)

            # Change display brightness
            self.set_brightness()

        # Volume option is selected
        elif self.current_option == 1:

            # Increase/decrease value
            self.volume = max(0, min(self.volume - 10 if decrease else self.volume + 10, 100))

            # Update options menu text
            self.option_values[self.current_option].text = str(self.volume)

            # Change volume
            self.set_volume()

    def update_char(self, backwards=False):
        '''
        Update character in current input text
        dir=1 forward through alphabet, dir=0 backwards
        '''

        # Get next input character based on current character and direction
        current_char = self.initial_inputs[self.current_initial].text
        if current_char == '_':
            next_char = AsteroidsGame.CHARACTERS[0] if backwards == False else  AsteroidsGame.CHARACTERS[-1]
        else:
            char_index = AsteroidsGame.CHARACTERS.index(current_char)
            dir = 1 if backwards == False else -1
            next_char_index = (char_index + dir) % len(AsteroidsGame.CHARACTERS)
            next_char = AsteroidsGame.CHARACTERS[next_char_index]

        # Update intial input text
        self.initial_inputs[self.current_initial].text = next_char

    def confirm_char(self):
        '''
        Confirm char, proceed if last char
        '''

        # Check that valid letter is selected
        if self.initial_inputs[self.current_initial].text != '_':

            # Progress the cursor to next input if not at last position
            if self.current_initial != self.num_initials-1:
                self.current_initial += 1
                self.update_initials_cursor()

            # If at last position, update scores and proceed to high scores menu
            else:
                self.update_high_scores()
                self.high_scores_menu()

    def control_sound(self, action, sound_name, loop=False):
        '''
        Play/stop sound out of correct mixer
        '''

        # Get voice index and wav for input sound name
        voice_index, sound_wav = self.sounds[sound_name]

        # Play or stop
        if action == 'play':
            self.mixer.voice[voice_index].play(sound_wav, loop=loop)
        elif action == 'stop':
            self.mixer.voice[voice_index].stop()
        elif action == 'end':
            self.mixer.voice[voice_index].end()

    def create_bullet(self):
        '''
        Create bullet object
        '''

        # Define bullet settings based on ship
        x = round(self.ship.x + (self.ship.tilegrid.tile_width * .8 / 2) * sin(self.ship.heading)) - 1
        y = round(self.ship.y - (self.ship.tilegrid.tile_height * .8 /2) * cos(self.ship.heading)) - 1
        v = self.ship.vmax + 20

        # Create bullet object and display
        bullet = Bullet(x=x, y=y, radius=1, v=v, angle=self.ship.heading, display=self.display, palette=self.palette)

        # Add to tracking list and display
        self.bullets.append(bullet)
        self.game_group.append(bullet.shape)

    def display_score(self):
        '''
        Display updated score..
        '''
        self.score_text.text = str(self.score)

    def display_lives(self):
        '''
        Display lives icons..
        '''
        for i, tilegrid in enumerate(self.lives_tilegrids):
            tilegrid.hidden = i+1 > self.lives

    def set_brightness(self):
        '''
        Set brightness
        '''
        self.display.brightness = self.brightness / 100.

    def set_volume(self):
        '''
        Set volume
        '''
        for i in range(self.voice_count):
            self.mixer.voice[i].level = self.volume / 100.


    def a_button_event(self, pressed=True):
        '''
        A Button event function invoked by harware button press or release.
        Processes game event based on current game state
        '''

        # Game in start menu state and button pressed
        if self.current_state == AsteroidsGame.STATE_START_MENU and pressed:

            # Begin new game and play continue sound
            self.new_game()
            self.control_sound('play', 'new_ship')

        # Game in active play state and button pressed
        elif self.current_state == AsteroidsGame.STATE_ACTIVE_GAME and pressed and self.ship.hidden == False:

            # Create bullet object
            now = monotonic()
            if self.create_bullet_time == None or now - self.create_bullet_time > self.create_bullet_seconds:
                self.create_bullet_time = now
                self.create_bullet()
                self.control_sound('play', 'bullet')

        # Game in game over state and button pressed
        elif self.current_state == AsteroidsGame.STATE_GAME_OVER and pressed:

            # Check if text instructions are displayed after delay
            if self.game_over_text_group.hidden == False:

                # If new high score was acheived, show score input menu
                # otherwise show high scores menu
                if self.check_high_score():
                    self.score_input_menu()
                else:
                    self.high_scores_menu()
                self.control_sound('play', 'continue')

        # Game in score input state and button pressed
        elif self.current_state == AsteroidsGame.STATE_SCORE_INPUT and pressed:

            # Confirm selected character and proceed to next initial or
            # high scores menu
            self.confirm_char()
            self.control_sound('play', 'continue')

        # Game in high score state and button pressed
        elif self.current_state == AsteroidsGame.STATE_HIGH_SCORES and pressed:

            # Start new game and play continue sound
            self.start_menu()
            self.control_sound('play', 'continue')

    def b_button_event(self, pressed=True):
        '''
        B Button event function invoked by harware button press or release.
        Processes game event based on current game state
        '''

        # Game is in active state and ship is visible
        if self.current_state == AsteroidsGame.STATE_ACTIVE_GAME and self.ship.hidden == False:

            # Enable ship thrusing and sound when button pressed
            if pressed:
                self.ship.thrusting = 1
                self.control_sound('play', 'ship_thrust', loop=True)

            # Dissable thrusting and sound when button released
            else:
                self.ship.thrusting = 0
                self.control_sound('end', 'ship_thrust')

        # Game in score input state and button pressed
        elif self.current_state == AsteroidsGame.STATE_SCORE_INPUT and pressed:

            # Select the previous initial and update cursor
            if self.current_initial > 0:
                self.current_initial -= 1
                self.update_initials_cursor()

    def select_button_event(self, pressed=True):
        '''
        Select Button event function invoked by harware button press or release.
        Processes game event based on current game state
        '''

        # Controls menu is not open and select button pressed
        if self.current_state != AsteroidsGame.STATE_CONTROLS_MENU and pressed:

            # Disable ship thrusting/turning and sound
            if self.ship.thrusting:
                self.ship.thrusting = False
                self.control_sound('end', 'ship_thrust')
            if self.ship.turning:
                self.ship.turning = 0

            # Show/hide options menu and play continue sound
            self.options_menu()
            self.control_sound('play', 'continue')

    def start_button_event(self, pressed=True):
        '''
        Start Button event function invoked by harware button press or release.
        Processes game event based on current game state
        '''

        # Options menu is not open and select button pressed
        if self.current_state != AsteroidsGame.STATE_OPTIONS_MENU and pressed:

            # Disable ship thrusting/turning and sound
            if self.ship.thrusting:
                self.ship.thrusting = False
                self.control_sound('end', 'ship_thrust')
            if self.ship.turning:
                self.ship.turning = 0

            # Show/hide options menu and play continue sound
            self.controls_menu()
            self.control_sound('play', 'continue')

    def left_button_event(self, pressed=True):
        '''
        Left Button event function invoked by harware button press or release.
        Processes game event based on current game state
        '''

        # Game is in active state and ship is visible
        if self.current_state == AsteroidsGame.STATE_ACTIVE_GAME and self.ship.hidden == False:

            # Set ship turing flag left based on key press or release
            self.ship.turning = -1  if pressed else 0

        # Game in options menu state and button pressed
        elif self.current_state == AsteroidsGame.STATE_OPTIONS_MENU and pressed:

            # Update selected option value and play click sound
            self.update_option(decrease=True)
            self.control_sound('play', 'click')

    def right_button_event(self, pressed=True):
        '''
        Right Button event function invoked by harware button press or release.
        Processes game event based on current game state
        '''

        # Game is in active state and ship is visible
        if self.current_state == AsteroidsGame.STATE_ACTIVE_GAME and self.ship.hidden == False:

            # Set ship turing flag right based on key press or release
            self.ship.turning = 1 if pressed else 0

        # Game in options menu state and button pressed
        elif self.current_state == AsteroidsGame.STATE_OPTIONS_MENU and pressed:

            # Update selected option value and play click sound
            self.update_option()
            self.control_sound('play', 'click')

    def up_button_event(self, pressed=True):
        '''
        Up Button event function invoked by harware button press or release.
        Processes game event based on current game state
        '''

        # Game in options menu state and button pressed
        if self.current_state == AsteroidsGame.STATE_OPTIONS_MENU and pressed:

            # Update selected option and cursor position
            self.current_option = (self.current_option + 1) % len(self.option_values)
            self.update_options_cursor()

        # Game in score input state and button pressed
        elif self.current_state == AsteroidsGame.STATE_SCORE_INPUT and pressed:

            # Update initial input with next character
            self.update_char()
            self.control_sound('play', 'click')

    def down_button_event(self, pressed=True):
        '''
        Down Button event function invoked by harware button press or release.
        Processes game event based on current game state
        '''

        # Game in options menu state and button pressed
        if self.current_state == AsteroidsGame.STATE_OPTIONS_MENU and pressed:

            # Update selected option and cursor position
            self.current_option = (self.current_option - 1) % len(self.option_values)
            self.update_options_cursor()

        # Game in score input state and button pressed
        elif self.current_state == AsteroidsGame.STATE_SCORE_INPUT and pressed:

            # Update initial input with previous character
            self.update_char(backwards=True)
            self.control_sound('play', 'click')


    def tick(self):
        '''
        Game tick that advances elements
        '''

        # Calculate delta time between game ticks
        current_tick_time = monotonic()
        delta_time = current_tick_time - self.last_tick_time if self.last_tick_time else 0.02
        self.last_tick_time = current_tick_time
        #gc_collect()
        #print( mem_free() )

        # If options/controls menu is not open, process game objects
        if self.current_state not in [AsteroidsGame.STATE_OPTIONS_MENU, AsteroidsGame.STATE_CONTROLS_MENU]:

            # Update ship position and rotation
            self.ship.update(delta_time)

            # Update asteroids position
            for asteroid in self.asteroids:
                asteroid.update(delta_time)

            # Update bullet positions and age
            for bullet in self.bullets:
                bullet.update(delta_time)

            # Update update positions and age
            for paritcle in self.particles:
                paritcle.update(delta_time)

            # Process active gameplay state
            if self.current_state == AsteroidsGame.STATE_ACTIVE_GAME:

                # Check for collisions between asteroids and ship/bullets
                for asteroid in self.asteroids:

                    # Detect ship hit
                    if self.ship.is_hit == False and asteroid.detect_hit(self.ship):

                            # Play/stop sounds
                            self.control_sound('stop', 'ship_thrust')
                            self.control_sound('play', 'ship_explosion')

                            # Remove ship from display
                            self.ship.hidden = True

                            # Create debris particles
                            self.create_hit_particles(self.ship)

                            # Update ship reset time
                            self.ship_hit_time = monotonic()

                            # Update player lives and display
                            self.lives -= 1
                            self.display_lives()

                    # Detect bullet hit
                    if not asteroid.is_hit:
                        for bullet in [b for b in self.bullets if b.is_hit == False]:
                            if asteroid.detect_hit(bullet):
                                break

                    # Process asteroid hit
                    if asteroid.is_hit:

                        # Play explosion sound based on size
                        if self.ship.is_hit == False:
                            if asteroid.size == 1:
                                self.control_sound('play', 'explosion_large')
                            elif asteroid.size == 2:
                                self.control_sound('play', 'explosion_medium')
                            elif asteroid.size == 3:
                                self.control_sound('play', 'explosion_small')

                        # Update score
                        self.score += AsteroidsGame.ASTEROID_POINTS[asteroid.size]
                        self.display_score()

                        # Create debris particles
                        self.create_hit_particles(asteroid)

                        # Create sub asteroids
                        if asteroid.size < 3:
                            self.create_sub_asteroids(asteroid)

                # Process hit ship
                if self.ship.is_hit:

                    # If game lives remain reset ship
                    if self.lives  > 0:

                        # Check if reset period has elapsed
                        if monotonic() - self.ship_hit_time > self.ship_reset_seconds:

                            # Determine if asteroids are blocking reset postion
                            buffer = 30
                            blocked = False
                            for asteroid in self.asteroids:
                                if self.display_center_x-buffer <= asteroid.x <= self.display_center_x+buffer and \
                                   self.display_center_y-buffer <= asteroid.y <= self.display_center_y+buffer:
                                    blocked = True
                                    break

                            # Reset ship position and settings and display
                            if blocked == False:
                                self.ship.reset(x=self.display_center_x, y=self.display_center_y)
                                self.ship.hidden = False
                                self.control_sound('play', 'new_ship')

                    # If zero lives remain
                    else:

                        # Display game over menu
                        self.game_over_time = monotonic()
                        self.game_over()
                        self.control_sound('play', 'game_over')

            # Process game over game step
            elif self.current_state == AsteroidsGame.STATE_GAME_OVER:

                # Show game over text instructions after delay has passed
                if self.game_over_text_group.hidden and monotonic() - self.game_over_time > self.game_over_seconds:
                    self.game_over_text_group.hidden = False

            # Clear hit asteroids from tracking and display
            hit_asteroids = [asteroid for asteroid in self.asteroids if asteroid.is_hit]
            for asteroid in hit_asteroids:
                self.game_group.remove(asteroid.tilegrid)
                self.asteroids.remove(asteroid)

            # Clear expired particles from tracking and display
            expired_particles = [particle for particle in self.particles if particle.check_expired()]
            for particle in expired_particles:
                self.game_group.remove(particle.shape)
                self.particles.remove(particle)

            # Clear expired bullets from tracking and display
            expired_bullets = [bullet for bullet in self.bullets if bullet.check_expired() or bullet.is_hit]
            for bullet in expired_bullets:
                self.game_group.remove(bullet.shape)
                self.bullets.remove(bullet)

            # Check if all asteroids destroyed
            if len(self.asteroids) == 0:

                # Initiate next wave of asteroids
                self.level += 1
                self.create_asteroid_wave(min(self.level, 3))

class SpaceTilegrid:
    '''
    Class
    '''

    def __init__(self, tilegrid, display, x=0, y=0, v=0, angle=0):
        # Tilegrid
        self.tilegrid = tilegrid

        # Display object - dimensions used for position wrapping
        self.display = display

        # Object movement parameters
        self.x = x
        self.y = y
        self.v = v
        self.angle = angle

        # Pixel height and width of the tilegrid
        self.display_width = tilegrid.width * tilegrid.tile_width
        self.display_height = tilegrid.height * tilegrid.tile_height

        # Flag designating objet as hit
        self.is_hit = False

    @property
    def hidden(self):
        return self.tilegrid.hidden

    @hidden.setter
    def hidden(self, hide):
        self.tilegrid.hidden = hide

    def get_bounds(self):
        '''
        Return display bounds...
        '''

        # Calculate upper left and lower right corners
        xmin = self.tilegrid.x
        xmax = self.tilegrid.x + self.display_width
        ymin = self.tilegrid.y
        ymax = self.tilegrid.y + self.display_height

        return xmin, xmax, ymin, ymax

    def get_pixel_locs(self, bounds):
        '''
        Return array of pixel locations where the bitmap represents the image
        '''

        # Determine background value
        background_value = self.tilegrid.bitmap[0,0]

        # Initialze output pixel list
        pixel_locs = []

        # Loop through all tiles in the tilegrid
        for j in range(self.tilegrid.height):
            for i in range(self.tilegrid.width):

                # Calculate tile bounds within display
                tile_xmin = self.tilegrid.x + i * self.tilegrid.tile_width
                tile_xmax = tile_xmin + self.tilegrid.tile_width
                tile_ymin = self.tilegrid.y + j * self.tilegrid.tile_height
                tile_ymax = tile_ymin + self.tilegrid.tile_height
                tile_bounds = [tile_xmin, tile_xmax, tile_ymin, tile_ymax]

                # Determine tile overlap with input bounds
                tile_overlap_bounds = find_overlap_bounds(bounds, tile_bounds)
                if tile_overlap_bounds:

                    # Get coordinates of tile within bitmap
                    tile_index = self.tilegrid[i,j]
                    tiles_per_row = self.tilegrid.bitmap.width / self.tilegrid.tile_width
                    bitmap_xstart = int((tile_index % tiles_per_row) * self.tilegrid.tile_width)
                    bitmap_ystart = int((tile_index // tiles_per_row) * self.tilegrid.tile_height)

                    # Calulate offsets from bitmap start to overlapping area, accounting
                    # for the tiles flipped status
                    if self.tilegrid.flip_x:
                        bitmap_xoffset = tile_xmax - tile_overlap_bounds[1]
                    else:
                        bitmap_xoffset = tile_overlap_bounds[0] - tile_xmin
                    if self.tilegrid.flip_y:
                        bitmap_yoffset = tile_ymax - tile_overlap_bounds[3]
                    else:
                        bitmap_yoffset = tile_overlap_bounds[2] - tile_ymin

                    # Calculate pixel range within bitmap of overlap
                    range_width = tile_overlap_bounds[1] - tile_overlap_bounds[0]
                    range_height = tile_overlap_bounds[3] - tile_overlap_bounds[2]
                    range_xstart = (bitmap_xstart + bitmap_xoffset)
                    range_ystart = (bitmap_ystart + bitmap_yoffset)
                    range_xend = range_xstart + range_width
                    range_yend = range_ystart + range_height

                    # Loop through bitmap pixel positions
                    for x in range(range_xstart, range_xend):
                        for y in range(range_ystart, range_yend):

                            # Determine if pixel is not equal to backgroudn value
                            if self.tilegrid.bitmap[x, y] != background_value:

                                # Calculate display coordinates of pixel
                                if self.tilegrid.flip_x:
                                    display_x = tile_xmin + self.tilegrid.tile_width - 1 - (x - bitmap_xstart)
                                else:
                                    display_x = tile_xmin + x - bitmap_xstart
                                if self.tilegrid.flip_y:
                                    display_y = tile_ymin + self.tilegrid.tile_height - 1 - (y - bitmap_ystart)
                                else:
                                    display_y = tile_ymin + y - bitmap_ystart

                                # Add display coordinates to output
                                pixel_locs.append((display_x, display_y))

        return pixel_locs


class Ship(SpaceTilegrid):
    '''
    Ship class...
    '''

    def __init__(self, tilegrid, display, x=0, y=0, v=0, angle=0, heading=0):
        super().__init__(tilegrid, display, x=x, y=y, v=v, angle=angle)

        # Ship heading angle controling
        self.heading = heading

        # Maximum ship velocity
        self.vmax = 110

        # Turing flag; -1 Left, 0 No Turning; 1 Right
        self.turning = 0

        # Delta angle applied on while turing on each updae
        self.turning_angle = pi / 36 * 60

        # Thrusting flag
        self.thrusting = 0

        # Thrust added on each update while thrusting
        self.thrust_value = 80

        # Dropoff factor applied on each update while not thrusting
        self.v_dropoff = .5

        # Number of tiles per row in tilegrid bitmap
        self.num_tiles = self.tilegrid.bitmap.width // self.tilegrid.tile_width

        # Update the ship position
        self.update()

    def update(self, delta_time=0):
        '''
        Update postion... factor in delta time..,
        '''

        # Update ship heading based on turnign status and apply angle wrapping
        if self.turning != 0:
            self.heading += self.turning * self.turning_angle * delta_time
            self.heading %= 2 * pi

        # Calculate current velocity components
        vx = sin(self.angle) * self.v
        vy = -cos(self.angle) * self.v

        # Update velocity components based on thursting status
        if self.thrusting:
            thrust_x = sin(self.heading) * self.thrust_value * delta_time
            thrust_y = -cos(self.heading) * self.thrust_value * delta_time
            vx = max(min(vx + thrust_x, self.vmax), -self.vmax)
            vy = max(min(vy + thrust_y, self.vmax), -self.vmax)
        else:
            decay_factor = (1 - self.v_dropoff) ** delta_time
            vx *= (1 - self.v_dropoff) ** delta_time
            vy *= (1 - self.v_dropoff) ** delta_time

        # Update ship position and apply screen wrapping
        self.x = ((self.x + vx * delta_time + self.display_width/2) % (self.display.width + self.display_width)) - self.display_width/2
        self.y = ((self.y + vy * delta_time + self.display_height/2) % (self.display.height + self.display_height)) - self.display_height/2

        # Update tilegrid position centered on the ship position
        self.tilegrid.x = int(self.x - self.display_width/2)
        self.tilegrid.y = int(self.y - self.display_height/2)

        # Recalculate velocity and angle
        self.v = sqrt(vx**2 + vy**2)
        self.angle = atan2(vx, -vy)

        # Determine tile index based on current heading
        tile_idx = round(degrees(self.heading) / (360 / self.num_tiles)) % self.num_tiles

        # Determine tile index offset based on thrust state
        if self.thrusting and ((monotonic() % 1) // 0.05 % 2) == 0:
            tile_offset =1
        else:
            tile_offset = 0

        # Update ship tiletrid
        self.tilegrid[0] = tile_idx + (tile_offset * self.num_tiles)

    def reset(self, x=0, y=0):
        '''
        Rest ship...
        '''

        # Set position and flag values
        self.x = x
        self.y = y
        self.v = 0
        self.thrusting = 0
        self.turning = 0
        self.angle=radians(0)
        self.heading=radians(0)
        self.is_hit = False

        # Update the ship position
        self.update()


class Asteroid(SpaceTilegrid):
    '''
    Asteroid class
    '''

    def __init__(self, tilegrid, display, x=0, y=0, v=0, angle=0, size=1):
        super().__init__(tilegrid, display, x=x, y=y, v=v, angle=angle)

        # Size of asteroid (1-3)
        self.size = size

        # Update the asteroid position
        self.update()

    def update(self, delta_time=0):
        '''
        Update postion... factor in delta time..,
        '''

        # Calculate velocity components
        vx = sin(self.angle) * self.v * delta_time
        vy = -cos(self.angle) * self.v  * delta_time

        # Update position and apply screen wrapping
        self.x = ((self.x + vx + self.display_width/2) % (self.display.width + self.display_width)) - self.display_width/2
        self.y = ((self.y + vy + self.display_height/2) % (self.display.height + self.display_height)) - self.display_height/2

        # Update tilegrid position centered on the ship position
        self.tilegrid.x = int(self.x - self.display_width/2)
        self.tilegrid.y = int(self.y - self.display_height/2)

    def detect_hit(self, obj):
        '''
        Detect hit..
        '''

        # Calculate bounds overlap between objects
        self_bounds = self.get_bounds()
        obj_bounds = obj.get_bounds()
        overlap_bounds = find_overlap_bounds(self_bounds, obj_bounds)

        # Return if no overlap exists
        if overlap_bounds == None:
            return False

        # Get non-background pixel locations within overlap bounds
        self_pixel_locs = self.get_pixel_locs(overlap_bounds)
        obj_pixel_locs = obj.get_pixel_locs(overlap_bounds)

        # Compare pixel locations for valid hit
        for self_pixel in self_pixel_locs:
            for obj_pixel in obj_pixel_locs:
                if self_pixel == obj_pixel:
                    self.is_hit = True
                    obj.is_hit = True
                    return True

        return False


class SpaceParticle:
    '''
    Base class...
    '''
    def __init__(self, x, y, v, angle, display, palette, max_age=0.7, color_index=0):
        # Display object - dimensions used for position wrapping
        self.display = display

        # Object movement parameters
        self.x = x
        self.y = y
        self.v = v
        self.angle = angle

        # Particle color pallet and selection
        self.palette = palette
        self.color_index = color_index

        # Particle life parameters (seconds)
        self.age = 0
        self.max_age = max_age

        # Particle shape object
        self.shape = None

    def update(self, delta_time=0):
        '''
        Update position...
        '''

        # Calculate velocity components
        vx = sin(self.angle) * self.v * delta_time
        vy = -cos(self.angle) * self.v  * delta_time

        # Update position and apply screen wrapping
        self.x = (self.x + vx) % self.display.width
        self.y = (self.y + vy) % self.display.height

        # Update update shape position
        self.shape.x = int(self.x)
        self.shape.y = int(self.y)

        # Update age
        self.age += delta_time

    def check_expired(self):
        '''
        Check expired...
        '''
        return self.age > self.max_age


class CircleParticle(SpaceParticle):
    def __init__(self, x, y, radius, v, angle, display, palette, max_age=0.9, color_index=0):
        super().__init__(x, y, v, angle, display, palette, max_age=max_age, color_index=color_index)

        # Circle radius
        self.radius = radius

        # Circle display object
        self.shape = Circle(
            x=int(self.x),
            y= int(self.y),
            radius=self.radius,
            pixel_shader=self.palette,
            color_index=self.color_index
        )


class RectParticle(SpaceParticle):
    '''
    Rect particle class
    '''
    def __init__(self, x, y, width, height, v, angle, display, palette, max_age=0.9, color_index=0):
        super().__init__(x, y, v, angle, display, palette, max_age=max_age, color_index=color_index)

        # Rectantle dimensions
        self.width = width
        self.height = height

        # Rectangle display object
        self.shape = Rectangle(
            x=int(self.x),
            y=int(self.y),
            width=int(self.width),
            height=int(self.height),
            pixel_shader=self.palette,
            color_index=self.color_index
        )

class LineParticle(SpaceParticle):
    '''
    Line particle class
    '''

    def __init__(self, x0, y0, x1, y1, v, angle, display, palette, color_index=0, max_age=0.9):
        super().__init__(x0, y0, v, angle, display, palette, max_age=max_age, color_index=color_index)
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.width = abs(self.x0 - self.x1)
        self.height = abs(self.y0 - self.y1)
        self.shape = Line(int(self.x0), int(self.y0), int(self.x1), int(self.y1), color=self.palette[self.color_index])
        self.x = self.shape.x
        self.y = self.shape.y

    def update(self, delta_time=0):
        '''
        Update
        '''

        # Update the line position
        vx = sin(self.angle) * self.v * delta_time
        vy = -cos(self.angle) * self.v  * delta_time
        self.x = ((self.x + vx + self.width/2) % (self.display.width + self.width)) - self.width/2
        self.y = ((self.y + vy + self.height/2) % (self.display.height + self.height)) - self.height/2
        self.shape.x = int(self.x)
        self.shape.y = int(self.y)

        # Update age
        self.age += delta_time


class Bullet(CircleParticle):
    def __init__(self, x, y, radius, v, angle, display, palette, max_age=0.6, color_index=0):
        super().__init__(x, y, radius, v, angle, display, palette, max_age=max_age, color_index=color_index)

        # Collision status flag
        self.is_hit = False

    def get_bounds(self):
        '''
        Get bounds...
        '''

        # Calculate upper left and lower right corners
        xmin = int(self.shape.x - self.radius)
        xmax = int(self.shape.x + self.radius)
        ymin = int(self.shape.y - self.radius)
        ymax = int(self.shape.y + self.radius)

        return xmin, xmax, ymin, ymax

    def get_pixel_locs(self, overlap_bounds):
        '''
        Get pixel locs
        '''
        return [(int(self.shape.x), int(self.shape.y))]

def find_overlap_bounds(bounds_1, bounds_2):
    ''' Return bounds (xmin, xmax, ymin, ymax) of overlapping
        area between two input bounds. Return None if no
        overlap exists
    '''

    # Calculate the overlapping region
    overlap_xmin = max(bounds_1[0], bounds_2[0])
    overlap_xmax = min(bounds_1[1], bounds_2[1])
    overlap_ymin = max(bounds_1[2], bounds_2[2])
    overlap_ymax = min(bounds_1[3], bounds_2[3])

    # Check if there is an actual overlap
    if overlap_xmin < overlap_xmax and overlap_ymin < overlap_ymax:
        return overlap_xmin, overlap_xmax, overlap_ymin, overlap_ymax
    else:
        # No overlap
        return None

