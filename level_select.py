import arcade
import arcade.gui
from arcade.gui import UIManager

class Button(arcade.gui.UIFlatButton):

    def on_click(self):
        print("clicked")

    def update_pos(self, x, y):
        self.center_x = x
        self.center_y = y


class MyView(arcade.View):
    """
    Main view. Really the only view in this example. """
    def __init__(self):
        super().__init__()

        self.ui_manager = UIManager()

    def on_draw(self):
        """ Draw this view. GUI elements are automatically drawn. """
        arcade.start_render()

    def on_show_view(self):
        """ Called once when view is activated. """
        self.setup()


    def on_hide_view(self):
        self.ui_manager.unregister_handlers()

    def setup(self):
        """ Set up this view. """
        self.ui_manager.purge_ui_elements()

        y_slot = self.window.height - 40
        left_column_x = self.window.width // 4
        right_column_x = self.window.width - 200

        # left side elements
        self.ui_manager.add_ui_element(arcade.gui.UILabel(
            'UILabel',
            center_x=left_column_x,
            center_y=y_slot * 3,
        ))




        # right side elements
        button = Button(
            'Tutorial',
            center_x=right_column_x,
            center_y=y_slot * 1,
            width=250,
            # height=20
        )
        self.ui_manager.add_ui_element(button)
        button = Button(
            'Tutorial',
            center_x=right_column_x,
            center_y=y_slot * 1,
            width=250,
            # height=20
        )




if __name__ == '__main__':
    window = arcade.Window(title='ARCADE_GUI')
    view = MyView()
    window.show_view(view)
    arcade.run()