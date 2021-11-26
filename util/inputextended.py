
def bool_input(output, default=None, abrv=True):
    # Create output with parameters
    # Loop until valid input is given
    # Return the user's response in bool form
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



    