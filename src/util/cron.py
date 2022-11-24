#!/usr/bin/crontab

from __future__ import annotations

from util.date import Date
from util.extension import stringContainsAnyCase
from .mielib.responseoption import ResponseOption
from .mielib.system import username
from crontab import CronTab
from enum import IntEnum

class CronScheduler:
    cron = CronTab(user=username())

    def createRecurringJob(self, time, command, comment):
        '''
        Creates a recurring crontab job for a given time, with a given comment.

        Parameters:
        time (str): A cron string represntation, of when the given command 
        should fire.
        command (str): The command to execute when running this job.
        comment (str): A desgination used to identify this command for future
        modification or deletion.
        '''
        for job in self.cron:
            if job.comment == comment:
                self.cron.remove(job)
                new_job = self.cron.new(command=command, comment=comment)
                new_job.setall(time)
                self.cron.write()
                break
        else:
            this_job = self.cron.new(command=command, comment=comment)
            this_job.setall(time)
            self.cron.write()

    def create_job_if_needed(self, time: str, command: str, comment: str):
        '''
        Creates a new cron job to fire at the specified cron time if the
        desired job doesn't already exist.

        Parameters:
        time (str): A cron string representing when and how this cron 
            job should fire.
        command (str): The command to execute when running this job.
        comment (str): A designation used mostly to identify this job.
        '''
        if not self.job_exists(comment):
            job = self.cron.new(command, comment)
            job.setall(time)
            self.cron.write()

    def job_exists(self, comment: str) -> bool:
        '''
        Determines if a job already exists in CronTab by looping through the
        already existing jobs in CronTab.

        Parameters:
        comment (str): The designation of the job to search for.
        '''
        for job in self.cron:
            if job.comment == comment:
                return True
        return False

    def removeJob(self, comment):
        for job in self.cron:
            if job.comment == comment:
                self.cron.remove(job)
        self.cron.write()

class CronFrequency(IntEnum):
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2
    REBOOT = 3
    ONCE = 4

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
    month = 0
    hour = 0
    minute = 0

    def __init__(self, frequency: CronFrequency=None,
                       week_day=None,
                       month_day=None,
                       time=None,
                       date: str = None):
        if date is None:
            self.frequency = frequency
            self.day_of_week = week_day
            self.day_of_month = month_day
            datetime = Date.date_from_string(time)
            self.hour = datetime.hour
            self.minute = datetime.minute
        else:
            self.frequency = CronFrequency.ONCE
            datetime = Date.date_from_string(date)
            self.day_of_month = datetime.day
            self.hour = datetime.hour
            self.minute = datetime.minute
            self.month = datetime.month

    def convertToCronTime(self):
        '''
        Converts this object into a cron string.
        '''
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
        elif self.frequency == CronFrequency.ONCE:
            return f'{self.minute} {self.hour} {self.day_of_month} {self.month} *'
        elif self.frequency == CronFrequency.REBOOT:
            return "@reboot"

    @staticmethod
    def convertFromCronTime(cron_string) -> CronDate:
        '''
        Converts a cron string into a CronDate object.
        '''
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
