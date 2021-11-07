from datetime import datetime

class Date:
    def timestamp(self):
        now = datetime.now()
        dt_string = now.strftime('%d/%m/%Y %H:%M:%S.%f')
        return dt_string