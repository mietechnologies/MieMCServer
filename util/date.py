from datetime import datetime

class Date:
    def format(self, date, formatString):
        return date.strftime(formatString)
    
    def timestamp(self):
        now = datetime.now()
        return self.format(now, '%d/%m/%Y %H:%M:%S.%f')
        
    # helper functions to extract components of date (if no date is given, defaults to current date and time)
    def month(self, date = datetime.now()):
        return int(self.format(date, '%m'))
        
    def day(self, date = datetime.now()):
        return int(self.format(date, '%d'))
        
    def weekday(self, date = datetime.now()):
        return date.weekday()
        
    def year(self, date = datetime.now()):
        return int(self.format(date, '%Y'))
        
    def hour(self, date = datetime.now()):
        return int(self.format(date, '%H'))
        
    def minute(self, date = datetime.now()):
        return int(self.format(date, '%M'))
        
    def second(self, date = datetime.now()):
        return int(self.format(date, '%S'))
        
    def milisecond(self, date = datetime.now()):
        return int(self.format(date, '%f'))