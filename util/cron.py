from __future__ import annotations
from .mielib.responseoption import ResponseOption
from crontab import CronTab
from enum import IntEnum

class CronScheduler:
    cron = CronTab(user='michaelcraun')
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


class CronFrequency(IntEnum):
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2
    REBOOT = 3


class WeekDay(IntEnum):
    SUNDAY = 0
    MONDAY = 1
    TUESDAY = 2
    WEDNESDAY = 3
    THURSDAY = 4
    FRIDAY = 5
    SATURDAY = 6

    def cronValue(self):
        return int(self)

class CronDate:

    FREQUENCY_OPTIONS = [
        ResponseOption("d", "daily", CronFrequency.DAILY),
        ResponseOption("w", "weekly", CronFrequency.WEEKLY),
        ResponseOption("m", "monthly", CronFrequency.MONTHLY)
    ]
    WEEK_DAY_OPTIONS = [
        ResponseOption("u", "sunday", WeekDay.SUNDAY),
        ResponseOption("m", "monday", WeekDay.MONDAY),
        ResponseOption("t", "tuesday", WeekDay.TUESDAY),
        ResponseOption("w", "wednesday", WeekDay.WEDNESDAY),
        ResponseOption("r", "thursday", WeekDay.THURSDAY),
        ResponseOption("f", "friday", WeekDay.FRIDAY),
        ResponseOption("s", "saturday", WeekDay.SATURDAY)
    ]

    frequency = None
    day_of_week = None
    day_of_month = None
    hour = 0
    minute = 0

    def __init__(self, frequency: CronFrequency,
                       week_day,
                       month_day,
                       time):
        self.frequency = frequency
        self.day_of_week = week_day
        self.day_of_month = month_day
        hour, minute = self.__convertTime(time)
        self.hour = hour
        self.minute = minute

    def convertToCronTime(self):
        if self.frequency == CronFrequency.DAILY:
            return "{} {} * * *".format(self.minute, self.hour)
        elif self.frequency == CronFrequency.WEEKLY:
            return "{} {} * * {}".format(self.minute,
                                         self.hour,
                                         self.day_of_week.cronValue())
        elif self.frequency == CronFrequency.MONTHLY:
            return "{} {} {} * *".format(self.minute,
                                         self.hour,
                                         self.day_of_month)
        elif self.frequency == CronFrequency.REBOOT:
            return "@reboot"

    @staticmethod
    def convertFromCronTime(cron_string) -> CronDate:
        cron_split = cron_string.split(" ")
        length = len(cron_split)
        minutes = None
        hours = None
        week_day = None
        month_day = None
        frequency = None
        if length == 1:
            return CronDate(CronFrequency.REBOOT)
        else:
            for index in range(length):
                item = cron_split[index]
                if item != "*":
                    if index == 0:
                        minutes = int(item)
                    elif index == 1:
                        hours = int(item)
                    elif index == 2:
                        month_day = int(item)
                        frequency = CronFrequency.MONTHLY
                    elif index == 4:
                        week_day = WeekDay(int(item))
                        frequency = CronFrequency.WEEKLY
            else:
                if not frequency:
                    frequency = CronFrequency.DAILY
                return CronDate(frequency,
                                week_day, 
                                month_day, 
                                "{}:{} 24".format(hours, minutes))


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


    def __convertTime(self, time):
        if time == None:
            return (None, None)

        time, type = time.split(" ")
        time_split = time.split(":")
        hour_split = int(time_split[0])
        minute_split = int(time_split[1])
        if type == "p":
            if hour_split > 12:
                hour_split += 12

            return (hour_split, minute_split)
        else:
            if type == "a" and hour_split == 12:
                return (0, minute_split)
            else:
                return (hour_split, minute_split)
            

