# Contributing to Arabic Voice of Customer Platform

Thank you for your interest in contributing to the Arabic VoC platform! This document provides guidelines for contributing to this Arabic-first feedback processing system.

## Getting Started

### Prerequisites
- Python 3.11+
- PostgreSQL database
- OpenAI API key
- Familiarity with Arabic language processing

### Development Setup
1. Fork the repository
2. Clone your fork: `git clone https://github.com/your-username/arabic-voc-platform.git`
3. Create a virtual environment: `python -m venv venv`
4. Activate virtual environment: `source venv/bin/activate` (Linux/Mac) or `venv\Scripts\activate` (Windows)
5. Install dependencies: `pip install -r requirements.txt`
6. Set up environment variables (see README.md)
7. Run tests: `pytest`

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use type hints for function parameters and return values
- Add comprehensive docstrings for all functions and classes
- Keep line length under 100 characters
- Use meaningful variable names, especially for Arabic text processing

### Arabic Language Guidelines
- Always test with real Arabic text, never use placeholder text
- Consider RTL (right-to-left) layout implications
- Test with various Arabic dialects when possible
- Preserve Arabic diacritics when culturally appropriate
- Handle mixed Arabic/English text scenarios

### Testing Requirements
- Write tests for all new features
- Include Arabic-specific test cases
- Test edge cases (empty strings, very long text, special characters)
- Maintain test coverage above 80%
- Include security tests for input validation

### Security Guidelines
- Validate all user inputs, especially Arabic text
- Sanitize data before database storage
- Test for XSS, SQL injection, and other common vulnerabilities
- Use parameterized queries for database operations
- Implement proper rate limiting

## Types of Contributions

### Bug Reports
- Use the bug report template
- Include Arabic text samples that cause issues
- Provide steps to reproduce
- Include environment details

### Feature Requests
- Use the feature request template
- Consider Arabic language implications
- Discuss cultural considerations
- Provide use cases and examples

### Code Contributions
- Create feature branch: `git checkout -b feature/your-feature-name`
- Write tests first (TDD approach)
- Implement feature with proper error handling
- Update documentation
- Submit pull request using the template

### Documentation
- Update README.md for significant changes
- Add inline code comments for complex logic
- Update API documentation
- Include Arabic language examples

## Commit Message Format
```
type(scope): brief description

Detailed description if needed.

- Include Arabic language considerations
- Reference issue numbers if applicable
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
Scopes: `api`, `ui`, `arabic`, `security`, `performance`, `tests`

## Arabic Language Testing

### Required Test Cases
- Basic Arabic text processing
- Text with diacritics (تشكيل)
- Mixed Arabic/English content
- Arabic numerals vs Latin numerals
- Long Arabic text (> 1000 characters)
- Empty and whitespace-only strings
- Special Arabic characters (e.g., ٱ, ة, ى)

### Cultural Considerations
- Regional dialect variations
- Formal vs informal language
- Religious and cultural sensitivity
- Date and number formatting preferences

## Performance Guidelines
- Profile Arabic text processing functions
- Use caching for expensive operations
- Consider batch processing for multiple texts
- Monitor memory usage with large Arabic texts
- Test with realistic data volumes

## Security Checklist
- [ ] Input validation for Arabic text
- [ ] XSS prevention in display
- [ ] SQL injection prevention
- [ ] Rate limiting implementation
- [ ] Unicode normalization attacks prevention
- [ ] Cultural content appropriateness

## Review Process
1. All PRs require at least one review
2. Arabic language changes require Arabic speaker review
3. Security changes require security review
4. Performance changes require performance testing
5. All tests must pass before merge

## Getting Help
- Check existing issues and documentation
- Join our community discussions
- Ask questions in PR comments
- Contact maintainers for urgent issues

## Recognition
Contributors will be recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- Project documentation
- Community showcases

Thank you for helping make Arabic customer feedback processing more accessible and effective!
