# Contributing to RPGer MongoDB MCP Server

## Welcome Contributors! 🎉

We're thrilled that you're interested in contributing to the RPGer MongoDB MCP Server. This document provides guidelines for contributing to the project.

## Code of Conduct

Please be respectful, inclusive, and considerate of others. Harassment and discrimination are not tolerated.

## Getting Started

1. Fork the repository
2. Clone your fork
3. Create a new branch for your feature or bugfix
4. Make your changes
5. Run tests
6. Submit a pull request

## Development Setup

### Prerequisites
- Node.js (v14.0.0 or later)
- npm (v6.0.0 or later)
- MongoDB (v4.4 or later)

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd mcp-servers/mongodb-mcp-server

# Install dependencies
npm install
```

## Development Workflow

### Running the Server
```bash
# Development mode
npm run start:dev

# Production mode
npm start
```

### Running Tests
```bash
# Run all tests
npm test

# Run tests with coverage
npm run test:coverage
```

### Linting
```bash
# Run ESLint
npm run lint

# Automatically fix linting issues
npm run lint:fix
```

## Contribution Process

### Branching Strategy
- `main`: Stable production code
- `develop`: Integration branch for upcoming release
- Feature branches: `feature/short-description`
- Bugfix branches: `bugfix/short-description`

### Pull Request Guidelines
1. Describe the purpose of your changes
2. Reference any related issues
3. Include screenshots for visual changes
4. Ensure all tests pass
5. Update documentation if needed

## Code Quality Standards

### Coding Conventions
- Follow ESLint rules
- Write clear, concise comments
- Use meaningful variable and function names
- Keep functions small and focused
- Write unit tests for new functionality

### Performance Considerations
- Minimize database queries
- Use efficient MongoDB queries
- Implement proper indexing
- Handle errors gracefully

## Tool Development Guidelines

### Adding New Tools
1. Define clear input schemas
2. Implement comprehensive error handling
3. Add unit tests
4. Update documentation
5. Consider performance implications

### Tool Schema Requirements
- Clear, descriptive name
- Comprehensive input validation
- Meaningful error messages
- Consistent return structure

## Security Considerations
- Never commit sensitive information
- Use environment variables for configuration
- Validate and sanitize all inputs
- Implement proper access controls
- Follow MongoDB security best practices

## Reporting Issues

### Bug Reports
- Use GitHub Issues
- Provide detailed description
- Include reproduction steps
- Specify environment details
- Attach relevant logs or screenshots

### Feature Requests
- Explain the use case
- Describe potential implementation
- Discuss potential impact

## Review Process
- Maintainers will review pull requests
- Feedback will be provided constructively
- Multiple approvals required for merging

## Documentation

### Updating Docs
- Keep README.md current
- Update inline code comments
- Maintain example files
- Document new features and changes

## Community
- Be kind and supportive
- Help fellow contributors
- Share knowledge
- Respect diverse perspectives

## License
By contributing, you agree to the MIT License terms.

## Questions?
Open an issue or contact the maintainers.

Happy Coding! 🚀