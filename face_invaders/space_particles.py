"""Particle effect classes used to draw explosions and bullets."""

from math import sin, cos
from vectorio import Rectangle, Circle
from adafruit_display_shapes.line import Line

class SpaceParticle:
    '''
    Base class for all particle effects in the game
    '''
    def __init__(self, x, y, v, angle, display, palette, max_age=0.7, color_index=0):
        """Initialize a particle effect."""

        # Display object - dimensions used for position wrapping
        self.display = display

        # Object movement parameters
        self.x = x
        self.y = y
        self.v = v
        self.angle = angle

        # Particle color palette and selection
        self.palette = palette
        self.color_index = color_index

        # Particle life parameters (seconds)
        self.age = 0
        self.max_age = max_age

        # Particle shape object
        self.shape = None

    def update(self, delta_time=0):
        '''
        Update particle position and age
        '''
        # Calculate velocity components
        vx = sin(self.angle) * self.v * delta_time
        vy = -cos(self.angle) * self.v * delta_time

        # Update position and apply screen wrapping
        self.x = (self.x + vx) % self.display.width
        self.y = (self.y + vy) % self.display.height

        # Update shape position
        self.shape.x = int(self.x)
        self.shape.y = int(self.y)

        # Update age
        self.age += delta_time

    def check_expired(self):
        '''
        Check if particle has exceeded its maximum age
        '''
        return self.age > self.max_age


class CircleParticle(SpaceParticle):
    '''
    Circular particle effect
    '''
    def __init__(self, x, y, radius, v, angle, display, palette, max_age=0.9, color_index=0):
        """Create a circular particle effect."""

        super().__init__(x, y, v, angle, display, palette, max_age=max_age, color_index=color_index)

        # Circle radius
        self.radius = radius

        # Circle display object
        self.shape = Circle(
            x=int(self.x),
            y=int(self.y),
            radius=self.radius,
            pixel_shader=self.palette,
            color_index=self.color_index
        )


class RectParticle(SpaceParticle):
    '''
    Rectangular particle effect
    '''
    def __init__(self, x, y, width, height, v, angle, display, palette, max_age=0.9, color_index=0):
        """Create a rectangular particle effect."""

        super().__init__(x, y, v, angle, display, palette, max_age=max_age, color_index=color_index)

        # Rectangle dimensions
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
    Line segment particle effect
    '''
    def __init__(self, x0, y0, x1, y1, v, angle, display, palette, color_index=0, max_age=0.9):
        """Create a line segment particle effect."""

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
        Update line particle position and age
        '''
        # Update the line position
        vx = sin(self.angle) * self.v * delta_time
        vy = -cos(self.angle) * self.v * delta_time
        self.x = ((self.x + vx + self.width/2) % (self.display.width + self.width)) - self.width/2
        self.y = ((self.y + vy + self.height/2) % (self.display.height + self.height)) - self.height/2
        self.shape.x = int(self.x)
        self.shape.y = int(self.y)

        # Update age
        self.age += delta_time


class Bullet(CircleParticle):
    '''
    Player bullet projectile
    '''
    def __init__(self, x, y, radius, v, angle, display, palette, max_age=0.6, color_index=0):
        """Create a player bullet."""

        super().__init__(x, y, radius, v, angle, display, palette, max_age=max_age, color_index=color_index)

        # Collision status flag
        self.is_hit = False

    def get_bounds(self):
        '''
        Get bullet bounds for collision detection
        '''
        # Calculate upper left and lower right corners
        xmin = int(self.shape.x - self.radius)
        xmax = int(self.shape.x + self.radius)
        ymin = int(self.shape.y - self.radius)
        ymax = int(self.shape.y + self.radius)

        return xmin, xmax, ymin, ymax

    def get_pixel_locs(self, overlap_bounds):
        '''
        Get pixel locations for collision detection
        '''
        return [(int(self.shape.x), int(self.shape.y))]
