import arcade
from player import *
from enemies import *
from terrain import *
from items import *
import pyglet
from debug import *
import arcade.gui
import timeit
import time
from physics import PhysicsEngine
import physics
from arcade.gui import UIManager
import random
import inspect
from perf_stats import *

SW, SH = 832, 768
SCALE = 1
GRAVITY = 1.5
JUMP_SPEED = 24
LEFT_VIEW_MARGIN = 384
RIGHT_VIEW_MARGIN = 384
TOP_VIEW_MARGIN = 300
BOTTOM_VIEW_MARGIN = 300
TOP_VIEW_CHANGE = 64
BOTTOM_VIEW_CHANGE = 64
VIEW_CHANGE = 128
BLOCK_SCALE = .5
right = 1
left = -1
PLAYER_SPEED = 4
FPS = 60

perf = FpsCounter(0, 768)


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SW, SH, "Sharpthrow Shawn")
        arcade.set_background_color(arcade.color.CHARCOAL)
        self.player = None
        self.players = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.controls = {}
        self.player_speed = PLAYER_SPEED
        self.ground_list = None
        self.keys_pressed = []
        self.set_vsync(True)
        self.right_view = SW
        self.left_view = 0
        self.top_view = SH
        self.bottom_view = 0
        self.left_boundary = 0
        self.right_boundary = 0
        self.top_boundary = 0
        self.bottom_boundary = 0
        self.game_over = False
        self.score = 0
        self.mouse_pos = (0, 0)
        self.show_trail = False
        self.weapon_traject: physics.ProjectileTrajectory = None
        self.trail_loaded = False
        # Time for on_update
        self.processing_time = 0
        self.mouse_x, self.mouse_y = 0, 0
        # mc = pyglet.image.load("resources/sprites/mouse.png")
        # m = pyglet.window.ImageMouseCursor(mc)
        # self.set_mouse_cursor(m)
        # arcade.load_texture('resources/sprites/mouse.png')

        # Time for on_draw
        self.draw_time = 0
        self.cursor = arcade.Sprite("resources/sprites/item/knife.png", .8)
        self.cursor.angle = 80
        self.set_update_rate(1/FPS)
        # Variables used to calculate frames per second
        self.frame_count = 0
        self.fps_start_timer = None
        self.fps = None
        self.setup()
        self.set_mouse_visible(False)
        self.tri = None
        self.knife_collisions = False

    def setup(self):
        # create UI

        # create the player
        self.player = Player(1000, 96, SCALE)
        self.players.append(self.player)

        self.controls = {
            'a': {'func': self.player.speed_x, 'param': -self.player_speed},
            'd': {'func': self.player.speed_x, 'param': self.player_speed}
        }
        self.slow = {
            'a': {'func': self.player.speed_x, 'param': -.5},
            'd': {'func': self.player.speed_x, 'param': .5}
                     }

        self.set_level("level_1")

        # setup the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.ground_list, GRAVITY)
        self.physics_engine.disable_multi_jump()
        # set initial texture
        self.player.update_animation()
        self.player.weapon = ThrowingKnife(self.player)
        self.physics = PhysicsEngine(self.player, self.ground_list)
        self.max_len = self.player.max_hp * 10

        self.cursor_pos = self._mouse_x, self._mouse_y
        self.show_math = False


    def on_draw(self):
        start_time = timeit.default_timer()


        # --- Calculate FPS
        fps_calculation_freq = FPS
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
        # draw score
        # arcade.draw_text(f"Score: {self.score}", self.left_view + SW / 2 - 10, self.top_view - 50, arcade.color.WHITE,
        #                  20)
        # # draw player pos and mouse pos
        # arcade.draw_text(f"X: {self.player.center_x}, Y:{self.player.center_y}", self.right_view - 10,
        #                  self.top_view - 40, arcade.color.BLACK, 12)
        # output = f"Mouse_Pos: {self.mouse_pos}"
        # arcade.draw_text(output, self.right_view - 10, self.top_view - 20,
        #                  arcade.color.BLACK, 12)


        if self.player.weapons:
            self.player.weapons.draw()
        if self.tri and self.show_math:
            self.set_triangle()
        if self.player.old_weapons:
            self.player.old_weapons.draw()

        if self.trail_loaded:
            self.weapon_traject.draw()

        self.players.draw()
        self.ground_list.draw()

        # calculate length of health bar
        box_len = self.player.hp * 10
        # draw the player's health bar

        arcade.draw_lrtb_rectangle_filled(self.left_view + 25, self.left_view + 25 + self.max_len, self.bottom_view + 35,
                                          self.bottom_view + 17.5, arcade.color.WHITE_SMOKE)
        arcade.draw_lrtb_rectangle_filled(self.left_view + 25, self.left_view + 25 + box_len, self.bottom_view + 35,
                                          self.bottom_view + 17.5, arcade.color.IMPERIAL_RED)
        arcade.draw_text("HP", self.left_view + 2, self.bottom_view + 17.5, arcade.color.BLACK, 15)

        output = f"Processing time: {self.processing_time:.3f}"
        arcade.draw_text(output, self.left_view + 10, self.top_view - 25, arcade.color.BLACK, 18)

        output = f"Drawing time: {self.draw_time:.3f}"
        arcade.draw_text(output, self.left_view + 10, self.top_view - 50, arcade.color.BLACK, 18)

        if self.fps is not None:
            output = f"FPS: {self.fps:.0f}"
            arcade.draw_text(output, self.left_view + 10, self.top_view - 75, arcade.color.BLACK, 18)
        self.cursor.draw()
        # Stop the draw timer, and calculate total on_draw time.
        self.draw_time = timeit.default_timer() - start_time

    def on_update(self, delta_time: float):
        start_time = timeit.default_timer()
        # Start timing how long this takes
        changed = False
        x = self.mouse_x + (self.right_view - SW)
        y = self.mouse_y + (self.top_view - SH)
        self.mouse_pos = (x, y)
        self.cursor.position = self.mouse_pos

        if self.player.weapons:
            for knife in self.player.weapons:
                knives = arcade.check_for_collision_with_list(knife, self.ground_list)
                if knives:
                    knife.thrown = False
                    self.player.old_weapons.append(knife)
                    if self.knife_collisions:
                        self.ground_list.append(knife)
                    self.player.weapons.remove(knife)

        if not self.game_over:
            self.player.update()
            self.player.update_animation()
            self.physics_engine.update()

        # screen scrolling system
        changed = self.scroll_screen()
        self.set_projectile()
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
            self.right_view = self.left_view + SW

        # if view has changed, update the window accordingly
        if changed:
            arcade.set_viewport(self.left_view, self.right_view, self.bottom_view, self.top_view)
        self.key_change()
        self.processing_time = timeit.default_timer() - start_time

    def key_change(self):
        if self.keys_pressed:
            key = self.keys_pressed[0]
            f = self.controls[key]['func']
            f(self.controls[key]['param'])
            # if self.player.can_move:
            #     key = self.keys_pressed[0]
            #     f = self.controls[key]['func']
            #     f(self.controls[key]['param'])
            # else:
            #     # key = self.keys_pressed[0]
            #     # f = self.slow[key]['func']
            #     # f(self.slow[key]['param'])
            #     self.player.change_x = 0

        else:
            self.player.speed_x(0)


    def get_screen_boundaries(self):
        left_bound = self.left_view + LEFT_VIEW_MARGIN
        right_bound = self.right_view - RIGHT_VIEW_MARGIN
        top_bound = self.top_view - TOP_VIEW_MARGIN
        bottom_bound = self.bottom_view + BOTTOM_VIEW_MARGIN
        return right_bound, left_bound, top_bound, bottom_bound


    def scroll_screen(self):
        right_boundary, left_boundary, top_boundary, bottom_boundary = self.get_screen_boundaries()
        x = False
        if self.player.left < left_boundary:
            self.left_view -= left_boundary - self.player.left
            self.right_view = SW + self.left_view
            x = True
        elif self.player.right > right_boundary:
            self.left_view += self.player.right - right_boundary
            self.right_view = SW + self.left_view
            x = True
        if self.player.top > top_boundary:
            self.bottom_view += self.player.top - top_boundary
            self.top_view = SH + self.bottom_view
            x = True
        elif self.player.bottom < bottom_boundary:
            self.bottom_view -= bottom_boundary - self.player.bottom
            self.top_view = self.bottom_view + SH
            x = True
        if x:
            return True
        else:
            return False



    def set_level(self, map):
        map_name = f"resources/maps/{map}.tmx"  # map file
        # read the map
        level_map = arcade.tilemap.read_tmx(map_name)
        # generate the tiles for the ground, and for ladders
        self.ground_list = arcade.tilemap.process_layer(map_object=level_map, layer_name="ground", scaling=BLOCK_SCALE,
                                                        use_spatial_hash=True, hit_box_algorithm="Simple")


    def on_key_press(self, symbol: int, modifiers: int):
        key = chr(symbol)
        # for each key pressed, add it to the current keys pressed
        if key in list(self.controls.keys()):
            self.keys_pressed.insert(0, key)


        # if player presses space, and jump conditions are met, jump
        if symbol == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.physics_engine.jump(JUMP_SPEED)
        elif symbol == arcade.key.P:
            print(f"player pos: {self.player.position}")
            print(f"top_view: {self.top_view}")
        elif symbol == arcade.key.M:
            if self.show_math:
                self.show_math = False
            else:
                self.show_math = True
        elif symbol == arcade.key.K:
            print(len(self.player.old_weapons))
            for i, knife in enumerate(self.player.old_weapons):
                print(i)
                knife.kill()
        elif symbol == arcade.key.C:
            if self.knife_collisions:
                self.knife_collisions = False
            else:
                self.knife_collisions = True


    def on_key_release(self, symbol: int, modifiers: int):
        key = chr(symbol)
        # removes keys from keys_pressed if they are no longer pressed
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)



    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        # shoot the knife on click
        if button == 1:
            x = x + (self.right_view - SW)
            y = y + (self.top_view - SH)
            self.player.attack(x, y)


        # show the knife trajectory while holding right click
        elif button == 4:
            x = x + (self.right_view - SW)
            y = y + (self.top_view - SH)
            self.show_trail = True
            self.tri = True
            self.set_projectile()
            self.player.can_move = False
            self.player.change_x = 0


    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        # throw the knife once right click is released and hide the trajectory
        self.tri = False
        if button == 4:
            x = x + (self.right_view - SW)
            y = y + (self.top_view - SH)
            self.player.attack(x, y)
            self.show_trail = False
            self.trail_loaded = False
            self.player.can_move = True

    # update position of
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x, self.mouse_y = x, y
        x = x + (self.right_view - SW)
        y = y + (self.top_view - SH)

        self.mouse_pos = (x, y)

    def set_projectile(self):
        if self.show_trail:
            x, y = self.mouse_pos
            self.weapon_traject = self.physics.get_trajectory(x, y)
            self.trail_loaded = True
        else:
            self.trail_loaded = False

    def set_triangle(self):
        x, y = self.mouse_pos
        direction = right
        if x < self.player.center_x:
            direction = left

        tri = physics.Triangle(self.player.center_x, x, self.player.center_y, y, direction * 100)
        ang = tri.get_angle()
        arcade.draw_text(f"{ang: .0f}", self.player.center_x, self.player.top, arcade.color.RED, 12)
        tri.draw()



def main():
    game = Game()
    arcade.run()


if __name__ == '__main__':
    main()