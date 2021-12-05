from .responseoption import ResponseOption, option, optionList

def bool_input(output, default=None, abrv=True):
    '''A function to get a user's response to a question that has a yes or no
    (True or False) answer.
    
    Keyword arguments:
        default -- This is the default response if the user does not input
    anything. This parameter can be either True, False, or None. If set to None,
    the function will not accept an empty answer. It will require one of the
    given responses. (Defaults to None)
        abrv -- Uses the abbreviated response. (Defaults to True)'''
    true_answers = ["y", "yes"]
    false_answers = ["n", "no"]
    used_index = 0 if abrv else 1
    ammendment = ""
    valid_answers = []
    if default is None:
        ammendment = "[{}/{}]".format(true_answers[used_index],
                                      false_answers[used_index])
        valid_answers = true_answers + false_answers
    elif default:
        ammendment = "[{}/{}]".format(true_answers[used_index].upper(),
                                      false_answers[used_index])
        valid_answers = true_answers + false_answers + [""]
    else:
        ammendment = "[{}/{}]".format(true_answers[used_index],
                                      false_answers[used_index].upper())
        valid_answers = true_answers + false_answers + [""]

    message = "{} {} ".format(output, ammendment)
    valid_input = False

    while (not valid_input):
        user_response = input(message)

        if user_response.lower() in true_answers:
            return True
        elif user_response.lower() in false_answers:
            return False
        elif user_response.lower() in valid_answers:
            return default

        print("I'm sorry, I didn't understand that input.")

def choice_input(output, options, default=None, abrv=True):
    ''''''
    option_list = optionList(options, default, abrv)
    message = "{} {} ".format(output, option_list)
    valid_input = False

    while (not valid_input):
        user_input = input(message)
        possible_option = option(options, user_input)

        if user_input == "" and default.response is not None:
            return default.response
        elif possible_option is None:
            print("I'm sorry, I didn't understand that input.")
        else:
            return possible_option.response

def range_input(output, lower, upper, default=None):
    ''''''
    message = "{} [{}-{}] ".format(output, lower, upper)
    user_input = None
    valid_input = False

    while (not valid_input):
        use_default = False
        try:
            user_input = input(message)

            if user_input == "":
                use_default = True

            user_input = int(user_input)
        except:
            pass

        if user_input in range(lower, upper + 1):
            return user_input
        elif use_default and default is not None:
            return default
        else:
            print("I'm sorry, I didn't understand that input.")

def regex_input(output, regex, default=None):
    split_regex = regex.split(" ")
    message = "{} [{}] ".format(output, regex)
    valid_input = False
    valid_num = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
    valid_alpha = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", 
    "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
    valid_alpha_num = valid_num + valid_alpha

    while (not valid_input):
        user_input = str(input(message))
        user_input_split = user_input.split(" ")
        valid_format = True

        if user_input == "" and default is not None:
            return default
        elif len(split_regex) is len(user_input_split):
            for index in range(0, len(split_regex)):
                item = split_regex[index]
                check = user_input_split[index]
            
                if "/" in item:
                    options = item.split("/")
                    if check not in options:
                        valid_format = False
                        break
                else:
                    if len(item) is not len(check):
                        valid_format = False
                        break
                    else:
                        for inner_index in range(0, len(item)):
                            if item[inner_index] == "#":
                                if check[inner_index] not in valid_num:
                                    valid_format = False
                                    break
                            elif item[inner_index] == "$":
                                if check[inner_index] not in valid_alpha:
                                    valid_format = False
                                    break
                            elif item[inner_index] == "*":
                                if check[inner_index] not in valid_alpha_num:
                                    valid_format = False
                                    break
            else:
                if valid_format:
                    return user_input

        print("I'm sorry, I didn't understand that input.")