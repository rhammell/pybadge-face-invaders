# pybadge-face-invaders
Face Invaders is an arcade game built for the Adafruit PyBadge, which features personalized 'face' objects that the player can dodge and destroy.

This repository contains the code, image sprites, and audio assets to run the game. Read the [project guide](https://www.hackster.io/rhammell/pybadge-face-invaders-c26c30) on Hackster.io for a more game details and installation instructions. 

# Project Description

The game recreates the arcade classic Asteroids, giving players control over a physics-based ship to thrust, turn, and shoot. The goal is to earn a high score by eliminating waves of incoming objects that destroy the ship on contact.

![Face Invaders Gameplay](https://i.imgur.com/ETon29N.gif)

For a fun experience, the typical asteroid game sprites are replaced with custom-created face sprites. This adds a playful twist to the gameplay, as players are now maneuvering around the floating faces of friends, family, or even themselves.

Additional Face Invaders features include:

- Frame Rate Optimization: Time-based movement calculations are used to update object positions each frame, providing consistent movement speeds regardless of frame processing time.
- High Score System: After earning a new high score, players are prompted to enter their initials to be added to the high scores list. These scores are saved and persist between games.
- Pixel-based Hit Detection: Collisions between the ship, bullets, and faces are calculated on a per-pixel basis (as opposed to hitboxes) to ensure accurate hits between objects.
- Brightness and Volume Control: Users can alter the brightness of the display and volume of the speakers within the game's Options menu.
- Sound Effects: Retro arcade sound effects are played for thrusting, shooting, collisions, and more.