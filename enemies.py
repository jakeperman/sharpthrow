import arcade
from debug import *
left = 1
right = 0

class Enemy(arcade.AnimatedWalkingSprite):
    def __init__(self, gravity):
        super().__init__()
        pass


class Goblin(arcade.AnimatedWalkingSprite):
    def __init__(self, x, y, kind="Ground"):
        super().__init__()
        self.center_x, self.center_y = x, y
        # path to texture folder
        texture_path = "resources/sprites/goblin/"
        self.animation_length = 1
        # load the textures for animation during standing, walking, and attacking
        self.stand_right_textures = [arcade.load_texture(f"{texture_path}walk/0.png")]
        self.stand_left_textures = [arcade.load_texture(f"{texture_path}walk/0.png", mirrored=True)]
        self.walk_right_textures = [arcade.load_texture(f"{texture_path}walk/{texture}.png")
                                    for texture in range(0, 2)]
        self.walk_left_textures = [arcade.load_texture(f"{texture_path}walk/{texture}.png", mirrored=True)
                                   for texture in range(0, 2)]
        self.attack_right_textures = [arcade.load_texture(f"{texture_path}attack/{texture}.png") for texture in
                                      range(3)]
        self.attack_left_textures = [arcade.load_texture(f"{texture_path}attack/{texture}.png", mirrored=True) for
                                     texture in range(3)]
        self.attacking_textures = [self.attack_right_textures, self.attack_left_textures]
        # goblin stats
        self.direction = 1
        self.base_velocity = 2
        self.change_x = -2
        self.hp = 4
        self.damage = 4
        # register variables for later use
        self.did_damage = False
        self.attack = False
        self.atk_index = 0
        self.attack_timer = 0
        self.target_speed = 0
        self.running = False
        self.can_attack = True
        self.first_attack = True
        self.damaged = False
        self.jumping = False

        self.kind = kind

    def update(self):
        # set direction based on which way the goblin is moving
        if self.change_x < 0:
            self.direction = 1
            self.hit_box = self.texture.hit_box_points  # update hitbox
        elif self.change_x > 0:
            self.direction = 0
            self.hit_box = self.texture.hit_box_points  # update hitbox
        # update position of hobline
        self.center_x += self.change_x
        self.center_y += self.change_y

    # update the current animation
    def update_animation(self, delta_time: float = 1/60):
        super(Goblin, self).update_animation()

        # only attack once every 60 frames
        if self.attack and self.attack_timer > 60:
            self.can_attack = True
            index = self.atk_index // 3
            self.texture = self.attacking_textures[self.direction][index]
            self.atk_index += 1
            # after attack is finished, reset
            if self.atk_index > 6:
                self.atk_index = 0
                self.attack = False
                self.attack_timer = 0
        # reset attack variables
        else:
            self.did_damage = False
            self.can_attack = False

    # player targetting system
    def target(self, object):
        # if the player is above the enemy, it will pace back and forth underneath
        if object.center_y - 10 > self.center_y:
            self.running = False
            if self.center_x <= object.center_x - 100:
                self.base_velocity = 2
            elif self.center_x >= object.center_x + 100:
                self.base_velocity = -2
        elif self.center_y > object.center_y:
            pass
        else:
            # prevent enemy from going through the player
            if object.right - 10 <= self.left <= object.right - 2:
                # self.center_x = object.right + 40
                self.base_velocity = 0
            elif object.left + 2 <= self.right <= object.left + 5:
                # self.center_x = object.right - 40
                self.base_velocity = 0
            # set enemy to run towards player
            elif object.center_x < self.center_x:
                self.running = True
                self.base_velocity = -6
            elif object.center_x > self.center_x:
                self.running = True
                self.base_velocity = 6

class Doggart(arcade.Sprite):
    def __init__(self):
        super().__init__("resources/sprites/doggart.png")



class EnemyPhysics:
    def __init__(self, enemy_list: arcade.SpriteList, player: arcade.Sprite, platforms: arcade.SpriteList, gravity: float,
                 ladders: arcade.SpriteList = None):
        self.sprites = enemy_list
        self.platforms = platforms
        self.gravity = gravity
        self.ladders = ladders
        self.player = player
        self.local_debug = LocalDebugger().out
        self.jump_counter = 0

    def update(self):
        for sprite in self.sprites:
            collisions = arcade.check_for_collision_with_list(sprite, self.platforms)
            ladders = self.is_on_ladder(sprite)
            if ladders:
                if self.player.center_y -10 > sprite.center_y:
                    ladder = ladders[-1]
                    if sprite.center_y < ladder.top:
                        sprite.center_x = ladder.center_x
                        sprite.change_y = 3
                        sprite.change_x = 0
                    elif sprite.bottom + 10 > ladder.top:
                        sprite.bottom += 50
                        if not self.is_on_ladder(sprite):
                            sprite.bottom -= 50
                            sprite.change_x = sprite.base_velocity
                            sprite.change_y = 1
                        else:
                            sprite.bottom -= 50
                    # elif sprite.center_y > ladder.top:
            elif not collisions:
                if sprite.center_y - 100 > self.player.center_y:
                    sprite.center_y -= 50
                elif self.can_jump(sprite):
                    sprite.jumping = True
                    sprite.bottom += 80
                    print("jumping")
                    if sprite.direction == left:
                        sprite.change_x = -6
                    else:
                        sprite.change_x = 6
                    self.jump_counter += 1
                else:
                    sprite.change_y = -self.gravity
            if collisions and not ladders:
                sprite.jumping = False
                for item in collisions:
                    if item.center_y <= sprite.center_y:
                        is_ground = True
                        break
                    else:
                        is_ground = False
                if is_ground:
                    sprite.change_y = 0
                    self.jump_counter = 0
                    if sprite.bottom - 1 < item.top:
                        sprite.bottom = item.top - 1
                    if sprite.direction == right:
                        sprite.change_x = sprite.base_velocity
                    elif sprite.direction == left:
                        sprite.change_x = sprite.base_velocity
                else:
                    sprite.change_x = 0
                    print("nothing")
            player_collide = arcade.check_for_collision(sprite, self.player)
            if sprite.right > self.player.left > sprite.left and sprite.center_y == self.player.center_y:
                sprite.change_x = 0
            elif player_collide:
                sprite.change_x = 0
            # if sprite.right >= self.player.left + 3:
            #     sprite.change_x = 0
            #     sprite.right = self.player.left
            sprite.update()
            sprite.target(self.player)
            sprite.update_animation()


    def can_jump(self, sprite, y_distance=5) -> bool:
        """
        Method that looks to see if there is a floor under
        the player_sprite. If there is a floor, the player can jump
        and we return a True.

        :returns: True if there is a platform below us
        :rtype: bool
        """

        # Move down to see if we are on a platform
        sprite.center_y -= y_distance

        # Check for wall hit
        hit_list = arcade.check_for_collision_with_list(sprite, self.platforms)

        sprite.center_y += y_distance

        if len(hit_list) == 0 and not self.jump_counter:
            return True
        else:
            return False


    def jump(self, sprite, velocity: int):
        """ Have the character jump. """
        sprite.change_y += velocity
        self.jump_counter += 1


    def is_on_ladder(self, sprite):
        """ Return 'true' if the player is in contact with a sprite in the ladder list. """
        # Check for touching a ladder
        if self.ladders:
            hit_list = arcade.check_for_collision_with_list(sprite, self.ladders)
            if len(hit_list) > 0:
                return hit_list
        return False



