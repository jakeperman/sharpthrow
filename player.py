import arcade
from items import *
FRAMES_PER_UPDATE = 5
FPU = FRAMES_PER_UPDATE
left = 1
right = 0


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
        self.weapon = None
        self.weapons = arcade.SpriteList()
        self.should_attack = False
        self.direction = 0
        self.attacking = False
        self.prev_index = 0
        self.actual_y = 0

    # attack with the players weapon
    def attack(self, x, y):
        self.attacking = True
        # self.weapon.attack()
        knife = ThrowingKnife(self)
        self.weapons.append(knife)
        knife.attack(x, y)

    def update(self):
        # if player is going left
        if self.change_x < 0:
            self.direction = left
        # if player is going right
        elif self.change_x > 0:
            self.direction = right
        if self.last_direction != self.direction:
            self.changed_direction = True
            self.hit_box = self.texture.hit_box_points
        else:
            self.changed_direction = False

        if .1 > self.change_x > -.1:
            self.moving = False
        else:
            self.moving = True


        # set correct direction to update weapon
        if self.weapons:
            if len(self.weapons) > 8 :
                self.weapons.pop(0)
            self.weapons.update()

        # attack
        if self.should_attack:
            self.attack()
            self.should_attack = False
        self.last_direction = self.direction

        # print("center_x", self.center_x)

    def update_animation(self, delta_time: float = 1/60):
        super(Player, self).update_animation()
        # if the player is attacking, display the attack animation
        if self.attacking:
            index = self.atk_index // 3
            self.texture = self.attacking_textures[self.direction][index]
            self.atk_index += 1
            if self.atk_index > 6:
                self.atk_index = 0
                self.attacking = False




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




class Player_old(arcade.Sprite):
    def __init__(self, x, y, scale):
        super().__init__()
        self.center_x, self.center_y = x, y
        self.scale = scale
        self.current_texture = 0
        self.can_jump = True
        self.direction_facing = 0
        # self.direction_textures = arcade.load_texture_pair("resources/sprites/char4x.png", "Simple")
        self.running_textures = []
        for i in range(2):
            t = arcade.load_texture_pair(f"resources/sprites/player/{i}.png", "Simple")
            self.running_textures.append(t)
        print(self.running_textures)
        self.texture = self.running_textures[1][0]

        self.win_x = x
        self.max_hp = 10
        self.hp = self.max_hp
        self.walk_frame = 0
        self.frame = 0
        self.weapon = None
        self.should_attack = False

    def update(self):
        # self.center_x += self.change_x
        # self.center_y += self.change_y
        if self.hp <= 0:
            self.hp = 0
        if self.should_attack:
            self.attack()
            self.should_attack = False
        if self.weapon is Sword:
            if self.direction_facing == 0:
                self.weapon.center_x, self.weapon.center_y = self.right + 2, self.center_y - 5
            elif self.direction_facing == 1:
                self.weapon.center_x, self.weapon.center_y = self.left, self.center_y
        else:
            if self.direction_facing == 0:
                self.weapon.center_x, self.weapon.center_y = self.right + 2, self.center_y - 12
            elif self.direction_facing == 1:
                self.weapon.center_x, self.weapon.center_y = self.left, self.center_y - 12
        self.weapon.direction_facing = self.direction_facing
        self.weapon.update()
        # self.weapon.update()


    def update_animation(self, delta_time: float = 1/60):
        left, right = 1, 0
        # calculate if frame needs to be updated
        d_time = 60 // UPDATES_PER_FRAME
        if self.frame % d_time == 0:
            if self.walk_frame:
                self.walk_frame = 0
            else:
                self.walk_frame = 1
        # set idle texture
        if self.change_x == 0:
            self.texture = self.running_textures[0][self.direction_facing]

        # set walking textures
        if self.change_x < 0:
            self.texture = self.running_textures[self.walk_frame][1]
            self.hit_box = self.texture.hit_box_points
            self.direction_facing = left
        elif self.change_x > 0:
            self.texture = self.running_textures[self.walk_frame][0]
            self.hit_box = self.texture.hit_box_points
            self.direction_facing = right

        self.frame += 1


    def attack(self):
        self.weapon.direction_facing = self.direction_facing
        self.weapon.slash()



        # swing = 10
        # for x in range(10):
        #     self.weapon.center_x += 10
        #     # self.weapon.draw()
        # self.weapon.angle = 0
        pass



