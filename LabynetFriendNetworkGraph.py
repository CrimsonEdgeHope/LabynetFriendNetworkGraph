import config
import crawler


def init():
    config.setup_logger()
    config.load_config()


if __name__ == "__main__":
    init()
    crawler.run()
