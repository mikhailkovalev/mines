from ui import MainWindow
from game_managers import GameManager
from fields import RectangleField


def main():
    manager = GameManager()
    main_window = MainWindow(manager)
    main_window.run()


if __name__ == '__main__':
    main()
