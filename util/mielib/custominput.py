from .responseoption import ResponseOption, option, optionList
import getpass
import sys, re
sys.path.append("..")
from util.cron import CronDate, CronFrequency

url_pattern = r'(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/\/=]*)'

def int_input(output, default=None):
    '''
    A custom input option that gets an int input from the user. This method will
    validate the user's input to ensure that it is an int type, returning their
    input as an int.

    Parameters:
    output (str): The output message displayed to the user.
    default (int): An optional default value, if a value is passed and the user
    doesn't give an input this function will return the default.
    '''
    message = "{} ".format(output)
    if default:
        message += "[{}] ".format(default)

    while (True):
        user_input = input(message)
        if default and user_input == "":
            return default
        else:
            try:
                valid_input = int(user_input)
                return valid_input
            except:
                print("I'm sorry, I didn't understand that input.")

def confirm_input(output):
    '''
    A custom input method. This input option requires that a user inputs the
    same input twice confirming their initial input. An example of its use is
    validating passwords.

    Parameters:
    output (str): The output message displayed to the user.
    '''
    valid_password = False

    while (not valid_password):
        first_password = input(output)
        second_password = input("Confirm your previous input by typing it " \
            "again please: ")

        while (second_password != first_password):
            second_password = input("Inputs don't match. Please re-enter " \
                "the original input: (Enter '!' to restart) ")
            if second_password == "!":
                break
        else:
            return first_password

def email_input(output, provider=None, multiples=False):
    '''
    A custom input method. This method collects and validates a user's input
    for an email address.

    Parameters:
    output (str): The output message displayed to the user.
    provider (str): An optional value to validate against. (i.e. 'gmail')
    multiples (bool): A boolean value indicating whether this method should
    collect and validate multiple email addresses.
    '''
    message = "{} ".format(output)
    if multiples:
        message += "(To enter multiple addresses, seperate each with ', ') "
    
    valid_inputs = False
    valid_emails = []
    while (not valid_inputs):
        user_response = input(message)
        if multiples:
            emails_split = user_response.split(", ")
            for email in emails_split:
                if __validate_email(email):
                    valid_emails.append(email)
                else:
                    new_email = __email_error(email)
                    valid_emails.append(new_email)
            else:
                return valid_emails
        else:
            if __validate_email(user_response, provider):
                return user_response
            else:
                print("I'm sorry, {} isn't a valid email.".format(user_response))

def __validate_email(email, provider=None):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

    if (re.fullmatch(regex, email)):
        if provider:
            provider = provider + ".com"
            if provider in email:
                return True
        else:
            return True

    return False

def __email_error(email):
    email = email
    while (True):
        message = "I'm sorry, {} is not a valid email. Please try again: ".format(email)
        email = input(message)
        if __validate_email(email):
            return email

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
    '''
    A custom input method. This input method allows a user to select from a 
    list of options.

    Parameters:
    output (str): The output message displayed to the user.
    options (list[ResponseOption]): The options that a user can choose from.
    default (ResponseOption): The default ResponseOption for this input, if no
    input is submitted this will be the option returned.
    abrv (bool): A boolean to determine whether to display the abbreviated 
    version of the give ResposneOptions.
    '''
    option_list = optionList(options, default, abrv)
    message = "{} {} ".format(output, option_list)
    valid_input = False

    while (not valid_input):
        user_input = input(message)
        possible_option = option(options, user_input)

        if user_input == "" and default is not None:
            return default.response
        elif possible_option is None:
            print("I'm sorry, I didn't understand that input.")
        else:
            return possible_option.response

def range_input(output, lower, upper, default=None):
    '''
    A custom input method. This input method collects an int for the user, and
    validates it to make sure it falls within the lower and upper bounds given.

    Parameters:
    output (str): The output message displayed to the user.
    lower (int): The lowest accepted number that can be an input.
    upper (int): The upper most accepted number that can be inputted.
    default (int): An optional int that is returned if a user doesn't give an
    input.
    '''
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

def time_input(output, default=None):
    '''
    A custom input method. This input method collects a time from the user and
    validates it against a regex.

    Parameters:
    output (str): The output message displayed to the user.
    '''
    regex = r'^([012])?\d:[0-5][0-9] ?(p|a|P|a)?(m|M)?$'
    message = "{} ".format(output)
    user_response = ""
    valid_input = False

    while (not valid_input):
        user_response = input(message)
        valid_input = re.fullmatch(regex, user_response)
    else:
        return user_response

