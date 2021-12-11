from datetime import datetime

class Date:

    @staticmethod
    def timestamp():
        date_format = '%m/%d/%Y %H:%M:%S.%f'
        now = datetime.now()
        return now.strftime(date_format)

    @staticmethod
    def timeFromDate(dateString):
        date_format = '%m/%d/%Y %H:%M:%S.%f'
        return datetime.strptime(dateString, date_format)

    @staticmethod
    def elapstedTime(firstDate, secondDate):
        return abs(firstDate - secondDate.total_seconds())

    @staticmethod 
    def strippedTimestamp():
        timestamp = Date.timestamp()
        return timestamp.replace('/', '-').replace(' ', '_').replace(':', '-')
