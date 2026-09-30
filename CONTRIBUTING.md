# Contributing

Thank you for your interest in contributing to Haulage Truck Management!

## Getting Started

1. Fork the repository and clone it locally.
2. Create a new branch: `git checkout -b feat/your-feature-name`
3. Make your changes with clear, descriptive commits.
4. Run the test suite before submitting: `docker-compose exec web python manage.py test --verbosity=2`
5. Open a pull request against `main`.

## Commit Style

Follow the [Conventional Commits](https://www.conventionalcommits.org/) spec:

- `feat:` — new feature
- `fix:` — bug fix
- `docs:` — documentation only
- `style:` — formatting, no logic change
- `refactor:` — code refactor
- `test:` — adding or updating tests
- `chore:` — maintenance tasks

## Code Style

- Follow PEP 8 for Python code.
- Keep functions small and focused.
- Write tests for new business logic.

## Reporting Issues

Open a GitHub issue with a clear description and steps to reproduce.
