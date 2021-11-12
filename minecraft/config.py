# Purpose: When called, asks user for input to configure setup; should ask for the following items:
# - Backup date and time
# - Clean up schedule
#   - Weekly cleanup
#   - Daily cleanup
# - RAM to allot to server

import os

from minecraft.version import Versioner

class Config:
    file = 'config.conf'
    ram = [1024, 2048, 3072, 4096, 6144, 8192]
    weekdays = ['S', 'M', 'T', 'W', 'R', 'F', 'A']
    hours = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24]
    
    def confirmInput(self, response, accepted):
        if response in accepted:
            return response
        else:
            print('Invalid response [{}]'.format(response))
            if type(response) is int:
                return self.confirmInput(int(input()), accepted)
            else:
                return self.confirmInput(input(), accepted)
                
    def dayAsInt(self, day):
        if day == 'S': return 0
        if day == 'M': return 1
        if day == 'T': return 2
        if day == 'W': return 3
        if day == 'R': return 4
        if day == 'F': return 5
        if day == 'A': return 6
            
    def allottedRam(self):
        # TODO: Check Pi's RAM to show to user
        print('How much RAM would you like to dedicate to your server? NOTE: Please be aware of you MinePi\'s limitations. {}'.format(self.ram))
        ram = self.confirmInput(int(input()), self.ram)
        return ram
    
    def backupSchedule(self):
        print('What day would you like to backup your server? {}'.format(self.weekdays))
        day = self.confirmInput(input(), self.weekdays)
        
        print('What hour (UTC) would you like to backup your server?')
        hour = self.confirmInput(int(input()), self.hours)
        
        return '{}-{}'.format(self.dayAsInt(day), hour)
    
    def dailyCleanSchedule(self):
        print('What hour (UTC) would you like to run daily cleanup of your server?')
        hour = self.confirmInput(int(input()), self.hours)
        return hour
    
    def weeklyCleanSchedule(self):
        print('What day would you like to run weekly cleanup of your server? {}'.format(self.weekdays))
        day = self.confirmInput(input(), self.weekdays)
        
        print('What hour (UTC) would you like to backup your server?')
        hour = self.confirmInput(int(input()), self.hours)
        
        return '{}-{}'.format(self.dayAsInt(day), hour)
            
    def start(self):
        print('Starting config...')
        ram = allottedRam()
        backupSchedule = backupSchedule()
        dailyCleanSchedule = dailyCleanSchedule()
        weeklyCleanSchedule = weeklyCleanSchedule()
        
        config = open(self.file, 'a')
        config.write('ram={}'.format(ram))
        config.write('backup={}'.format(backupSchedule))
        config.write('dailySched={}'.format(dailyCleanSchedule))
        config.write('weeklySched={}'.format(weeklyCleanSchedule))
        config.close()
        print('Config completed! Continuing with initial setup...')

