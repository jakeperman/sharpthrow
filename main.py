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
from jarcade.shapes import Triangle, StaticTriangle
from arcade.gui import UIManager
import random
import inspect
from perf_stats import *
from level_select import MyView
import level_select
from level_load import load_map
from item_load import load_knife
import item_load
from screen_scroll import ScrollManager

SW, SH = 832, 768
SCALE = 1
GRAVITY = 1.5
JUMP_SPEED = 35
LEFT_VIEW_MARGIN = 416
RIGHT_VIEW_MARGIN = 416
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
        self.set_vsync(True)
        self.set_update_rate(1 / FPS)
        self.set_mouse_visible(True)
        arcade.set_background_color(arcade.color.CHARCOAL)
        self.player = None
        self.players = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.controls = {}
        self.player_speed = PLAYER_SPEED
        self.ground_list = arcade.SpriteList()
        self.target_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()
        self.surface_list = arcade.SpriteList()
        self.keys_pressed = []

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
        self.weapon_traject = None
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

        # Variables used to calculate frames per second
        self.frame_count = 0
        self.fps_start_timer = None
        self.fps = None

        self.tri = None
        self.knife_collisions = True

        self.knives_to_load = [load_knife(knife) for knife in item_load.knives]
        self.knives = {knife.name: knife for knife in self.knives_to_load}
        self.set_level("test")
        self.scroll_manager = ScrollManager(self)
        self.scroll_manager.set_view_change_margins(right=RIGHT_VIEW_MARGIN, left=LEFT_VIEW_MARGIN, top=TOP_VIEW_MARGIN, bottom=BOTTOM_VIEW_MARGIN)

        # physics.TimeTrajectory(10, 10, 35, 12, 3, 1654, .5)
        # physics.Triangle(10, 25, 4, 16, 100)
        self.setup()

    def setup(self):
        # create UI

        # self.ui_manager.add_ui_element(self.button)
        # create the player
        self.load_level(self.map)
        self.players = arcade.SpriteList()
        self.player = Player(self.map.spawn_x, self.map.spawn_y, SCALE)
        self.player.weapon_type = ThrowingKnife
        self.player.weapon_stats = self.knives['starter']
        self.players.append(self.player)

        self.controls = {
            'a': {'func': self.player.speed_x, 'param': -self.player_speed},
            'd': {'func': self.player.speed_x, 'param': self.player_speed}
        }

        self.slow = {
            'a': {'func': self.player.speed_x, 'param': -.5},
            'd': {'func': self.player.speed_x, 'param': .5}
                     }

        # setup the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.surface_list, GRAVITY)
        self.physics_engine.disable_multi_jump()
        # set initial texture
        self.player.update_animation()
        self.physics = PhysicsEngine(self.player, self.surface_list, self.target_list, 3, self.map)
        self.max_len = self.player.max_hp * 10
        self.show_math = False

        self.scroll_manager.set_view_max(right=self.map.x_bound, left=0, top=self.map.y_bound, bottom=0)

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
        # self.ui_manager.on_draw()
        # draw score
        # arcade.draw_text(f"Score: {self.score}", self.left_view + SW / 2 - 10, self.top_view - 50, arcade.color.WHITE,
        #                  20)
        # # draw player pos and mouse pos
        # arcade.draw_text(f"X: {self.player.center_x}, Y:{self.player.center_y}", self.right_view - 10,
        #                  self.top_view - 40, arcade.color.BLACK, 12)
        # output = f"Mouse_Pos: {self.mouse_pos}"
        # arcade.draw_text(output, self.right_view - 10, self.top_view - 20,
        #                  arcade.color.BLACK, 12)

        # tm = time.perf_counter()
        if self.player.weapons:
            self.player.weapons.draw()
            # self.player.weapons[-1].trajectory.draw()
        if self.tri and self.show_math:
            # self.set_triangle()
            self.draw_traject_triangle()
        if self.player.old_weapons:
            self.player.old_weapons.draw()

        self.players.draw()
        self.surface_list.draw()
        self.target_list.draw()
        self.wall_list.draw()
        self.ground_list.draw()
        if self.trail_loaded:
            self.physics.draw_trajectory(self.weapon_traject)
            # self.weapon_traject.draw()
        # print("time to draw:", time.perf_counter() - tm)

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
        # self.cursor.draw()
        # Stop the draw timer, and calculate total on_draw time.
        self.draw_time = timeit.default_timer() - start_time

    def on_update(self, delta_time: float):
        start_time = timeit.default_timer()
        # Start timing how long this takes
        # self.ui_manager.on_update(delta_time)

        # x = self.mouse_x + (self.right_view - SW)
        # y = self.mouse_y + (self.top_view - SH)
        # self.mouse_pos = (x, y)
        # self.cursor.position = self.actual_pos((self.mouse_x, self.mouse_y))
        # self.button.update_pos(self.right_view - 300, self.top_view - 300)

        if self.player.weapons:
            # x = time.perf_count er()
            # print(len(self.player.weapons))
            # print("player weapons:", len(self.player.weapons))
            for knife in self.player.weapons:

                # hit_walls = arcade.check_for_collision_with_list(knife, self.wall_list)

                if self.map.collisions == "block":
                    hits = arcade.check_for_collision_with_list(knife, self.surface_list)
                else:
                    hits = arcade.check_for_collision_with_list(knife, self.target_list)

                hit_knives = arcade.check_for_collision_with_list(knife, self.player.old_weapons)
                if hits or hit_knives:
                    # knife.hit_sound.play(1)
                    # knife.thrown = False
                    self.player.old_weapons.append(knife)
                    self.player.weapons.remove(knife)
                    self.physics.remove_object(knife)
                    if self.knife_collisions:
                        self.surface_list.append(knife)
                

            # print(f"knife time: {time.perf_counter() - x}")

        self.player.update()
        self.player.update_animation()
        # self.physics_engine.update()
        self.physics.update()
        self.scroll_manager.update()
        if self.map.name == 'tutorial' and self.player.center_y < 200:
            self.setup()
        # screen scrolling system
        # changed = self.scroll_screen()
        self.set_projectile()

        self.key_change()
        self.processing_time = timeit.default_timer() - start_time
        self.right_view, self.left_view, self.top_view, self.bottom_view = self.scroll_manager.get_views()

    def key_change(self):
        if self.keys_pressed:
            key = self.keys_pressed[0]
            f = self.controls[key]['func']
            f(self.controls[key]['param'])

        else:
            self.player.speed_x(0)

    def actual_x(self, x):
        return x + (self.right_view - SW)

    def actual_y(self, y):
        return y + self.top_view - SH

    def actual_pos(self, pos):
        new_x = self.actual_x(pos[0])
        new_y = self.actual_y((pos[1]))
        return new_x, new_y

    def set_level(self, map_name):
        self.map = load_map(map_name)


    def load_level(self, level):
        map_name = f"resources/maps/{level.name}.tmx"
        level_map = arcade.tilemap.read_tmx(map_name)
        # generate the tiles for the ground, and for ladders
        self.ground_list = arcade.tilemap.process_layer(map_object=level_map, layer_name="ground", scaling=BLOCK_SCALE,
                                                         use_spatial_hash=True, hit_box_algorithm="Simple")
        self.surface_list = arcade.tilemap.process_layer(map_object=level_map, layer_name="surface", scaling=BLOCK_SCALE, use_spatial_hash=True)
        self.target_list = arcade.tilemap.process_layer(map_object=level_map, layer_name="targets", scaling=BLOCK_SCALE,
                                                        use_spatial_hash=True)
        self.wall_list = arcade.tilemap.process_layer(map_object=level_map, layer_name="walls", scaling=BLOCK_SCALE,
                                                      use_spatial_hash=True)


    def on_key_press(self, symbol: int, modifiers: int):
        key = chr(symbol)
        # for each key pressed, add it to the current keys pressed
        if key in list(self.controls.keys()):
            self.keys_pressed.insert(0, key)


        # if player presses space, and jump conditions are met, jump
        elif symbol == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.physics.jump(JUMP_SPEED)
        elif symbol == arcade.key.P:
            print(f"player pos: {self.player.position}")
            self.scroll_manager.output_values()
        elif symbol == arcade.key.M:
            if self.show_math:
                self.show_math = False
            else:
                self.show_math = True
        elif symbol == arcade.key.K:
            kills = []
            for i, knife in enumerate(self.player.old_weapons):
                kills.append(knife)
            for k in kills:
                k.kill()
        elif symbol == arcade.key.C:
            if self.knife_collisions:
                self.knife_collisions = False
            else:
                self.knife_collisions = True

        elif symbol == arcade.key.N:
            print(f"Number of knives: {len(self.player.old_weapons)}")
        elif symbol == arcade.key.R:
            self.setup()
        elif symbol == arcade.key.E:
            print(f"end_angle: {self.player.weapons[-1].angle}")
        # elif symbol == arcade.key.L:
        #     self.window.show_view(MyView())
        elif key == "0":
            self.set_level("tutorial")
            self.setup()
        elif key == "9":
            self.set_level("test")
            self.setup()
        elif key == "1":
            self.player.weapon_stats = self.knives['starter']
        elif key == "2":
            self.player.weapon_stats = self.knives['basic']
        elif key == "3":
            self.player.weapon_stats = self.knives['pro']

    def on_key_release(self, symbol: int, modifiers: int):
        key = chr(symbol)
        # removes keys from keys_pressed if they are no longer pressed
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)

        if key == arcade.key.SPACE:
            self.player.change_y *= -.5



    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        # shoot the knife on click
        if button == 1:
            x = x + (self.right_view - SW)
            y = y + (self.top_view - SH)
            self.player.attack(x, y)
            # self.physics.throw_object(obj, x, y, 50)
            # self.weapon_traject = self.player.weapon.trajectory
            # self.trail_loaded = True
            # self.show_trail = True


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

        if button == 4:
            x = x + (self.right_view - SW)
            y = y + (self.top_view - SH)
            self.player.attack(x, y)
            self.show_trail = False
            self.trail_loaded = False
            self.player.can_move = True
            self.tri = False

    # update position of
    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        self.mouse_x, self.mouse_y = x, y
        x = x + (self.right_view - SW)
        y = y + (self.top_view - SH)

        self.mouse_pos = (x, y)

    def set_projectile(self):
        if self.show_trail:
            x, y = self.mouse_pos
            self.weapon_traject = self.physics.get_knife_trajectory_from_player(x, y, self.player.get_weapon())
            # self.weapon_traject = self.physics.get_knife_trajectory_from_player(x, y, obj)
            self.trail_loaded = True
        else:
            self.trail_loaded = False

    def set_triangle(self):
        x, y = self.mouse_pos
        direction = right
        if x < self.player.center_x:
            direction = left
        tri = StaticTriangle(self.player.center_x, x, self.player.center_y, y, direction * 100)
        ang = tri.get_angle()
        arcade.draw_text(f"{ang: .0f}", self.player.center_x, self.player.top, arcade.color.RED, 12)
        tri.draw()

    def draw_traject_triangle(self):
        x, y = self.mouse_pos
        knife = self.player.get_weapon()
        trajectory = self.physics.get_knife_trajectory_from_player(x, y, knife, .25)
        mid_point = trajectory.get_max_point()
        start_point = trajectory.x0, trajectory.y0
        # trajectory.trim()
        end_point = trajectory.get_point_of_impact(self.surface_list)
        tri = Triangle(start_point, mid_point, end_point)

        tri.draw()
        a, b, c = tri.angle_a(), tri.angle_b(), tri.angle_c()
        arcade.draw_text(str(a), start_point[0] + 20, start_point[1], arcade.color.BLACK, 12)
        arcade.draw_text(str(b), mid_point[0], mid_point[1] + 20, arcade.color.BLACK, 12)
        arcade.draw_text(str(c), end_point[0], end_point[1] + 20, arcade.color.BLACK, 12)
        arcade.draw_circle_filled(end_point[0], end_point[1], 20, arcade.color.RED, 12)




def main():
    game = Game()
    arcade.run()


if __name__ == '__main__':
    main()