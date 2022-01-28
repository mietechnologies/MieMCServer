# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- The ability to run a user's own custom shell scripts placed in `./scripts/custom-command.sh`
- Discord Integration. The user now has the ability to configure settings to post messages into their Discord server.
  - Unhandled exceptions. When the system runs into an unhandled error it will now post a message to your configured Discord server.
- Password input is now hidden during setup
- Command Terminal. You can now open a command terminal with '-c' with no additional arguments.

### Changed

### Deprecated

### Removed

### Fixed
- The temperature monitor was starting even when it hadn't been configured.

### Security

## [1.1.0] - 2021.12.27

### Added
- Added GitHub templates for pull request and pull request review.
- Rewrote README with the goal of making the workflow of this project clear to future developers.
- Merged MinePi project (custom functionality for running this project on Raspberry Pi). When running this project on a Raspberry Pi, the project now monitors the system's CPU temperature and shuts down if it detects a critical event.

## [1.0.0] - 2021.12.12
