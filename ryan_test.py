from jarcade import engine
from jarcade import items
import arcade


class Game(arcade.Window):
    def __init__(self):
        super(Game, self).__init__( 800, 800, "game")
        self.knife = items.Projectile("resources/sprites/item/knife.png", .5)
        self.knifes = arcade.SpriteList()
        arcade.set_background_color(arcade.color.BLUE)
        self.target = arcade.Sprite("resources/sprites/world/target_down_facing.png", 1)
        self.target.center_x = 200
        self.target.center_y = 50
        self.targets = arcade.SpriteList()
        self.targets.append(self.target)
        self.physics = engine.RyanEngine(self.targets, 5)
        self.traject = None
        self.draw_traject = False

    def on_draw(self):
        arcade.start_render()
        self.knifes.draw()
        if self.draw_traject:
            self.traject.draw()
        self.targets.draw()

    def on_update(self, delta_time: float):
        self.physics.update()

    def on_mouse_press(self, x: float, y: float, button: int, modifiers: int):
        knife = items.Projectile("resources/sprites/item/knife.png", .5)
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.traject = self.physics.get_trajectory_from_object(knife, x, y, 50)
            self.draw_traject = True
        else:
            self.knifes.append(knife)
            self.physics.throw_object(knife, x, y, 50)

    def on_mouse_release(self, x: float, y: float, button: int,
                         modifiers: int):
        if button == arcade.MOUSE_BUTTON_RIGHT:
            knife = items.Projectile("resources/sprites/item/knife.png", .5)
            self.knifes.append(knife)
            self.physics.throw_object(knife, x, y, 50)
            self.draw_traject = False


    def on_mouse_motion(self, x: float, y: float, dx: float, dy: float):
        knife = items.Projectile("resources/sprites/item/knife.png", .5)
        self.traject = self.physics.get_trajectory_from_object(knife, x, y, 50)

    def on_key_press(self, symbol: int, modifiers: int):





def main():
    game = Game()
    arcade.run()


if __name__ == "__main__":
    main()
