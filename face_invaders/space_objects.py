# objects.py - Core game objects for Face Invaders

from math import sin, cos, radians, pi, sqrt, atan2, degrees
from time import monotonic

# Import utilities
from face_invaders.utils import find_overlap_bounds

class SpaceTilegrid:
    '''
    Base class for all game objects with tilegrid representation
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

        # Flag designating object as hit
        self.is_hit = False

    @property
    def hidden(self):
        return self.tilegrid.hidden

    @hidden.setter
    def hidden(self, hide):
        self.tilegrid.hidden = hide

    def get_bounds(self):
        '''
        Return display bounds as (xmin, xmax, ymin, ymax)
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

        # Initialize output pixel list
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

                    # Calculate offsets from bitmap start to overlapping area, accounting
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

                            # Determine if pixel is not equal to background value
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
    Player spaceship class
    '''

    def __init__(self, tilegrid, display, x=0, y=0, v=0, angle=0, heading=0):
        super().__init__(tilegrid, display, x=x, y=y, v=v, angle=angle)

        # Ship heading angle controlling
        self.heading = heading

        # Maximum ship velocity
        self.vmax = 110

        # Turning flag; -1 Left, 0 No Turning; 1 Right
        self.turning = 0

        # Delta angle applied while turning on each update
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
        Update position based on heading, thrust, and delta time
        '''
        # Update ship heading based on turning status and apply angle wrapping
        if self.turning != 0:
            self.heading += self.turning * self.turning_angle * delta_time
            self.heading %= 2 * pi

        # Calculate current velocity components
        vx = sin(self.angle) * self.v
        vy = -cos(self.angle) * self.v

        # Update velocity components based on thrusting status
        if self.thrusting:
            thrust_x = sin(self.heading) * self.thrust_value * delta_time
            thrust_y = -cos(self.heading) * self.thrust_value * delta_time
            vx = max(min(vx + thrust_x, self.vmax), -self.vmax)
            vy = max(min(vy + thrust_y, self.vmax), -self.vmax)
        else:
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
            tile_offset = 1
        else:
            tile_offset = 0

        # Update ship tilegrid
        self.tilegrid[0] = tile_idx + (tile_offset * self.num_tiles)

    def reset(self, x=0, y=0):
        '''
        Reset ship position and movement parameters
        '''
        # Set position and flag values
        self.x = x
        self.y = y
        self.v = 0
        self.thrusting = 0
        self.turning = 0
        self.angle = radians(0)
        self.heading = radians(0)
        self.is_hit = False

        # Update the ship position
        self.update()


class Face(SpaceTilegrid):
    '''
    Enemy face class (renamed from Asteroid)
    '''

    def __init__(self, tilegrid, display, x=0, y=0, v=0, angle=0, size=1):
        super().__init__(tilegrid, display, x=x, y=y, v=v, angle=angle)

        # Size of face (1-3)
        self.size = size

        # Update the face position
        self.update()

    def update(self, delta_time=0):
        '''
        Update face position and apply screen wrapping
        '''
        # Calculate velocity components
        vx = sin(self.angle) * self.v * delta_time
        vy = -cos(self.angle) * self.v * delta_time

        # Update position and apply screen wrapping
        self.x = ((self.x + vx + self.display_width/2) % (self.display.width + self.display_width)) - self.display_width/2
        self.y = ((self.y + vy + self.display_height/2) % (self.display.height + self.display_height)) - self.display_height/2

        # Update tilegrid position centered on the face position
        self.tilegrid.x = int(self.x - self.display_width/2)
        self.tilegrid.y = int(self.y - self.display_height/2)

    def detect_hit(self, obj):
        '''
        Detect collision with another game object
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