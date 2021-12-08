from crontab import CronTab
from enum import Enum

class CronScheduler:
    cron = CronTab(user='bachapin')
    # TODO: Add some functionality to convert a more human readable "date/time"
    #       input into an usable crantab time

    def createRecurringJob(self, time, file, comment):
        for job in self.cron:
            if job.comment == comment:
                break
        else:
            command = 'sudo python /home/pi/minePi/cron/{} > /home/pi/minePi/logs.txt'.format(file)
            this_job = self.cron.new(command=command, comment=comment)
            this_job.setall(time)
            print("Creating '{}' cron job...".format(comment))
            self.cron.write()

    def removeJob(self, comment):
        for job in self.cron:
            if job.comment == comment:
                self.cron.remove(job)


class CronFrequency(Enum):
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2


class CronDate:
    frequency = None
    day_of_week = None
    day_of_month = None
    hour = 0
    minute = 0

    def __init__(self, frequency, week_day, month_day, hour, minute):
        self.frequency = frequency
        self.day_of_week = week_day
        self.day_of_month = month_day
        self.hour = hour
        self.minute = minute

    @staticmethod
    def validTime(check):
        time_style = check[1]
        time = [int(t) for t in check[0].split(":")]

        for index in range(0, 2):
            if index == 0:
                if time_style == "a" or time_style == "p":
                    if time[0] > 12:
                        return False
                elif time_style == "24":
                    if time[0] > 23:
                        return False
            elif index == 1:
                if time[index] > 59:
                    return False
        else:
            return True


    def __convertTime(self, time, type):
        time_split = time.split(":")
        hour_split = int(time_split[0])
        minute_split = int(time_split[1])
        if type == "p":
            if hour_split == 12:
                hour_split = 0
            else:
                hour_split += 12

            return (hour_split, minute_split)
        else:
            return (hour_split, minute_split)
            

