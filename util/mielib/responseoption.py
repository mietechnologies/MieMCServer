
class ResponseOption:
    
    abrv_option = ""
    full_option = ""
    all_options = []
    response = None

    def __init__(self, abrv_option, full_option, response):
        self.abrv_option = abrv_option.lower()
        self.full_option = full_option.lower()
        self.response = response
        self.all_options = [abrv_option.lower(), full_option.lower()]

    def __eq__(self, __o: object) -> bool:
        if (isinstance(__o, ResponseOption)):
            return self.all_options == __o.all_options

    def contains(self, response):
        if response.lower() in self.all_options:
            return True
        else:
            return False

    def setDefault(self):
        self.abrv_option = self.abrv_option.upper()
        self.full_option = self.full_option.upper()


def option(options, response):
    for option in options:
        if option.contains(response):
            return option
    else:
        return None

def optionList(options, default=None, abrv=True):
    choice_list = []
    
    for option in options:
        if option == default:
            option.setDefault()

        if abrv:
            choice_list.append(option.abrv_option)
        else:
            choice_list.append(option.full_option)
    
    output = "/".join(choice_list)
    return "[{}]".format(output)