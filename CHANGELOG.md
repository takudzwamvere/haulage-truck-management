# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- `.editorconfig` for consistent editor settings across contributors
- `CONTRIBUTING.md` with guidelines for commit style and code style

---

## [1.0.0] - 2026-04-21

### Added
- Initial release with full truck, driver, and job management
- REST API via Django Ninja with JWT authentication
- Portal frontend using Django Templates
- Docker and Docker Compose setup for local and production use
- Automated test suite covering API endpoints, portal views, and business logic
- Audit logging for user actions
- PostgreSQL database with `dj-database-url` configuration
- Whitenoise static file serving
