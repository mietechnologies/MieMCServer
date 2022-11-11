from util.mielib import custominput as ci

class Messaging:
    data = {}
    discord = None

    def __init__(self, data: dict) -> None:
        self.data = data
        self.discord = self.data.get('discord', None)

    def build(self) -> dict:
        if ci.bool_input('If you\'d like, I can post important updates (like '\
            'server shut downs and restarts) to a Discord server. Would you like '\
            'to use this service?', False):
            print('Alright, the only information I need to setup discord is a '\
                'webhook URL. You can find out how to get that information at '\
                'https://support.discord.com/hc/en-us/articles/228383668-Intro-to-'\
                'Webhooks.')
            self.discord = ci.url_input('So, what is that webhook URL?')
        return self.update()

    def update(self) -> dict:
        self.data['discord'] = self.discord
        return self.data

    def reset(self) -> dict:
        self.discord = None
        return self.update()
