from util.mielib import custominput as ci

class Maintenance:
    data = {}
    backup = {}
    updates = {}
    complete_shutdown = ''
    schedule = ''
    maintenance_running = False
    startup_timeout = 30

    def __init__(self, data: dict) -> None:
        self.data = data
        self.backup = self.data.get("backup", {})
        self.updates = self.data.get("update", {})
        self.complete_shutdown = self.data.get("complete_shutdown", "0 4 1 * *")
        self.schedule = self.data.get("schedule", "0 4 * * *")
        self.maintenance_running = self.data.get('scheduled_running', False)

    def build(self) -> dict:
        print("Warning: A system restart is good practice to clear out any " \
            "residual problems that might still be in RAM. Also, in order to " \
            "run the commands file a server restart is required.")
        restart_cron = ci.cron_date_input("restart")

        print("Warning: It is good practice to backup your server so if any" \
            "thing were to happen, you would be able to revert back to your " \
            "previous backup.")
        backup_cron = ci.cron_date_input("backup Minecraft")
        backup_path = input("Where would you like your backups to be stored? ")
        backup_limit = ci.int_input("How many backups would you like to be " \
            "stored before removing old backups?")

        print("Warning: It is wise to check for updates on a regular basis so " \
            "any bugs the developers might find and fix will be applied to " \
            "your server. We can understand your concern for larger updates, " \
            "so we will ask your permission on if you want us to do bigger " \
            "updates automatically. If not, we will email you and alert you " \
            "of any major updates.")
        update_cron = ci.cron_date_input("check for updates")
        major_updates = ci.bool_input("Would you like me to update to " \
            "major releases?", default=False)

        print("Warning: I have ben preprogrammed with some useful maintenance " \
            "scripts to help keep your server up and running smoothly. It is " \
            "always good to run these scripts so your players experience as " \
            "little server lag as possible.")
        maintenance_cron = ci.cron_date_input("run maintenance scripts")

        self.complete_shutdown = restart_cron
        self.schedule = maintenance_cron
        self.backup['schedule'] = backup_cron
        self.backup['path'] = backup_path
        self.backup['number'] = backup_limit
        self.updates['schedule'] = update_cron
        self.updates['allow_major_update'] = major_updates
        return self.update()

    def update(self) -> dict:
        self.data['complete_shutdown'] = self.complete_shutdown
        self.data['schedule'] = self.schedule
        self.data['backup'] = self.backup
        self.data['update'] = self.updates
        self.data['scheduled_running'] = self.maintenance_running
        return self.data

    def reset(self) -> dict:
        self.complete_shutdown = "0 4 1 * *"
        self.schedule = "0 4 * * *"
        self.backup['schedule'] = "0 3 * * *"
        self.backup['path'] = "~/MC_Backups"
        self.backup['number'] = 1
        self.updates['schedule'] = '0 3 * * 0'
        self.updates['allow_major_update'] = False
        return self.update()

    def path(self) -> str:
        return self.backup.get('path', '~/MC_Backups')

    def backup_limit(self) -> int:
        return self.backup.get('number', 1)

    def backup_schedule(self) -> str:
        return self.backup.get('schedule', '0 3 * * *')

    def update_schedule(self) -> str:
        return self.updates.get('schedule', '0 3 * * 0')
    
    def allows_major_udpates(self) -> bool:
        return self.updates.get('allow_major_update', False)
