from ui import TkWindow
from game_managers import GameManager
from fields import RectangleField


def main():
    main_window = TkWindow()
    manager = GameManager()
    main_window.bind_manager(manager)
    manager.set_render_context(
        main_window.get_render_context())
    main_window.run()


if __name__ == '__main__':
    main()

