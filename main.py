import arcade
from player import *
from enemies import *
from terrain import *
from items import *
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
TOP_VIEW_CHANGE = 128
VIEW_CHANGE = 128
BLOCK_SCALE = .5
right = 0
left = 1
PLAYER_SPEED = 4

perf = FpsCounter()


class Game(arcade.Window):
    def __init__(self):
        super().__init__(SW, SH, "Sharpthrow Shawn")
        arcade.set_background_color(arcade.color.PURPLE_TAUPE)
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
        self.setup()

        
        
    
    def setup(self):
        # create UI
    
        # create the player
        self.player = Player(1000, 96, SCALE)
        self.players.append(self.player)

        self.controls = {
            'a': {'func': self.player.speed_x, 'param': -self.player_speed},
            'd': {'func': self.player.speed_x, 'param': self.player_speed}
        }

        self.set_level("level_1")

        # setup the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.ground_list, GRAVITY)
        self.physics_engine.disable_multi_jump()
        # set initial texture
        self.player.update_animation()
        self.player.weapon = ThrowingKnife(self.player)
        self.physics = PhysicsEngine(self.player, self.ground_list)

    @perf.draw_fps
    def on_draw(self):
        arcade.start_render()
        # draw score
        arcade.draw_text(f"Score: {self.score}", self.left_view + SW/2 - 10, self.top_view - 50, arcade.color.WHITE, 20)
        # draw player pos and mouse pos
        arcade.draw_text(f"X: {self.player.center_x}, Y:{self.player.center_y}", self.right_view - 10, self.top_view - 40, arcade.color.BLACK, 12, anchor_x="right")
        arcade.draw_text(f"Mouse_Pos: {self.mouse_pos}", self.right_view - 10, self.top_view - 20,
                         arcade.color.BLACK, 12, anchor_x="right")
        

        if self.player.weapons:
            self.player.weapons.draw()
            if self.stats_loaded:
                arcade.draw_polygon_outline(self.triangle, arcade.color.PURPLE, 2)
                arcade.draw_points(self.weapon_traject, arcade.color.GOLD, 3)
                self.player.draw_hit_box(arcade.color.RED, 1)
                arcade.draw_text(f"{self.weapon_angle:.1f}°", self.player.center_x, self.player.center_y + 40, arcade.color.RED, 8, anchor_x="center")

        if self.trail_loaded:
            self.weapon_traject.draw()
        self.players.draw()
        self.ground_list.draw()
        # calculate length of health bar
         box_len = self.player.hp * 10
         max_len = self.player.max_hp * 10
         # draw the player's health bar
        arcade.draw_lrtb_rectangle_filled(self.left_view + 25, self.left_view + 25 + max_len, self.top_view - 17.5,
                                       self.top_view - 35, arcade.color.WHITE_SMOKE)
        arcade.draw_lrtb_rectangle_filled(self.left_view + 25, self.left_view + 25 + box_len, self.top_view - 17.5, self.top_view - 35, arcade.color.RED_DEVIL)
        arcade.draw_text("HP", self.left_view + max_len + 30, self.top_view - 40, arcade.color.BLACK, 20)
            
    @perf.update_time
    def on_update(self, delta_time: float):
        # Start timing how long this takes
        changed = False
        #if self.player.weapons:
#            for knife in self.player.weapons:
#                knives = arcade.check_for_collision_with_list(knife, self.ground_list)
#                if knives:
#                    knife.thrown = False

        if not self.game_over:
            self.player.update()
            self.player.update_animation()
            self.physics_engine.update()

        # screen scrolling system
        changed = self.scroll_screen()
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

    def key_change(self):
        if self.keys_pressed:
            key = self.keys_pressed[0]
            f = self.controls[key]['func']
            f(self.controls[key]['param'])
        else:
            self.player.speed_x(0)

    def get_screen_boundaries(self):
        left_bound = self.left_view + LEFT_VIEW_MARGIN
        right_bound = self.left_view + SW - RIGHT_VIEW_MARGIN
        top_bound = self.bottom_view + SH - TOP_VIEW_MARGIN
        bottom_bound = self.bottom_view + BOTTOM_VIEW_MARGIN
        return right_bound, left_bound, top_bound, bottom_bound

    def scroll_screen(self):
        right_boundary, left_boundary, top_boundary, bottom_boundary = self.get_screen_boundaries()
        if self.player.left < left_boundary:
            self.left_view -= left_boundary - self.player.left
            self.right_view = SW + self.left_view
            return True
        elif self.player.right > right_boundary:
            self.left_view += self.player.right - right_boundary
            self.right_view = SW + self.left_view
            return True
        if self.player.top > top_boundary:
            self.bottom_view += self.player.top - top_boundary
            self.top_view = SH + self.bottom_view
            return True
        elif self.player.bottom < bottom_boundary:
            self.bottom_view -= bottom_boundary - self.player.bottom
            self.top_view = self.bottom_view + SH
            return True
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
            self.key_change()

        # if player presses space, and jump conditions are met, jump
        if symbol == arcade.key.SPACE:
            if self.physics_engine.can_jump():
                self.physics_engine.jump(JUMP_SPEED)
      
    def on_key_release(self, symbol: int, modifiers: int):
        key = chr(symbol)
        # removes keys from keys_pressed if they are no longer pressed
        if key in self.keys_pressed:
            self.keys_pressed.remove(key)
            self.key_change()

    

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        if button == 1:
            x = x + (self.right_view - SW)
            y = y + (self.top_view - SH)
            self.player.attack(x, y)

        elif button == 4:
            x = x + (self.right_view - SW)
            y = y + (self.top_view - SH)
            self.show_trail = True


    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):

        if button == 4:
            x = x + (self.right_view - SW)
            y = y + (self.top_view - SH)
            self.player.attack(x, y)
            self.show_trail = False

    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        x = x + (self.right_view - SW)
        y = y + (self.top_view - SH)
        self.mouse_pos = (x, y)
        self.trail_loaded = False
        if self.show_trail:
            self.weapon_traject = self.physics.get_trajectory(x, y)
            self.trail_loaded = True


def main():
    game = Game()
    arcade.run()


if __name__ == '__main__':
    main()
