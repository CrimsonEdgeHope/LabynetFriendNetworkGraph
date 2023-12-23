import config

if __name__ == "__main__":
    config.load_config()
    import crawler
    crawler.run()
