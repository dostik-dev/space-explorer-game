import arcade
import os

def main():
    print("=" * 50)
    print("Космический Исследователь")
    print("=" * 50)

    if os.path.exists("space_explorer.db"):
        print("✓ Найден файл сохранения")
    else:
        print("✗ Файл сохранения не найден, будет создан")

    from ui import SpaceExplorerGame
    game = SpaceExplorerGame()
    game.run()

if __name__ == "__main__":
    main()
