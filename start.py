from main import Main

if __name__ == '__main__':
    main = Main()
    main.configure()
    main.install()
    main.startMonitors()
    main.start()