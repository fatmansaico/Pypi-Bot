from core.bot import Bot

import os


def main() -> None:
    if os.name != "nt":
        import uvloop

        uvloop.install()

    bot = Bot("1.0.0")
    bot.run()
    

if __name__ == "__main__":
    main()