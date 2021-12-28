# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Added first draft of the README
- Password input is now hidden during setup

### Changed

### Deprecated

### Removed

### Fixed
- The temperature monitor was starting even when it hadn't been configured.

### Security

## [1.1.2] - 2022.01.27

### Fixed
- An issue with the Emailer preventing it from sending emails as expected
- Unknown to us, Paper servers split entity, poi, and region data for the end 
regions into separate directories. Previously, we were only removing region
data for the /region directory. Now, we remove region data for all 
subdirectories in the /server/world_the_end/DIM1/ directory.

## [1.1.1] - 2022.01.27

### Added
- Added automatic fetching of the system username for use in CronTab so that we do not
have to ask the user for it and allow for automatic cron job scheduling.

## [1.1.0] - 2021.12.27

### Added
- Added GitHub templates for pull request and pull request review.
- Rewrote README with the goal of making the workflow of this project clear to future developers.
- Merged MinePi project (custom functionality for running this project on Raspberry Pi). When running this project on a Raspberry Pi, the project now monitors the system's CPU temperature and shuts down if it detects a critical event.

## [1.0.0] - 2021.12.12
