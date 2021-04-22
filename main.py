import arcade
from player import *
from enemies import *
from terrain import *
from items import *
from debug import *
import arcade.gui
import timeit
from arcade.gui import UIManager
import random
import inspect
SW, SH = 832, 768
SCALE = 1
GRAVITY = 1.5
JUMP_SPEED = 24
LEFT_VIEW_MARGIN = 384
RIGHT_VIEW_MARGIN = 384
TOP_VIEW_MARGIN = 300
BOTTOM_VIEW_MARGIN = 300
TOP_VIEW_CHANGE = 128
VIEW_CHANGE = 128
BLOCK_SCALE = .5
right = 0
show_traject = False
PLAYER_SPEED = 4

class Button(arcade.gui.UIFlatButton):

    def on_click(self):
        global show_traject
        if show_traject:
            show_traject = False
        else:
            show_traject = True



class Game(arcade.Window):
    def __init__(self):
        super().__init__(SW, SH, "Sharpthrow Shawn")
        arcade.set_background_color(arcade.color.SPANISH_SKY_BLUE)
        self.player = None
        self.players = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.controls = {"a": -PLAYER_SPEED, "d": PLAYER_SPEED, "w": 3, "s": -3}
        self.jump = 32
        self.ui_manager = UIManager()
        self.ground_list = None
        self.keys_pressed = []
        self.math_stats = False
        self.perf_stats = False
        # self.goblin = Goblin(800, 125)
        # self.enemies.append(self.goblin)
        # self.goblin.update_animation()
        # self.hurt_sound = arcade.Sound("resources/sounds/oof.wav")
        # self.current_player = self.hurt_sound.play(0)
        self.right_view = SW
        self.left_view = 0
        self.top_view = SH
        self.bottom_view = 0
        self.set_vsync(True)
        self.left_boundary = 0
        self.right_boundary = 0
        self.top_boundary = 0
        self.bottom_boundary = 0
        self.ladder_list = None
        self.frame = 0
        self.setup()
        self.game_over = False
        self.debugger = Debugger(self)
        self.local_debugger = LocalDebugger()
        self.debug = self.debugger.out
        self.l_debug = self.local_debugger.out
        self.debugger.disable()
        self.local_debugger.disable()
        self.score = 0
        self.mouse_pos = (0, 0)

        # --- Variables for our statistics

        # Time for on_update
        self.processing_time = 0

        # Time for on_draw
        self.draw_time = 0

        # Variables used to calculate frames per second
        self.frame_count = 0
        self.fps_start_timer = None
        self.fps = None

        # self.d = Debug(self)


    def setup(self):
        # create UI
        button_img = arcade.load_texture((':resources:gui_basic_assets/red_button_normal.png'))
        button = arcade.gui.UIFlatButton("Toggle Stats", self.left_view + 100, self.top_view - 200, 50, 20)
        self.ui_manager.add_ui_element(button)
        # create the player
        self.player = Player(1000, 96, SCALE)
        self.players.append(self.player)
        # self.enemies.append(Goblin(2000, 320))
        # self.enemies.update_animation()
        map_name = "resources/maps/level_1.tmx"  # map file
        # read the map
        level_map = arcade.tilemap.read_tmx(map_name)
        # generate the tiles for the ground, and for ladders
        self.ground_list = arcade.tilemap.process_layer(map_object=level_map, layer_name="ground", scaling=BLOCK_SCALE, use_spatial_hash=True, hit_box_algorithm= "Simple")
        # self.ladder_list = arcade.tilemap.process_layer(map_object=level_map, layer_name="ladders", scaling=BLOCK_SCALE, use_spatial_hash=True)

        # setup the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.ground_list, GRAVITY)
        self.physics_engine.disable_multi_jump()
        # self.enemy_physics_engine = EnemyPhysics(self.enemies, self.player, self.ground_list, 4)
        # set initial texture
        self.player.update_animation()
        # set the players weapon
        # self.player.weapon = Dagger(self.player.right, self.player.center_y, self.player)
        self.player.weapon = ThrowingKnife(self.player)

    def on_draw(self):
        # Start timing how long this takes
        start_time = timeit.default_timer()

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
        arcade.start_render()
        arcade.draw_text(f"Score: {self.score}", self.left_view + SW/2 - 10, self.top_view - 50, arcade.color.WHITE, 20)
        # draw all sprites to screen
        arcade.draw_text(f"X: {self.player.center_x}, Y:{self.player.center_y}", self.right_view - 10, self.top_view - 40, arcade.color.BLACK, 12, anchor_x="right")
        arcade.draw_text(f"Mouse_Pos: {self.mouse_pos}", self.right_view - 10, self.top_view - 20,
                         arcade.color.BLACK, 12, anchor_x="right")

        self.ground_list.draw()
        if self.player.weapons:
            self.player.weapons.draw()
            if self.math_stats:
                p = self.player.weapons[-1].tri
                p2 = self.player.weapons[-1].trajectory
                a = self.player.weapons[-1].ang
                arcade.draw_polygon_outline(p, arcade.color.PURPLE, 2)
                arcade.draw_points(p2, arcade.color.GOLD, 3)
                self.player.draw_hit_box(arcade.color.RED, 1)
                arcade.draw_text(f"{a:.1f}°", self.player.center_x, self.player.center_y + 40, arcade.color.RED, 8, anchor_x="center")
        # if self.player.attacking:
        # self.player.weapon.draw()
        self.players.draw()
        # calculate length of health bar
        box_len = self.player.hp * 10
        max_len = self.player.max_hp * 10
        # self.d.out('max_len')
        # draw the player's health bar
        arcade.draw_lrtb_rectangle_filled(self.left_view + 25, self.left_view + 25 + max_len, self.top_view - 17.5,
                                          self.top_view - 35, arcade.color.WHITE_SMOKE)
        arcade.draw_lrtb_rectangle_filled(self.left_view + 25, self.left_view + 25 + box_len, self.top_view - 17.5, self.top_view - 35, arcade.color.RED_DEVIL)
        arcade.draw_text("HP", self.left_view + max_len + 30, self.top_view - 40, arcade.color.BLACK, 20)

        if self.perf_stats:
            # Display timings
            output = f"Processing time: {self.processing_time:.3f}"
            arcade.draw_text(output, self.left_view + 20, self.top_view - 75 - 25, arcade.color.BLACK, 18)

            output = f"Drawing time: {self.draw_time:.3f}"
            arcade.draw_text(output, self.left_view + 20, self.top_view - 75 - 50, arcade.color.BLACK, 18)

            if self.fps is not None:
                output = f"FPS: {self.fps:.0f}"
                arcade.draw_text(output, self.left_view + 20, self.top_view - 75, arcade.color.BLACK, 18)

        # Stop the draw timer, and calculate total on_draw time.
        self.draw_time = timeit.default_timer() - start_time

    def on_update(self, delta_time: float):
        # Start timing how long this takes
        start_time = timeit.default_timer()
        if self.frame > 60:
            self.frame = 0
        # set screen scroll boundaries
        left_boundary = self.left_view + LEFT_VIEW_MARGIN
        right_boundary = self.left_view + SW - RIGHT_VIEW_MARGIN
        top_boundary = self.bottom_view + SH - TOP_VIEW_MARGIN
        bottom_boundary = self.bottom_view + BOTTOM_VIEW_MARGIN
        changed = False


        if self.player.weapons:
            for knife in self.player.weapons:
                knives = arcade.check_for_collision_with_list(knife, self.ground_list)
                if knives:
                    knife.thrown = False
        if self.keys_pressed:
            for key in reversed(self.keys_pressed):
                # move left/right
                if key in 'ws':
                    if self.physics_engine.is_on_ladder():
                        self.player.change_y = self.controls[key]
                # move up/down (on ladders)
                if key in 'ad':
                    if self.physics_engine.is_on_ladder() and self.player.change_y != 0:
                        self.player.change_x = self.controls[key] / 10
                    else:
                        self.player.change_x = self.controls[key]
        else:
            self.player.change_x = 0


        if not self.game_over:
            # self.enemy_physics_engine.update()
            self.player.update_animation()
            # self.enemies.update_animation()
            self.player.update()
            self.physics_engine.update()


        # screen scrolling system
        # check if player is close enough to edges to scroll screen
        if self.player.left < left_boundary:
            self.left_view -= left_boundary - self.player.left
            self.right_view = SW + self.left_view

            changed = True
        elif self.player.right > right_boundary:
            self.left_view += self.player.right - right_boundary
            self.right_view = SW + self.left_view
            changed = True
        if self.player.top > top_boundary:
            self.bottom_view += self.player.top - top_boundary
            self.top_view = SH + self.bottom_view
            changed = True
        elif self.player.bottom < bottom_boundary:
            self.bottom_view -= bottom_boundary - self.player.bottom
            self.top_view = self.bottom_view + SH
            changed = True
        # prevent the view from going below or to the side of the level
        if self.bottom_view < 0:
            self.bottom_view = 0
            self.top_view = self.bottom_view + SH
        elif self.top_view > 1230:
            self.top_view = 1230
            self.bottom_view = self.top_view - SH
        if self.left_view + SW >= 2550:
            self.left_view = 2550 - SW
            self.right_view = self.left_view + SW
        elif self.left_view < 0:
            self.left_view = 0
            self.right_view = self.left_view +SW

        # if view has changed, update the window accordingly
        if changed:
            arcade.set_viewport(self.left_view, self.right_view, self.bottom_view, self.top_view)



        # Stop the draw timer, and calculate total on_draw time
        self.processing_time = timeit.default_timer() - start_time

    def on_key_press(self, symbol: int, modifiers: int):
        key = chr(symbol)
        # for each key pressed, add it to the current keys pressed
        if key in list(self.controls.keys()):
            self.keys_pressed.insert(0, key)
        # if player presses space, and jump conditions are met, jump
        elif symbol == self.jump:
            if self.physics_engine.can_jump():
                if self.physics_engine.is_on_ladder():
                    if 0 > self.player.change_x > 0:
                        self.physics_engine.jump(JUMP_SPEED)
                else:
                    self.physics_engine.jump(JUMP_SPEED)
        elif symbol == arcade.key.P:
            if self.perf_stats:
                self.perf_stats = False
            else:
                self.perf_stats = True
        elif symbol == arcade.key.M:
            if self.math_stats:
                self.math_stats = False
            else:
                self.math_stats = True
        # print(self.keys_pressed)
        pass

    def on_key_release(self, symbol: int, modifiers: int):
        key = chr(symbol)
        # removes keys from keys_pressed if they are no longer pressed
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
        if key in 'ws':
            self.player.change_y = 0
        # if symbol == self.jump:
        #     self.player.change_y = 0
            pass

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        # tell player to attack

        # self.player.should_attack = True
        x = x + (self.right_view - SW)
        y = y + (self.top_view - SH)
        self.player.attack(x ,y)
        # kill goblin if player is within range and attacks
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        x = x + (self.right_view - SW)
        y = y + (self.top_view - SH)
        self.mouse_pos = (x, y)

# x = inspect.getouterframes(inspect.currentframe())[0][0].f_locals
# print(x['Debugger'].enabled)


def main():
    game = Game()
    arcade.run()


if __name__ == '__main__':
    main()