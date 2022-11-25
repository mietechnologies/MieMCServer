import os

from util.cron import CronDate, CronScheduler
from util.date import Date
from util.mielib import custominput as ci
from util.logger import messageDiscord

class Maintenance:
    dir = os.path.dirname(__file__)
    root_dir = os.path.join(dir, '..')
    scheduler = CronScheduler()

    __configuration = None
    __log = None

    @classmethod
    def __init__(cls, configuration, logger):
        cls.__configuration = configuration
        cls.__log = logger

    @classmethod
    def end(cls):
        '''
        Ends any currently scheduled/running scheduled maintenance
        cycles. As part of ending, also messages the Discord server (if
        enabled).
        '''
        cls.__log(f'Ending maintenance at { Date.timestamp() }')
        messageDiscord('Server maintenance has ended! The server should be ' \
            'up and running in a few minutes!')

        cls.scheduler.removeJob('maintenance.end')
        cls.scheduler.removeJob('maintenance.start')
        cls.__configuration.maintenance.maintenance_running = False
        cls.__configuration.maintenance.update()

        os.system(f'python {cls.root_dir}/main.py')

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
        if cls.scheduler.job_exists(comment='maintenance.start'):
            if ci.bool_input('WARN: Maintenance is scheduled but not ' \
                'completed yet. Should I overwrite?', default=False):
                cls.scheduler.removeJob(comment='maintenance.end')
                cls.scheduler.removeJob(comment='maintenance.start')
            else:
                return

        print('WARN: During scheduled maintenance, I will shut down your '\
            'Minecraft server.')
        end = None
        start = None

        while start is None:
            tmp_start = ci.date_time_input(
                date_output='When do you want to start maintenance?',
                time_output='And what time?'
            )

            # Compare the start date to the current date:
            #   - Start date should not be lesser than current date
            today_timestamp = Date.timestamp()
            today_datetime = Date.date_from_string(today_timestamp)
            start_datetime = Date.date_from_string(tmp_start)
            start_difference = Date.difference(today_datetime, start_datetime)
            if start_difference > 0:
                start = tmp_start
            else:
                print('Sorry, maintenance can only be scheduled to start at ' \
                    'a future date...')

        while end is None:
            tmp_end = ci.date_time_input(
                date_output='When do you want to end maintenance?',
                time_output='And what time?'
            )

            # Compare the end date to the start date:
            # - End date should not be lesser than start date
            # - End date should be at least 5 minutes greater than start date
            end_datetime = Date.date_from_string(tmp_end)
            start_datetime = Date.date_from_string(start)
            start_difference = Date.difference(start_datetime, end_datetime)
            if start_difference >= 5 * 60:
                end = tmp_end
            else:
                print('Sorry, maintenance can only be scheduled to end more ' \
                    'than 5 minutes after it has been scheduled to start...')

        print(f'starting at { start } and ending at { end }')

        # Schedule cron jobs to automatically start and stop maintenance
        cron_end = CronDate(date=end).convertToCronTime()
        cron_start = CronDate(date=start).convertToCronTime()
        end_command = f'python {cls.root_dir}/main.py -m end'
        start_command = f'python {cls.root_dir}/main.py -m start'
        cls.scheduler.create_job_if_needed(
            cron_start,
            start_command,
            'maintenance.start'
        )
        cls.scheduler.create_job_if_needed(
            cron_end,
            end_command,
            'maintenance.end'
        )

        # Inform users that maintenance has been scheduled via Discord
        discord_end = Date.format(end, '%m/%d/%Y %I:%M %p')
        discord_start = Date.format(start, '%m/%d/%Y %I:%M %p')
        messageDiscord('Server maintenance has been scheduled. **The server ' \
            f'will be down** starting on {discord_start} and ending on ' \
            f'{discord_end}.')

    @classmethod
    def start(cls):
        '''
        Starts 'scheduled' maintenance immediately. As part of starting, also
        messages the Discord server (if enabled).
        '''
        cls.__log(f'Starting maintenance at {Date.timestamp()}')
        messageDiscord('Server maintenance has started and will be completed ' \
            'as quickly as possible. Until then, **the server will be shut ' \
            'down.**')

        cls.scheduler.removeJob('maintenance.restart')
        cls.scheduler.removeJob('maintenance.backup')
        cls.scheduler.removeJob('maintenance.scripts')
        cls.scheduler.removeJob('maintenance.update')
        cls.__configuration.maintenance.maintenance_running = True
        cls.__configuration.maintenance.update()

        os.system(f'python {cls.root_dir}/main.py -q')
