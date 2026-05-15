# Contributing Guide

## How to Contribute

We welcome contributions to the Identity Risk Scoring Engine! This document provides guidelines for contributing.

### Code of Conduct

- Be respectful and inclusive
- Focus on ideas, not individuals
- Help others learn and grow

### Getting Started

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Make your changes
4. Write tests for new functionality
5. Ensure all tests pass
6. Commit with clear messages
7. Push to your fork
8. Open a Pull Request

### Development Guidelines

#### Code Style

- Follow PEP 8 Python style guide
- Use black for formatting: `black src/`
- Use type hints for function signatures
- Keep functions focused and single-purpose

#### Testing

- Write unit tests for all new code
- Aim for >80% test coverage
- Use pytest framework
- Include both happy path and error cases

```bash
# Run tests with coverage
pytest tests/ --cov=src --cov-report=term-missing
```

#### Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions
- Include examples in documentation
- Document design decisions in ARCHITECTURE.md

#### Commit Messages

Follow conventional commits:

```
type(scope): description

feat(iam): add MFA enforcement for admins
fix(risk): correct behavioral score calculation
docs(architecture): clarify policy evaluation flow
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

### Pull Request Process

1. **Title**: Clear, concise description
2. **Description**:
   - Problem statement
   - Solution approach
   - Related issues (#123)
3. **Testing**:
   - All tests pass
   - New tests for new code
   - No regressions
4. **Documentation**:
   - Updated docs/
   - Added docstrings
   - Examples if applicable

### Review Expectations

- Code review by maintainers
- Address feedback constructively
- Iterative improvements are normal
- Aim for consensus on design

### Areas for Contribution

#### High Priority

- [ ] ML-based anomaly detection
- [ ] Real-time dashboard visualization
- [ ] GraphQL API layer
- [ ] Multi-tenancy support

#### Medium Priority

- [ ] Enhanced threat intelligence integration
- [ ] Advanced audit capabilities
- [ ] Performance optimizations
- [ ] Additional language bindings

#### Good for First-time Contributors

- [ ] Documentation improvements
- [ ] Code examples
- [ ] Test coverage expansion
- [ ] Bug fixes with existing tests

### Reporting Issues

#### Bug Reports

Include:

- Steps to reproduce
- Expected vs. actual behavior
- Environment (Python version, OS, etc.)
- Error traces/logs

#### Feature Requests

Include:

- Use case/problem statement
- Proposed solution
- Alternative approaches
- Impact assessment

### Security

Found a security vulnerability? Please email security@example.com rather than using the issue tracker.

### License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Check existing documentation
- Search existing issues
- Ask in discussions
- Email maintainers

Thank you for contributing!
