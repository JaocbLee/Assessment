"""
Super bruv
"""

import arcade
from arcade.experimental.lights import Light, LightLayer
import timeit
import math

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 650
SCREEN_TITLE = "Super Bruv"

# Constants used to scale our sprites from their original size
TILE_SCALING = 0.5
CHARACTER_SCALING = 0.4
COIN_SCALING = TILE_SCALING
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 7
GRAVITY = 1.5
PLAYER_JUMP_SPEED = 20

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = 250
RIGHT_VIEWPORT_MARGIN = 250
BOTTOM_VIEWPORT_MARGIN = 150
TOP_VIEWPORT_MARGIN = 300

Lives = 3
num_level = 1

PLAYER_START_X = 140
PLAYER_START_Y = 360

# Speed of the bullets
BULLET_SPEED: int = 7
SPRITE_SCALING_LASER = 1.2

# way the character is facing
RIGHT_FACING = 0
LEFT_FACING = 1


def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(arcade.Sprite):
    """ Player Sprite"""

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING
        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Track our state
        self.jumping = False
        self.climbing = False
        self.is_on_ladder = False

        # --- Load Textures ---
        main_path = ":resources:images/animated_characters/male_person/malePerson"


        # Load textures for idle standing
        self.idle_texture_pair = load_texture_pair("Sprites/Character/Character_detail.png")

        # Load textures for walking
        self.walk_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}_walk{i}.png")
            self.walk_textures.append(texture)

        # Load textures for climbing
        self.climbing_textures = []
        texture = arcade.load_texture(f"{main_path}_climb0.png")
        self.climbing_textures.append(texture)
        texture = arcade.load_texture(f"{main_path}_climb1.png")
        self.climbing_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_texture_pair[0]

        # Hit box will be set based on the first image used. If you want to specify
        # a different hit box, you can do it like the code below.
        # self.set_hit_box([[-22, -64], [22, -64], [22, 28], [-22, 28]])
        self.set_hit_box(self.texture.hit_box_points)

    '''def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING

        # Climbing animation
        if self.is_on_ladder:
            self.climbing = True
        if not self.is_on_ladder and self.climbing:
            self.climbing = False
        if self.climbing and abs(self.change_y) > 1:
            self.cur_texture += 1
            if self.cur_texture > 7:
                self.cur_texture = 0
        if self.climbing:
            self.texture = self.climbing_textures[self.cur_texture // 4]
            return

        # Jumping animation
        if self.change_y > 0 and not self.is_on_ladder:
            self.texture = self.jump_texture_pair[self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.texture = self.fall_texture_pair[self.character_face_direction]
            return

        # Idle animation
        if self.change_x == 0:
            self.texture = self.idle_texture_pair[self.character_face_direction]
            return

        # Walking animation
        self.cur_texture += 1
        if self.cur_texture > 7:
            self.cur_texture = 0
        self.texture = self.walk_textures[self.cur_texture][self.character_face_direction]'''


# this is the class for creating a starting view
class InstructionView(arcade.View):
    def on_show(self):
        """ This is run once when we switch to this view """

        arcade.set_background_color(arcade.csscolor.DARK_SLATE_BLUE)

        # Reset the viewport, necessary if we have a scrolling game and we need
        # to reset the viewport back to the start so we can see what we draw.
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        # This is adding then drawing a background image
        img = arcade.load_texture('boom.png')
        arcade.draw_lrwh_rectangle_textured(0, 0, 1000, 650, img)

        # This is drawing the text
        arcade.draw_text("Super Bruv", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.BLACK, font_size=50, anchor_x="center")
        arcade.draw_text("Click to advance", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 75,
                         arcade.color.BLACK, font_size=20, anchor_x="center")
        arcade.draw_text("By Jacob.L", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 140,
                         arcade.color.BLACK, font_size=20, anchor_x="center")

    # If the player clicks the screen it will load into the game
    def on_mouse_press(self, _x, _y, _button, _modifiers):
        """ If the user presses the mouse button, start the game. """
        game_view = GameView()
        game_view.setup(num_level)
        self.window.show_view(game_view)


