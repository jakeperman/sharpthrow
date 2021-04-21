import arcade
from player import *
from enemies import *
from terrain import *
from items import *
from debug import *
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
BLOCK_SCALE = .75

class Game(arcade.Window):
    def __init__(self):
        super().__init__(SW, SH, "Goblin Clash")
        arcade.set_background_color(arcade.color.SPANISH_SKY_BLUE)
        self.player = None
        self.players = arcade.SpriteList()
        self.enemies = arcade.SpriteList()
        self.controls = {"a": -5, "d": 5, "w": 5, "s": -5}
        self.jump = 32
        self.ground_list = None
        self.keys_pressed = []
        self.goblin = Goblin(800, 125)
        self.enemies.append(self.goblin)
        self.goblin.update_animation()
        self.hurt_sound = arcade.Sound("resources/sounds/oof.wav")
        self.current_player = self.hurt_sound.play(0)
        self.right_view = SW
        self.left_view = 0
        self.top_view = SH
        self.bottom_view = 0
        self.set_vsync(True)
        self.left_boundary = 0
        self.right_boundary = 0
        self.top_boundary = 0
        self.bottom_boundary = 0
        self.slash = Slash(SW/2, SH/2)
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

        # self.d = Debug(self)


    def setup(self):
        # create the player
        self.player = Player(1000, 96, SCALE)
        self.players.append(self.player)
        # self.enemies.append(Goblin(2000, 320))
        self.enemies.update_animation()
        map_name = "resources/maps/my_map.tmx"  # map file
        # read the map
        level_map = arcade.tilemap.read_tmx(map_name)
        # generate the tiles for the ground, and for ladders
        self.ground_list = arcade.tilemap.process_layer(map_object=level_map, layer_name="ground", scaling=BLOCK_SCALE, use_spatial_hash=True, hit_box_algorithm= "Simple")
        self.ladder_list = arcade.tilemap.process_layer(map_object=level_map, layer_name="ladders", scaling=BLOCK_SCALE, use_spatial_hash=True)

        # setup the physics engine
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player, self.ground_list, GRAVITY, ladders=self.ladder_list)
        self.physics_engine.disable_multi_jump()
        self.enemy_physics_engine = EnemyPhysics(self.enemies, self.player, self.ground_list, 4, ladders=self.ladder_list)
        # set initial texture
        self.player.update_animation()
        # set the players weapon
        # self.player.weapon = Dagger(self.player.right, self.player.center_y, self.player)
        self.player.weapon = ThrowingKnife(self.player)

    def on_draw(self):
        arcade.start_render()
        arcade.draw_text(f"Score: {self.score}", self.left_view + SW/2 - 10, self.top_view - 50, arcade.color.WHITE, 20)
        # draw all sprites to screen
        arcade.draw_text(f"Pos_x: {self.player.center_x}", self.right_view - 225, self.top_view - 50, arcade.color.BLACK, 12)
        arcade.draw_text(f"Mouse_Pos: {self.mouse_pos}", self.right_view - 225, self.top_view - 75,
                         arcade.color.BLACK, 12)
        self.ladder_list.draw()
        self.player.draw_hit_box(arcade.color.RED, 1)
        # if self.player.weapons:
            # arcade.draw_points(self.player.weapons[-1].path, arcade.color.RED)
        # self.enemies.draw()
        self.ground_list.draw()
        if self.player.weapons:
            self.player.weapons.draw()
        # if self.player.attacking:
        # self.player.weapon.draw()
        self.players.draw()
        if self.game_over:
            arcade.draw_text("GAME OVER", self.left_view + SW/2 - 100, SH/2, arcade.color.RED, 50)
        # calculate length of health bar
        box_len = self.player.hp * 10
        max_len = self.player.max_hp * 10
        # self.d.out('max_len')
        # draw the player's health bar
        arcade.draw_lrtb_rectangle_filled(self.left_view + 25, self.left_view + 25 + max_len, self.top_view - 17.5,
                                          self.top_view - 35, arcade.color.WHITE_SMOKE)
        arcade.draw_lrtb_rectangle_filled(self.left_view + 25, self.left_view + 25 + box_len, self.top_view - 17.5, self.top_view - 35, arcade.color.RED_DEVIL)
        arcade.draw_text("HP", self.left_view + max_len + 30, self.top_view - 40, arcade.color.BLACK, 20)
    def on_update(self, delta_time: float):
        if self.frame > 60:
            self.frame = 0
        # set screen scroll boundaries
        left_boundary = self.left_view + LEFT_VIEW_MARGIN
        right_boundary = self.left_view + SW - RIGHT_VIEW_MARGIN
        top_boundary = self.bottom_view + SH - TOP_VIEW_MARGIN
        bottom_boundary = self.bottom_view + BOTTOM_VIEW_MARGIN
        changed = False


        for goblin in self.enemies:
            if not self.player.attacking:
                goblin.damaged = False
            weapon_hit = arcade.check_for_collision_with_list(goblin, self.player.weapons)
            if self.player.attacking and weapon_hit:
                if not goblin.damaged:
                    goblin.kill()
                    weapon_hit[0].kill()
                    goblin.damaged = True
                    print("gob hp:", goblin.hp)

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

        # check for collision between player and enemies
        enemies_hit = arcade.check_for_collision_with_list(self.player, self.enemies)
        if enemies_hit and self.player.hp > 0:

            for goblin in enemies_hit:
                if self.player.direction == left:
                    if self.player.left > goblin.center_x and self.player.change_x < 0:
                        self.player.change_x = 0
                elif self.player.direction == right:
                    if self.player.right < goblin.center_x and self.player.change_x > 0:
                        self.player.change_x = 0
                if goblin.first_attack:
                    self.current_player = self.hurt_sound.play(1)
                    self.player.hp -= 2
                    goblin.did_damage = True
                    goblin.first_attack = False
                elif goblin.can_attack and not goblin.did_damage:
                    self.current_player = self.hurt_sound.play(1)
                    self.player.hp -= 2
                    goblin.did_damage = True
        # if the player has no HP left, the game is over
        elif self.player.hp <= 0:
            self.game_over = True

        # register keypress actions
        self.player.actual_y = self.player.center_y + (self.right_view - SW)
        # print(self.player.actual_y)
        # update sprites
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
        if self.left_view + SW > 2304:
            self.left_view = 2304 - SW
            self.right_view = self.left_view + SW
        elif self.left_view < 0:
            self.left_view = 0
            self.right_view = self.left_view +SW

        # if view has changed, update the window accordingly
        if changed:
            arcade.set_viewport(self.left_view, self.right_view, self.bottom_view, self.top_view)

        # check for collision of player with enemies


        # for weapon in self.player.weapons:
        #     if weapon.center_x > self.right_view or weapon.center_x < self.left_view:
        #         weapon.kill()

        # enemy physics
        for enemy in self.enemies:
            enemy.attack_timer += 1
            # prevent enemy from going through the floor
            # kill enemy if it goes off screen
            if enemy.left <= 0:
                enemy.kill()
            # prevent enemies from spawning off screen
            if enemy.right >= 2270:
                enemy.right -= 50
                enemy.base_velocity *= -1

                # enemy.center_x -= enemy.right - 2270
                # enemy.right -= 20

            # attack the player if the enemy is within range
            if enemy.left <= self.player.center_x + 80 and enemy.center_y > self.player.center_y - 32:
                enemy.attack = True

            # set the enemy to target/follow the player


        # spawn enemies if they are all killed
        # if not self.enemies:
        #     for x in range(50, 100, 50):
        #         if arcade.check_for_collision_with_list(self.player, self.ground_list):
        #             new_enemy = Goblin(random.randint(0, 2270), self.player.center_y)
        #         else:
        #             new_enemy = Goblin(random.randint(0, 2270), 125)
        #         self.enemies.append(new_enemy)
        #         new_enemy.update_animation()
        #
        #     print(len(self.enemies))
        self.frame += 1

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