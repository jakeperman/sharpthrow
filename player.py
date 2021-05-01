import arcade
from items import ThrowingKnife, Projectile
import time
FRAMES_PER_UPDATE = 5
FPU = FRAMES_PER_UPDATE
left = -1
right = 1


class Player(arcade.AnimatedWalkingSprite):
    def __init__(self, x, y, scale):
        super().__init__(scale=scale)
        # path to texture folder
        texture_path = "resources/sprites/player/"
        self.center_x, self.center_y = x, y
        self.animation_length = 2
        # load the textures for animation during standing, walking, and attacking
        self.stand_right_textures = [arcade.load_texture(f"{texture_path}0.png")]
        self.stand_left_textures = [arcade.load_texture(f"{texture_path}0.png", mirrored=True)]
        self.walk_right_textures = [arcade.load_texture(f"{texture_path}{texture}.png")
                                    for texture in range(self.animation_length)]
        self.walk_left_textures = [arcade.load_texture(f"{texture_path}{texture}.png", mirrored=True)
                                   for texture in range(self.animation_length)]
        self.attack_right_textures = [arcade.load_texture(f"{texture_path}{texture}.png")
                                      for texture in range(2,5)]
        self.attack_left_textures = [arcade.load_texture(f"{texture_path}{texture}.png", mirrored=True)
                                     for texture in range(2,5)]
        self.attacking_textures = [self.attack_right_textures, self.attack_left_textures]
        self.atk_index = 0
        # setup player stats
        self.max_hp = 20
        self.hp = self.max_hp
        self.moving = False
        self.last_direction = 0
        self.changed_direction = False
        # register variables for later use
        self.weapon_stats = None
        self.weapon_type = None
        self.weapons = arcade.SpriteList()
        self.current_weapon = None
        self.should_attack = False
        self.direction = 1
        self.attacking = False
        self.prev_index = 0
        self.actual_y = 0
        self.physics_engine = None
        self.can_move = True
        self.old_weapons = arcade.SpriteList()
        self.weapon = None
        # self.weapons.disable_spatial_hashing()
        # self.old_weapons.disable_spatial_hashing()

    # attack with the players weapon
    def attack(self, x, y):
        # set player to attack (for animations)
        self.attacking = True
        # create an instance of the players weapon object
        # self.current_weapon = self.weapon_type(self.weapon_stats)
        self.set_weapon()
        self.physics_engine.throw_knife(x, y, self.weapon)
        # self.physics_engine.throw_object(self.current_weapon, x, y, 20)


    def set_weapon(self):
        self.weapon = self.get_weapon()
        self.weapons.append(self.weapon)

    def get_weapon(self):
        return self.weapon_type(self.weapon_stats)

    def update(self):
        # if player is going left
        if self.change_x < -.1:
            self.direction = left
        # if player is going right
        elif self.change_x > .1:
            self.direction = right
        if self.last_direction != self.direction:
            self.changed_direction = True

        else:
            self.changed_direction = False

        if .1 > self.change_x > -.1:
            self.moving = False
        else:
            self.moving = True


        # set correct direction to update weapon
        # if self.weapons:
        #     if len(self.old_weapons) > 1000:
        #         self.old_weapons[0].kill()
        #     self.weapons.update()


        self.last_direction = self.direction

        # print("center_x", self.center_x)

    def update_animation(self, delta_time: float = 1/60):
        super(Player, self).update_animation()
        # if the player is attacking, display the attack animation
        if self.attacking:
            direct = 0
            if self.direction == -1:
                direct = 1
            index = self.atk_index // 3
            self.texture = self.attacking_textures[direct][index]
            self.atk_index += 1
            if self.atk_index > 6:
                self.atk_index = 0
                self.attacking = False

    def speed_x(self, v):
        self.change_x = v

    def speed_y(self, v):
        self.change_y = v

    def set_direction(self, direction):
        self.direction = direction
        self.update_animation()



            # # animation will update every 3 frames
            # index = self.atk_index // FPU
            # # set texture
            # self.texture = self.attacking_textures[self.direction][index]
            # # if the animation changes, update the weapon position
            # self.prev_index = index  # set previous index for comparison
            # self.atk_index += 1  # increase index
            # # reset index and stop attacking if finished
            # if self.atk_index > FPU * 1:
            #     self.atk_index = 0
            #     self.attacking = False
            #     self.weapon.use = False
        # self.hit_box = self.texture.hit_box_points