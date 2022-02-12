# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.2.0] - 2022.02.11

### Added
- The project now fetches the system username to use for scheduling cron jobs.
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
- An issue with the Emailer preventing it from sending emails as expected.

### Security
- Any passwords stored within the config are now encrypted.
  - **It is not recommended that the user update any password manually via the config file.**
- Password input is now hidden during setup.

## [1.1.0] - 2021.12.27

### Added
- Added GitHub templates for pull request and pull request review.
- Rewrote README with the goal of making the workflow of this project clear to future developers.
- Merged MinePi project (custom functionality for running this project on Raspberry Pi). When running this project on a Raspberry Pi, the project now monitors the system's CPU temperature and shuts down if it detects a critical event.

## [1.0.0] - 2021.12.12
