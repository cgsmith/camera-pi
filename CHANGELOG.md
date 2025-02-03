# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased] 

### Added
- Introduced `MockGPIO` for local testing, which simulates GPIO pins using `simulated_pins.json`.
- Added `simulated_pins.json` file to mock GPIO pin states. Example configurations:
  - PIN `16` for `SYSTEM_ARMED_PIN`.
  - PIN `20` for `SYSTEM_ALARM_PIN`.
- Updated `README.md` with information about using the mock GPIO library and testing on a specific subnet.

### Changed
- Simplified language conversion by replacing `distutils.util.strtobool` with a custom `to_bool` function.
- Dynamically constructed file paths for `cameras.json` and locale directories using `USER_HOME` from environment variables.
- Enhanced file path handling for improved compatibility in local and production environments.

### Fixed
- Missing newline in `requirements.txt` to meet formatting standards.
- Improved error handling and simulation defaults for `MockGPIO` when files are missing or contain invalid JSON.


## [1.0.0] 2024-07-03

### Added
- Integrated Gmail SMTP with `smtplib` for email notifications, replacing Postmark API.
- Support for localization using `gettext` for handling translations.
  - Set up language files (e.g., `base.po` for German and English).
  - Updated key log messages for multilingual support.
- Added new configurations in `.env.example` for:
  - Email server setup (`EMAIL_SERVER`, `EMAIL_PORT`).
  - Raspberry Pi-specific paths to improve the setup process.

### Changed
- Updated email handling workflow to integrate with Gmail SMTP instead of Postmark API.

### Removed
- Deprecated or unused libraries from `requirements.txt` (e.g., `postmarker`).

### Fixed
- Ensured compatibility with localized file paths and user roles in a Raspberry Pi environment.


[Unreleased]: 
[1.0.0]: https://bitbucket.org/mount7freiburg/security-camera-privacy-mask/src/1.0.0/