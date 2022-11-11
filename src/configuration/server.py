from util.mielib import custominput as ci

class Server:
    '''
    Any data we need to store in relation to the server that can't be stored
    in the server.properties file should be stored here. At the time of writing,
    this is just the ip/url used to connect to the server, but could turn into
    other things in the future.
    '''
    data = {}
    url = None

    def __init__(self, data: dict) -> None:
        self.data = data
        self.url = data.get('url', None)

    def build(self) -> dict:
        '''
        Constructs the `Server` section of the user's `config.yml` file based
        upon the user's input.
        '''
        print('Hosting a Minecraft server requires a url to connect to. This ' \
            'url can be an IP address or a url to a private server-space ' \
            'hosted on this device.')
        print('If you are hosting a local server, it\'s fine to use an IP ' \
            'address for your server, but I recommend using a url if you are ' \
            'hosting a public server.')
        print('If you need to create a public-facing url to allow users to ' \
            'connect to your server, I recommend using a service called no-ip' \
            'to generate a dynamic url that always points to your IP, ' \
            'regardless of how it might change.')
        print('You can find more information on no-ip at https://www.noip.com.')
        self.url = ci.server_address_input('What url would you like to use to' \
            'host your Minecraft server?')
        return self.update()

    def update(self) -> dict:
        '''Updates the `Server` section of the user's `config.yml` file.'''
        self.data['url'] = self.url
        return self.data

