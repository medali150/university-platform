# Contributing to University Platform

Thank you for your interest in contributing to the University Platform! This document provides guidelines and information for contributors.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- Python 3.13+
- Node.js 18+
- PostgreSQL 14+
- Git
- Docker (optional, but recommended)

### Setting Up the Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/medali150/university-platform.git
   cd university-platform
   ```

2. **Backend Setup**
   ```bash
   cd api
   python -m venv ../.venv
   source ../.venv/bin/activate  # On Windows: ..\.venv\Scripts\activate
   pip install -r requirements.txt
   python -m prisma generate
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   npm install
   ```

4. **Admin Panel Setup**
   ```bash
   cd apps/admin-panel
   npm install
   ```

## Development Workflow

### Branching Strategy

We use the following branch naming conventions:

- `feature/` - New features (e.g., `feature/student-dashboard`)
- `fix/` - Bug fixes (e.g., `fix/login-validation`)
- `docs/` - Documentation updates (e.g., `docs/api-endpoints`)
- `refactor/` - Code refactoring (e.g., `refactor/auth-module`)
- `test/` - Test additions or updates (e.g., `test/user-service`)

### Making Changes

1. Create a new branch from `main`:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit them with clear, descriptive messages:
   ```bash
   git commit -m "feat: add student attendance tracking"
   ```

3. Push your branch and create a Pull Request:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

## Code Style

### Python (Backend)

- Follow [PEP 8](https://pep8.org/) style guide
- Use type hints where applicable
- Write docstrings for functions and classes

### TypeScript (Frontend)

- Use ESLint and Prettier for code formatting
- Follow React best practices
- Use TypeScript types and interfaces

## Testing

### Backend Testing
```bash
cd api
pytest
```

### Frontend Testing
```bash
cd frontend
npm run test
```

## Pull Request Guidelines

1. Fill out the PR template completely
2. Link any related issues
3. Ensure all tests pass
4. Request review from maintainers
5. Address feedback promptly

## Need Help?

If you have questions or need help:

1. Check the [README](README.md) for documentation
2. Open an issue for bug reports or feature requests
3. Contact the development team

## License

By contributing, you agree that your contributions will be licensed under the MIT License.
