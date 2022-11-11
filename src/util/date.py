from datetime import datetime
from .extension import string_contains, stringContainsAnyCase

class Date:
    @staticmethod
    def date_from_string(date: str) -> datetime:
        '''
        Converts a date-time or time string into a useable datetime object.
        This method can handle time in both 12- and 24-hour formats.

        Parameters:
        date (str): The date-time or time string to convert.
        '''
        if stringContainsAnyCase(date, ['a', 'am', 'p', 'pm']):
            if '/' in date:
                return Date.timeFromDate(date, '%m/%d/%Y %I:%M %p')
            return Date.timeFromDate(date, '%I:%M %p')

        if '/' in date:
            if string_contains(
                date,
                r'\d{2}\/\d{2}\/\d{4} \d{2}:\d{2}:\d{2}.\d+'
            ):
                return Date.timeFromDate(date, '%m/%d/%Y %H:%M:%S.%f')
            return Date.timeFromDate(date, '%m/%d/%Y %H:%M')
        return Date.timeFromDate(date, '%H:%M')

    @staticmethod
    def format(date, format_str: str) -> str:
        '''
        This is a conveinence method to get a formatted date string.

        Parameters:
        date (datetime): The date to format.
        format_str (str): The formula for the date to me formatted into.
        '''
        if isinstance(date, datetime):
            return date.strftime(format_str)
        date_string = Date.date_from_string(date)
        return date_string.strftime(format_str)

    @staticmethod
    def timestamp():
        '''
        Returns a formatted date string using the format of: 
        MM/DD/YYYY HH:mm:SS, i.e. 01/01/2022 12:00:12
        '''
        date_format = '%m/%d/%Y %H:%M:%S.%f'
        now = datetime.now()
        return now.strftime(date_format)

    @staticmethod
    def timeFromDate(dateString, format_str:str=None):
        '''
        Returns a datetime object from a string. If no format_str is specified
        the default format is '%m/%d/%Y %H:%M:%S'
        '''
        date_format = '%m/%d/%Y %H:%M:%S.%f' if format_str is None else format_str
        return datetime.strptime(dateString, date_format)

    @staticmethod
    def elapsedTime(firstDate, secondDate):
        '''
        Calculates and returns the time elapsed between to datetime obejcts, in
        seconds.
        '''
        return abs(firstDate - secondDate.total_seconds())

    @staticmethod
    def difference(past_date: datetime, future_date: datetime) -> float:
        '''
        Calculates the difference of time between two datetime objects.

        Parameters:
            - past_date (datetime): The current/past date to compare
            - future_date (datetime): The current/future date to compare

        Returns:
            The difference of past_date and future_date. If past_date is later
            than future_date, this method will return a negative number.
        '''
        return (future_date - past_date).total_seconds()

    @staticmethod 
    def strippedTimestamp():
        '''
        Removes all of the special characters form a date string.
        '''
        timestamp = Date.timestamp()
        return timestamp.replace('/', '-').replace(' ', '_').replace(':', '-')
