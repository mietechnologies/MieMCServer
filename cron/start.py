# On start, we want to:
# - Backup current world
# - Send logs to owner via email
# - Execute list of user-entered commands
# - Launch server

from main import Main

main = Main()
main.backup()
main.commands()
main.sendLogs()
main.start()
