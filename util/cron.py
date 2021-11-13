from crontab import CronTab

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