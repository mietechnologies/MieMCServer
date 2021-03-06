# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- The user can now add configuration for uploading server backups to an external file server.
  - This configuration exists under the Maintenance section of the config and can be updated by calling `python main.py -uc maintenance`.
  - If the user has configured these settings and the project fails to upload a backup to the server for any reason, the project generates an email to send to the server admins.

### Changed

### Deprecated

### Removed

### Fixed

### Security
## [1.2.1] - 2022.2.18

### Fixed
- End trimming wasn't being properly called.
- System username was not being fetched correctly.
- Extraneous maintenace arguments were removed.

## [1.2.0] - 2022.02.11

### Added
- Functionality that allows user to schedule, start, or stop maintenance on their Minecraft server or hosting system.
- The ability to run the user's own custom shell scripts placed in `./scripts/custom-command.sh`.
- The user now has the ability to configure settings to post messages into their Discord server.
  - When the system runs into an unhandled error it will now post a message to a Discord server if configured.
- The user can now open a command-line-like session with '-c' (with no argument) to issue a series of server commands.
- The project now asks for and stores the server address during configuration to use in conjuction with RCON.
- Functionality to automatically sign Minecraft's EULA upon user acceptance.
- The user can now update a setting collection with '-uc'.

### Changed
- The reboot process now issues a statement to the players on the server informing them that the server will be saved and stopped in 30 seconds for the server to restart. After the server is stopped, the system will wait for 60 seconds before rebooting.

### Fixed
- When restarting the server, the project would start as if running on a RaspberryPi and start services specific to that system that were causing system errors and generating an egregious number of emails.

### Security
- Any passwords stored within the config are now encrypted.
  - **It is not recommended that the user update any password manually via the config file.**
- Password input is now hidden during setup.

## [1.1.2] - 2022.01.27

### Fixed
- An issue with the Emailer preventing it from sending emails as expected.
- Paper splits entity, poi, and region data for the end regions into separate directories. Previously, only data in the `/region` directory was being removed during end trimming. Now, data for all subdirectories in the appropriate directory is removed.

## [1.1.1] - 2022.01.27

### Added
- The project now fetches the system username to use for scheduling cron jobs.

## [1.1.0] - 2021.12.27

### Added
- Implemented GitHub templates for pull request and pull request review.
- Transferred functionality for running on Raspberry Pi from the [MinePi](https://github.com/Michaelcraun/MinePi) project. 
  - The system's CPU temperature is monitored at intervals configured by the user. 
  - If the system's temperature reaches a critical level, an email is generated to inform the user and the system is restarted.

## [1.0.0] - 2021.12.12
