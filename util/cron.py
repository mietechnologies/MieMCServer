from crontab import CronTab

class CronScheduler:
    cron = CronTab(user='pi')
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