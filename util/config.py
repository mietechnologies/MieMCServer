import os

from logger import log

class Config:
    root = os.path.dirname(__file__)
    file = os.path.join(root, 'config.txt')
    weekdays = ['S', 'M', 'T', 'W', 'R', 'F', 'U']
    hours = [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    
    def confirmInput(self, response, accepted = [], isInt = False):
        if isInt and response.isnumeric():
            if accepted == []:
                return int(response)
            if int(response) in accepted:
                return int(response)
        if response in accepted:
            return response
        log('Invalid input [{}]'.format(response))
        return self.confirmInput(input(), accepted, isInt)
    
    def allottedRam(self):
        # TODO: Fetch maximum RAM from system
        log('WARNING: MinePi does NOT know how much RAM your Pi has available!')
        log('WARNING: Your server should never consume more than 75% of your total RAM!')
        log('How much RAM would you like to dedicate to your server?')
        allotted = self.confirmInput(input(), [], True)
        return allotted
        
    def backupSchedule(self):
        log('What day of the week would you like to backup your server? {}'.format(self.weekdays))
        day = self.confirmInput(input(), self.weekdays)
        
        log('What hour of the day would you like to backup your server? (UTC; 0 is not accepted)')
        hour = self.confirmInput(input(), self.hours, True)
        
        return { 'day' : day, 'hour' : hour }
        
    def dailyCleanSchedule(self):
        log('What hour of the day would you like to run daily clean up of your server? (UTC; 0 is not accpeted)')
        hour = self.confirmInput(input(), self.hours, True)
        return hour
        
    def dayAsInt(self, day):
        if day == 'S': return 0
        if day == 'M': return 1
        if day == 'T': return 2
        if day == 'W': return 3
        if day == 'R': return 4
        if day == 'F': return 5
        if day == 'U': return 6
        return None
        
    def weeklyCleanSchedule(self):
        message = 'What day of the week would you like to run weekly clean up of your server? {}'.format(self.weekdays)
        log(message)
        day = self.confirmInput(input(), self.weekdays)
        
        message = 'What hour of the day would you like to run weekly clean up of your server? (UTC; 0 is not accepted)'
        log(message)
        hour = self.confirmInput(input(), self.hours, True)
        
        return { 'day' : day, 'hour' : hour }
    
    def start(self):
        log('Starting config...')
        # Should ask user for input on the following:
        # - allotted RAM
        # - backup schedule
        # - daily clean schedule
        # - weekly clean schedule
        # - ???
        allottedRam = self.allottedRam()
        backupSchedule = self.backupSchedule()
        dailyCleanSchedule = self.dailyCleanSchedule()
        weeklyCleanSchedule = self.weeklyCleanSchedule()
        
        file = open(self.file, 'w')
        file = open(self.file, 'a')
        file.write('ram={}\n'.format(allottedRam))
        file.write('backupDay={}\n'.format(self.dayAsInt(backupSchedule['day'])))
        file.write('backupHour={}\n'.format(backupSchedule['hour']))
        file.write('dailyClean={}\n'.format(dailyCleanSchedule))
        file.write('weeklyDay={}\n'.format(self.dayAsInt(weeklyCleanSchedule['day'])))
        file.write('weeklyHour={}'.format(weeklyCleanSchedule['hour']))
        file.close()
    
    def read(self):
        if os.path.isfile(self.file):
            file = open(self.file, 'r')
            lines = file.readlines()
            file.close()
            
            output = {}
            for line in lines:
                if 'ram' in line: output['allottedRam'] = int(line.replace('ram=', ''))
                if 'backupDay' in line: output['backupDay'] = int(line.replace('backupDay=', ''))
                if 'backupHour' in line: output['backupHour'] = int(line.replace('backupHour=', ''))
                if 'dailyClean' in line: output['dailyClean'] = int(line.replace('dailyClean=', ''))
                if 'weeklyDay' in line: output['weeklyDay'] = int(line.replace('weeklyDay=', ''))
                if 'weeklyHour' in line: output['weeklyHour'] = int(line.replace('weeklyHour=', ''))
            return output
        else:
            file = open(self.file, 'w')
            file.close()
            return None
        