def url_input(output) -> str:
    '''
    Asks for and confirms input of valid url from the user in the
    https://www.example.com format.

    Returns:
    A valid user-input url
    '''
    ammendment = '[http://www.example.com]'
    message = '{} {} '.format(output, ammendment)
    user_response = None
    valid_input = False

    while(not valid_input):
        user_response = input(message)
        if re.fullmatch(url_pattern, user_response):
            valid_input = True
    else:
        return user_response

def version_input(output):
    '''
    A custom input method. This method collects a version number from the user,
    validating it against the semantic versioning scheme.

    Parameters:
    output (str): The output message displayed to the user.
    '''
    regex = r'\d+\.\d+(.\d+)?'
    ammendment = "[#.##.#/#.##]"
    message = "{} {} ".format(output, ammendment)
    user_response = None
    valid_input = False

    while (not valid_input):
        user_response = input(message)
        if user_response == "" or re.fullmatch(regex, user_response):
            valid_input = True
    else:
        return user_response

def cron_date_input(output):
    '''
    A custom input method. This method collects a cron formatted string from
    the user.

    Parameters:
    output (str): The output message displayed to the user.
    '''
    freq_output = "How frequently would you like your server to " \
        "{}?".format(output)
    week_day_output = "What day of the week would you like your server to " \
        "{}?".format(output)
    month_output = "What day of the month would ou like your server to " \
        "{}?".format(output)
    time_output = "What time of the day would you like your server to " \
        "{}?".format(output)
    freq = choice_input(freq_output, options=CronDate.FREQUENCY_OPTIONS,
                        abrv=False)
    week_day = None
    month_day = None
    if freq == CronFrequency.WEEKLY:
        week_day = choice_input(week_day_output,
                                options=CronDate.WEEK_DAY_OPTIONS,
                                abrv=False)
    elif freq == CronFrequency.MONTHLY:
        month_day = range_input(month_output, lower=1, upper=28)

    time = time_input(time_output)

    cron_date = CronDate(freq, week_day, month_day, time)
    return cron_date.convertToCronTime()

def password_input(output:str, pattern:str=None) -> str:
    '''
    Asks user for password input and to confirm

    Parameters:
    output (str): The message displayed to the user
    pattern (str): The optional RegEx pattern to match when confirming
        user input
    
    Returns:
    str: The final confirmed user-input password
    '''
    ammendment = '(Passwords are saved locally to your system)'
    message = '{} {} '.format(output, ammendment)
    user_response = None
    valid_response = False
    
    while (not valid_response):
        user_response = getpass.getpass(message)
        if pattern is not None:
            if re.fullmatch(pattern, user_response):
                valid_response = True
            else:
                message = 'That password is invalid, please try again. '
        elif user_response != '':
            valid_response = True
    else:
        valid_response = False
        message = 'Please confirm your password '

        while (not valid_response):
            confirmed = getpass.getpass(message)
            if user_response == confirmed:
                valid_response = True
            else:
                message = 'Those passwords don\'t match. Please try ' \
                    'again '
        else: 
            return user_response

def server_address_input(output: str) -> str:
    '''
    A user input method to ask the user for a server address. This method
    handles both IP address and URL inputs.

    - Parameters:
        - output (str): The message to display to the user when asking for
        input.

    - Returns:
        - (str): The user's valid input.
    '''
    ip_format = '192.168.1.107'
    url_format = 'someserver.net'
    ammendment = f'[{ ip_format } / { url_format }]'
    message = f'{ output } { ammendment } '

    ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
    user_response = None
    valid_response = False

    while not valid_response:
        user_response = input(message)
        if re.fullmatch(ip_pattern, user_response):
            valid_response = True
        elif re.fullmatch(url_pattern, user_response):
            valid_response = True
        else:
            message = 'That server address is invalid, please try again. '
    else:
        return user_response

def calendar_date_input(output) -> str:
    '''
    A custom input method. This method collects a date from the user in the
    format of 'MM/DD/YYYY' and validates it against a regex.

    Parameters:
    output (str): The output message displayed to the user.
    '''
    regex = r'^[0|1][0-9]\/[0-3][0-9]\/2\d{3}$'
    ammendment = '[MM/DD/YYYY]'
    message = '{} {} '.format(output, ammendment)
    user_response = None
    valid_input = False

    while (not valid_input):
        user_response = input(message)
        valid_input = re.fullmatch(regex, user_response)
    else:
        return user_response

def date_time_input(date_output: str, time_output: str) -> str:
    '''
    A custom input method that combines two input methods into one. This input
    method collects both the date and the time from the user.

    Parameters:
    date_output (str): The output message displayed to the user when collecting
    the date.
    time_output (str): The output message displayed to the user when collecting
    the time.
    '''
    date = calendar_date_input(date_output)
    time = time_input(time_output)
    return '{} {}'.format(date, time)