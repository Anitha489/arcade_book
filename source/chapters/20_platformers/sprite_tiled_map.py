"""
Load a map stored in csv format, as exported by the program 'Tiled.'

Artwork from: http://kenney.nl
Tiled available from: http://www.mapeditor.org/
"""
import arcade

SPRITE_SCALING = 0.5

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
VIEWPORT_MARGIN = 40
RIGHT_MARGIN = 150

# Physics
MOVEMENT_SPEED = 5
JUMP_SPEED = 14
GRAVITY = 0.5


def get_map(filename):
    """
    This function loads an array based on a map stored as a list of
    numbers separated by commas.
    """

    # Open the file
    map_file = open(filename)

    # Create an empty list of rows that will hold our map
    map_array = []

    # Read in a line from the file
    for line in map_file:

        # Strip the whitespace, and \n at the end
        line = line.strip()

        # This creates a list by splitting line everywhere there is a comma.
        map_row = line.split(",")

        # The list currently has all the numbers stored as text, and we want it
        # as a number. (e.g. We want 1 not "1"). So loop through and convert
        # to an integer.
        for index, item in enumerate(map_row):
            map_row[index] = int(item)

        # Now that we've completed processing the row, add it to our map array.
        map_array.append(map_row)

    # Done, return the map.
    return map_array


class MyWindow(arcade.Window):
    """ Main application class. """

    def __init__(self, width, height):
        """
        Initializer
        """
        # Call the parent class
        super().__init__(width, height)

        # Sprite lists
        self.all_sprites_list = None
        self.coin_list = None
        self.wall_list = None

        # Set up the player
        self.score = 0
        self.player_sprite = None

        # Physics engine
        self.physics_engine = None

        # Used for scrolling map
        self.view_left = 0
        self.view_bottom = 0

        # When the user gets far enough, we'll print "Game Over"
        self.game_over = False

    def setup(self):
        """ Set up the game and initialize the variables. """

        # Sprite lists
        self.all_sprites_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()

        # Set up the player
        self.score = 0
        self.player_sprite = arcade.Sprite("character.png", SPRITE_SCALING)

        # Starting position of the player
        self.player_sprite.center_x = 64
        self.player_sprite.center_y = 270
        self.all_sprites_list.append(self.player_sprite)

        # Get a 2D array made of numbers based on the map
        map_array = get_map("map.csv")

        # Now that we've got the map, loop through and create the sprites
        for row_index, row in enumerate(map_array):
            for column_index, item in enumerate(row):

                # For this map, the numbers represent:
                # -1 = empty
                # 0  = box
                # 1  = grass left edge
                # 2  = grass middle
                # 3  = grass right edge
                if item == -1:
                    continue
                elif item == 0:
                    wall = arcade.Sprite("boxCrate_double.png", SPRITE_SCALING)
                elif item == 1:
                    wall = arcade.Sprite("grassLeft.png", SPRITE_SCALING)
                elif item == 2:
                    wall = arcade.Sprite("grassMid.png", SPRITE_SCALING)
                elif item == 3:
                    wall = arcade.Sprite("grassRight.png", SPRITE_SCALING)

                # Calculate where the sprite goes
                wall.right = column_index * 64
                wall.top = (7 - row_index) * 64

                # Add the sprite
                self.all_sprites_list.append(wall)
                self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY)

        # Set the background color
        arcade.set_background_color(arcade.color.AMAZON)

        # Set the view port boundaries
        # These numbers set where we have 'scrolled' to.
        self.view_left = 0
        self.view_bottom = 0

        self.game_over = False

    def on_draw(self):
        """
        Render the screen.
        """

        # This command has to happen before we start drawing
        arcade.start_render()

        # Draw all the sprites.
        self.all_sprites_list.draw()

        # Put the text on the screen.
        # Adjust the text position based on the view port so that we don't
        # scroll the text too.
        distance = self.view_left + self.player_sprite.right
        output = f"Distance: {distance}"
        arcade.draw_text(output, self.view_left + 10, self.view_bottom + 20, arcade.color.WHITE, 14)

        if self.game_over:
            output = "Game Over"
            arcade.draw_text(output, self.view_left + 200,
                             self.view_bottom + 200,
                             arcade.color.WHITE, 30)

    def on_key_press(self, key, modifiers):
        """
        Called whenever a key is pressed.
        """
        if key == arcade.key.UP:
            # This line below is new. It checks to make sure there is a platform underneath
            # the player. Because you can't jump if there isn't ground beneath your feet.
            if self.physics_engine.can_jump():
                self.player_sprite.change_y = JUMP_SPEED
        elif key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED

    def on_key_release(self, key, modifiers):
        """
        Called when the user releases a key.
        """
        if key == arcade.key.LEFT or key == arcade.key.RIGHT:
            self.player_sprite.change_x = 0

    def update(self, delta_time):
        """ Movement and game logic """

        if self.view_left + self.player_sprite.right >= 5630:
            self.game_over = True

        # Call update on all sprites (The sprites don't do much in this
        # example though.)
        if not self.game_over:
            self.physics_engine.update()

        # --- Manage Scrolling ---

        # Track if we need to change the view port

        changed = False

        # Scroll left
        left_bndry = self.view_left + VIEWPORT_MARGIN
        if self.player_sprite.left < left_bndry:
            self.view_left -= left_bndry - self.player_sprite.left
            changed = True

        # Scroll right
        right_bndry = self.view_left + SCREEN_WIDTH - RIGHT_MARGIN
        if self.player_sprite.right > right_bndry:
            self.view_left += self.player_sprite.right - right_bndry
            changed = True

        # Scroll up
        top_bndry = self.view_bottom + SCREEN_HEIGHT - VIEWPORT_MARGIN
        if self.player_sprite.top > top_bndry:
            self.view_bottom += self.player_sprite.top - top_bndry
            changed = True

        # Scroll down
        bottom_bndry = self.view_bottom + VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_bndry:
            self.view_bottom -= bottom_bndry - self.player_sprite.bottom
            changed = True

        # If we need to scroll, go ahead and do it.
        if changed:
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    window = MyWindow(SCREEN_WIDTH, SCREEN_HEIGHT)
    window.setup()

    arcade.run()


main()
