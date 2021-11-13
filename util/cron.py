from crontab import CronTab
<<<<<<< HEAD
        
class CronScheduler:
    cron = CronTab(user='pi')
    
    def createRecurringJob(self, time, path, comment):
        for job in self.cron:
            if job.comment == comment:
                break
        else:
            this_job = self.cron.new(command=path, comment=comment)
            this_job.setall(time)
            print("Creating '{}' cron job...".format(comment))
            self.cron.write()
        
    def removeJob(self, comment):
        for job in self.cron:
            if job.comment == comment:
                self.cron.remove(job)
=======

def createRecurringJob(time, path, comment):
    cron = CronTab(user="pi")
    removeJob(comment)
    this_job = cron.new(command='cron', comment=comment)
    this_job.setall(time)
    print("Creating 'this_job'...")
    cron.write()
    
def removeJob(comment):
    cron = CronTab(user='pi')
    for job in cron:
        if job.comment == comment:
            cron.remove(job)
>>>>>>> 5a53cc1fc1630d4d0db58025df56c13c201cf79d