# game class
class GameView(arcade.View):
    """
    Main application class.
    """

    # really important things
    def __init__(self):

        # Call the parent class and set up the window
        super().__init__()

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.coordinate_list2 = None

        self.flags_list = None
        self.foreground_list = None
        self.coin_list = None
        self.wall_list = None
        self.player_list = None
        self.background_list = None
        self.lever_list = None
        self.invisible_list = None
        self.ladder_list = None
        self.test_list = None

        # Separate variable that holds the player sprite
        self.player_sprite = None

        # physics engine
        self.physics_engine = None
        self.bullet_sprite = None

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0
        self.view_top = 0
        self.view_right = 0

        self.end_of_map = 0

        # Keep track of the score
        self.score = 0
        # Lives variable
        self.lives = 3
        # level variable
        self.num_level = 1
        # lever variable
        self.lever = 0

        # New Code remove if doesnt work
        # setting up torch list
        self.torch_list = arcade.SpriteList(is_static=True)

        self.light_layer = LightLayer(SCREEN_WIDTH, SCREEN_HEIGHT)

        # Add lights to the location of the torches. We're just using hacky tweak value list here

        self.moving_light = Light(400, 300, radius=250, mode='soft')
        self.light_layer.add(self.moving_light)

        # End of new code

        self.upheld = False

        # Variables used to calculate frames per second
        self.frame_count = 0
        self.fps_start_timer = None
        self.fps = None
        # Load sounds
        self.collect_coin_sound = arcade.load_sound(":resources:sounds/coin1.wav")
        self.jump_sound = arcade.load_sound(":resources:sounds/jump1.wav")

        arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    # This is the death loop
    def died(self, message):
        print(message)
        self.player_sprite.change_y = PLAYER_JUMP_SPEED
        self.lives -= 1

        self.player_sprite.center_x = 128
        self.player_sprite.center_y = 500

    # this is the setup loop
    def setup(self, num_level):
        """ Set up the game here. Call this function to restart the game. """

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0
        self.view_top = 0
        self.view_right = 0

        # Create the Sprite lists
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()
        self.flags_list = arcade.SpriteList()
        self.foreground_list = arcade.SpriteList()
        self.bullet_sprite = arcade.SpriteList()
        self.lever_list = arcade.SpriteList()
        self.invisible_list = arcade.SpriteList()
        self.test_list = arcade.SpriteList(use_spatial_hash=True)

        # Set up the player, specifically placing it at these coordinates.
        # Set up the player, specifically placing it at these coordinates.
        self.player_sprite = PlayerCharacter()

        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)

        # --- Load in a map from the tiled editor ---

        # Name of map file to load
        map_name = f"Level_{num_level}.tmx"

        # Read in the tiled map
        my_map = arcade.tilemap.read_tmx(map_name)
        moving_platforms_layer_name = 'Moving Platforms'
        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        background_layer_name = 'Background'
        flags_layer_name = 'Flags'
        foreground_layer_name = 'Foreground'
        invisible_layer_name = 'Invisible'
        lever_layer_name = 'Lever'

        self.end_of_map = my_map.map_size.width * GRID_PIXEL_SIZE
        # -- Platforms list
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)
        # -- Moving Platforms
        moving_platforms_list = arcade.tilemap.process_layer(my_map, moving_platforms_layer_name, TILE_SCALING)
        for sprite in moving_platforms_list:
            self.wall_list.append(sprite)

        # -- other lists
        self.coin_list = arcade.tilemap.process_layer(my_map, coins_layer_name, TILE_SCALING)
        self.flags_list = arcade.tilemap.process_layer(my_map, flags_layer_name, TILE_SCALING)
        self.background_list = arcade.tilemap.process_layer(my_map, background_layer_name, TILE_SCALING)
        self.foreground_list = arcade.tilemap.process_layer(my_map, foreground_layer_name, TILE_SCALING)
        self.lever_list = arcade.tilemap.process_layer(my_map, lever_layer_name, TILE_SCALING)
        self.invisible_list = arcade.tilemap.process_layer(my_map, invisible_layer_name, TILE_SCALING)
        self.ladder_list = arcade.tilemap.process_layer(my_map, "Ladders",
                                                        TILE_SCALING,
                                                        use_spatial_hash=True)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)

        # Create the 'physics engine'
        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY,
                                                             ladders=self.ladder_list)
        self.coordinate_list2 = [[2304, 512],
                                 [2304, 640],
                                 [2304, 766],
                                 [1128, 300]]

        '''for coordinate in self.coordinate_list2:
            # Add a crate on the ground
            wall = arcade.Sprite(":resources:images/tiles/stoneCenter.png", TILE_SCALING)
            wall.position = coordinate
            self.wall_list.append(wall)'''

    # draws the level and stuff
    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # --- Calculate FPS

        fps_calculation_freq = 60
        # Once every 60 frames, calculate our FPS

        if self.frame_count % fps_calculation_freq == 0:
            # Do we have a start time?
            if self.fps_start_timer is not None:
                # Calculate FPS
                total_time = timeit.default_timer() - self.fps_start_timer
                self.fps = fps_calculation_freq / total_time
            # Reset the timer
            self.fps_start_timer = timeit.default_timer()
        # Add one to our frame count
        self.frame_count += 1

        # New Code
        # Everything that should be affected by lights in here
        with self.light_layer:

            self.torch_list.draw()
            # Draw the contents with lighting

            # Draw our sprites
            self.test_list.draw()
            self.background_list.draw()
            self.ladder_list.draw()
            self.wall_list.draw()
            self.coin_list.draw()
            self.player_list.draw()
            self.flags_list.draw()
            self.foreground_list.draw()
            self.bullet_sprite.draw()
            self.lever_list.draw()
            self.invisible_list.draw()

        self.light_layer.draw()
        # End of New code

        # Draw our important info on the screen, scrolling it with the viewport
        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 10 + self.view_left, 10 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

        cords_text_y = f"Cords y: {self.player_sprite.center_y}"
        arcade.draw_text(cords_text_y, 10 + self.view_left, 30 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

        cords_text_x = f"Cords x: {self.player_sprite.center_x}"
        arcade.draw_text(cords_text_x, 10 + self.view_left, 50 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

        lives_text = f"Lives: {self.lives}"
        arcade.draw_text(lives_text, 10 + self.view_left, 70 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

        lever_text = f"Buttons hit: {self.lever}"
        arcade.draw_text(lever_text, 10 + self.view_left, 110 + self.view_bottom,
                         arcade.csscolor.WHITE, 18)

        # draw fps
        if self.fps is not None:
            output = f"FPS: {self.fps:.0f}"
            arcade.draw_text(output, 10 + self.view_left, 90 + self.view_bottom,
                             arcade.color.WHITE, 18)

    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump(y_distance=10) and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED

        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def on_mouse_press(self, x, y, button, modifiers):
        """
        Called whenever the mouse button is clicked.
        """
        # Create a bullet
        bullet = arcade.Sprite("Sprites/bullet.png", SPRITE_SCALING_LASER)

        # Position the bullet at the player's current location
        start_x = self.player_sprite.center_x
        start_y = self.player_sprite.center_y
        bullet.center_x = start_x
        bullet.center_y = start_y

        # Get from the mouse the destination location for the bullet
        # IMPORTANT! If you have a scrolling screen, you will also need
        # to add in self.view_bottom and self.view_left.
        dest_x = x + self.view_left
        dest_y = y + self.view_bottom

        # Do math to calculate how to get the bullet to the destination.
        # Calculation the angle in radians between the start points
        # and end points. This is the angle the bullet will travel.
        x_diff = dest_x - start_x
        y_diff = dest_y - start_y
        angle = math.atan2(y_diff, x_diff)

        # Angle the bullet sprite so it doesn't look like it is flying
        # sideways.
        bullet.angle = math.degrees(angle)
        print(f"Bullet angle: {bullet.angle:.2f}")

        # Taking into account the angle, calculate our change_x
        # and change_y. Velocity is how fast the bullet travels.
        bullet.change_x = math.cos(angle) * BULLET_SPEED
        bullet.change_y = math.sin(angle) * BULLET_SPEED

        # Add the bullet to the appropriate lists
        self.bullet_sprite.append(bullet)

    # player press key this happens
    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = True
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = True
        elif key == arcade.key.R:
            self.player_sprite.center_x = 128
            self.player_sprite.center_y = 500
            if self.score > 5:
                self.score = self.score - 5
            elif self.score < 5:
                self.score = 0
        elif key == arcade.key.ESCAPE or key == arcade.key.P:
            # pass self, the current view, to preserve this view's state
            pause = PauseView(self)
            self.window.show_view(pause)
        elif key == arcade.key.KEY_6:
            self.num_level = self.num_level + 1
            self.setup(self.num_level)

        self.process_keychange()

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.UP or key == arcade.key.W:
            self.up_pressed = False
            self.jump_needs_reset = False
        elif key == arcade.key.DOWN or key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.LEFT or key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.RIGHT or key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    # this is on update, every time something changes it changes the screen
    def on_update(self, delta_time):
        """ Movement and game logic """
        # Call update on all sprites
        self.bullet_sprite.update()

        # Loop through each bullet
        for bullet in self.bullet_sprite:

            # Check this bullet to see if it hit a coin
            hit_list = arcade.check_for_collision_with_list(bullet, self.coin_list)

            hit_list2 = arcade.check_for_collision_with_list(bullet, self.wall_list)

            hit_list3 = arcade.check_for_collision_with_list(bullet, self.lever_list)
            # If it did, get rid of the bullet
            if len(hit_list) > 0:
                bullet.remove_from_sprite_lists()

            if len(hit_list2) > 0:
                bullet.remove_from_sprite_lists()

            if len(hit_list3) > 0:
                bullet.remove_from_sprite_lists()

            # For every coin we hit, add to the score and remove the coin
            for coin in hit_list:
                coin.remove_from_sprite_lists()
                self.score += 1

            for lever in hit_list3:
                lever.remove_from_sprite_lists()
                self.lever += 1
                '''if self.lever == 1:
                    remove_sprite(self.coordinate_list2)
                    self.coordinate_list2.clear()'''

            # If the bullet flies off-screen, remove it.
            if bullet.bottom > 800 or bullet.top < 0 or bullet.right < 0 or bullet.left > 7000:
                bullet.remove_from_sprite_lists()

        # moving the light at the same place as the player
        self.moving_light.position = (
            self.player_sprite.center_x,
            self.player_sprite.center_y
        )

        # this is what happens to player when it respawns
        if self.lives >= 0 and self.player_sprite.center_y < -1000:
            self.died("You fell out of the world")
        elif self.lives <= 0:
            self.lives = 3
            self.setup(self.num_level)

        # Move the player with the physics engine
        self.physics_engine.update()

        # Update animations
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = False
        else:
            self.player_sprite.can_jump = True

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        self.coin_list.update_animation(delta_time)
        self.background_list.update_animation(delta_time)
        self.player_list.update_animation(delta_time)

        self.wall_list.update()

        # See if the moving wall hit a boundary and needs to reverse direction.
        for wall in self.wall_list:

            if wall.boundary_right and wall.right > wall.boundary_right and wall.change_x > 0:
                wall.change_x *= -1
            if wall.boundary_left and wall.left < wall.boundary_left and wall.change_x < 0:
                wall.change_x *= -1
            if wall.boundary_top and wall.top > wall.boundary_top and wall.change_y > 0:
                wall.change_y *= -1
            if wall.boundary_bottom and wall.bottom < wall.boundary_bottom and wall.change_y < 0:
                wall.change_y *= -1

        # See if we hit any coins/flag
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)
        flag_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.flags_list)
        # lever_hit_list = arcade.check_for_collision_with_list(self.bullet_sprite,
        #                                                     self.lever_list)

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 1

        for flags in flag_hit_list:
            flags.remove_from_sprite_lists()
            # if there is another level change to it when hit a flag
            try:
                self.num_level = self.num_level + 1
                self.setup(self.num_level)
            # if no more levels quit the game
            except:
                print("ha ha ha, I ran out of time to make more levels")
                exit()
        # --- Manage Scrolling ---

        # Track if we need to change the viewport

        # for lever in lever_hit_list:
        #    lever.remove_from_sprite_lists()

        changed = False

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed = True

        if changed:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


# this is what happens when the player pauses the game
class PauseView(arcade.View):
    def __init__(self, game_view):
        super().__init__()
        self.game_view = game_view

    def on_show(self):
        # background = orange
        arcade.set_background_color(arcade.color.ORANGE)

    def on_draw(self):
        arcade.start_render()

        # Draw player, for effect, on pause screen.
        # The previous View (GameView) was passed in
        # and saved in self.game_view.
        player_sprite = self.game_view.player_sprite
        # player_sprite.draw()

        # draw an orange filter over him

        arcade.draw_lrtb_rectangle_filled(left=player_sprite.left,
                                          right=player_sprite.right,
                                          top=player_sprite.top,
                                          bottom=player_sprite.bottom,
                                          color=arcade.color.ORANGE + (200,))

        arcade.draw_text("PAUSED", player_sprite.left, player_sprite.top + 40,
                         arcade.color.BLACK, font_size=50, anchor_x="center")

        # Show tip to return or reset
        arcade.draw_text("Press Esc. to return",
                         player_sprite.left,
                         player_sprite.top,
                         arcade.color.BLACK,
                         font_size=20,
                         anchor_x="center")
        arcade.draw_text("Press Enter to reset",
                         player_sprite.left,
                         player_sprite.top - 40,
                         arcade.color.BLACK,
                         font_size=15,
                         anchor_x="center")

    def on_key_press(self, key, _modifiers):
        if key == arcade.key.ESCAPE:  # resume game
            self.window.show_view(self.game_view)
            arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

        elif key == arcade.key.ENTER:  # reset game
            self.window.show_view(InstructionView())


def main():
    """ Main method """
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
    start_view = InstructionView()
    window.show_view(start_view)
    arcade.run()


if __name__ == "__main__":
    main()
