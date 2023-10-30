from src import TkGUIFactory

PATH = "helloworld.tkd"


def main():
    factory = TkGUIFactory()
    gui = factory.to_gui(PATH)
    gui.start()


if __name__ == "__main__":
    main()
