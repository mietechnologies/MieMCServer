<!-- TODO: Add cost breakdown -->
<!-- TODO: Add usage --> 
<!-- TODO: Add license -->
<!-- TODO: Add installation -->

<!-- I think the idea of this project needs to change just slightly. I'm starting to think that the server should run 
on Paper (which doesn't have a way to automatically download, AFAIK) so the project should be modified so that:
- The Pi starts the server automatically whenever it starts up
- The Pi starts the monitoring functionality automatically whenever it starts up
- The Pi schedules cleanup and backup tasks using cron automatically whenever it stats up
The project should NOT:
- Configure the MinePi project automatically (values used will be hardcoded manually)
- Install the latest version of the server if none exist (this will be done by the user manually)
- Check for updates (this will be done by the user and updated manually)
-->

<!-- Directories: below is a list of important directories and their purpose:
- /minePi/minecraft/backups                 -> Used to store backups of the server world
- /minePi/minecraft/server                  -> Where the server files are stored (.jar, /world, etc.)