import os

from . import configuration as c
from .cron import CronDate, CronScheduler
from .date import Date
from .mielib import custominput as ci
from .syslog import messageDiscord, log

class Maintenance:
    dir = os.path.dirname(__file__)
    root_dir = os.path.join(dir, '..')
    scheduler = CronScheduler()

    @classmethod
    def end(cls):
        '''
        Ends any currently scheduled/running scheduled maintenance
        cycles. As part of ending, also messages the Discord server (if
        enabled).
        '''
        log(f'Ending maintenance at { Date.timestamp() }')

        c.Maintenance.maintenance_running = False
        c.Maintenance.update()

        cls.scheduler.removeJob('end maintenance automatically')
        cls.scheduler.removeJob('start maintenance automatically')

        messageDiscord('Server maintenance has ended! The server should be ' \
            'up and running in a few minutes!')

        os.system(f'python {cls.root_dir}/main.py -r')

    @classmethod
    def schedule(cls):
        '''
        Prompts user for the date and time when the scheduled maintenance
        should start and end. Once dates and times have been confirmed, also
        sends a message to the Discord server (if enabled) to alert players
        of scheduled maintenance.
        '''
        # Jobs have already been scheduled but have not been completed.
        # Should we overwrite?
        if cls.scheduler.job_exists(comment='start maintenance automatically'):
            if ci.bool_input('WARN: Maintenance is scheduled but not ' \
                'completed yet. Should I overwrite?', default=False):
                cls.scheduler.removeJob(comment='end maintenance automatically')
                cls.scheduler.removeJob(comment='start maintenance automatically')
            else:
                return

        print('WARN: During scheduled maintenance, I will shut down your Minecraft server.')
        start = ci.date_time_input(
            date_output='When do you want to start maintenance?',
            time_output='And what time?'
        )
        end = ci.date_time_input(
            date_output='When do you want to end maintenance?',
            time_output='And what time?'
        )

        # Schedule cron jobs to automatically start and stop maintenance
        cron_end = CronDate(date=end).convertToCronTime()
        cron_start = CronDate(date=start).convertToCronTime()
        end_command = f'python {cls.root_dir}/main.py -em'
        start_command = f'python {cls.root_dir}/main.py -sm'
        cls.scheduler.create_job_if_needed(
            cron_start,
            start_command,
            'start maintenance automatically'
        )
        cls.scheduler.create_job_if_needed(
            cron_end,
            end_command,
            'end maintenance automatically'
        )

        # Inform users that maintenance has been scheduled via Discord
        discord_end = Date.format(end, '%m/%d/%Y %I:%M %p')
        discord_start = Date.format(start, '%m/%d/%Y %I:%M %p')
        messageDiscord('Server maintenance has been scheduled. **The ' \
            f'server will be down** starting on {discord_start} and '\
            f'ending on {discord_end}.')

    @classmethod
    def start(cls):
        '''
        Starts 'scheduled' maintenance immediately. As part of starting, also
        messages the Discord server (if enabled).
        '''
        log(f'Starting maintenance at {Date.timestamp()}')
        print(f'python {cls.root_dir}/main.py -q')
        os.system(f'python {cls.root_dir}/main.py -q')

        c.Maintenance.maintenance_running = True
        c.Maintenance.update()

        messageDiscord('Server maintenance has started and will be ' \
            'completed as quickly as possible. Until then, **the server ' \
            'will be shut down.**')
