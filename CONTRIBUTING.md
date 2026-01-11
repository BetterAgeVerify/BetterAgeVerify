
# Contributing to BetterAgeVerify

**Created by luvaary**

Thank you for your interest in contributing to BetterAgeVerify! This document provides guidelines for contributing to the world's most accurate, privacy-first, open-source age verification system.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [How to Contribute](#how-to-contribute)
3. [Development Setup](#development-setup)
4. [Contribution Guidelines](#contribution-guidelines)
5. [Privacy Requirements](#privacy-requirements)
6. [Testing Requirements](#testing-requirements)
7. [Pull Request Process](#pull-request-process)
8. [Code Style](#code-style)
9. [Areas for Contribution](#areas-for-contribution)
10. [Recognition](#recognition)

---

## Code of Conduct

### Our Pledge

BetterAgeVerify is committed to providing a welcoming and inclusive environment for all contributors, regardless of:

- Age, body size, disability, ethnicity, gender identity
- Level of experience, education, socio-economic status
- Nationality, personal appearance, race, religion
- Sexual identity and orientation

### Our Standards

**Positive behaviors:**
- Using welcoming and inclusive language
- Respecting differing viewpoints and experiences
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behaviors:**
- Harassment, trolling, or insulting comments
- Personal or political attacks
- Publishing others' private information
- Any conduct that could reasonably be considered inappropriate

### Enforcement

Violations of the code of conduct should be reported to project maintainers. All complaints will be reviewed and investigated promptly and fairly.

---

## How to Contribute

### Types of Contributions

We welcome:

1. **Bug Reports**: Found an issue? Let us know
2. **Feature Requests**: Have an idea? Share it
3. **Code Contributions**: Submit improvements
4. **Documentation**: Clarify, expand, or correct docs
5. **Testing**: Add test cases, improve coverage
6. **Benchmarking**: Provide datasets, run tests
7. **Design**: UI/UX improvements for demos
8. **Research**: Academic collaboration, papers

### Getting Started

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub
   git clone https://github.com/YOUR_USERNAME/BetterAgeVerify.git
   cd BetterAgeVerify
   ```

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b bugfix/issue-description
   ```

3. **Make your changes**
   - Follow code style guidelines
   - Add tests for new features
   - Update documentation

4. **Test your changes**
   ```bash
   pytest tests/
   python benchmarks/benchmark_accuracy.py
   ```

5. **Commit and push**
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin feature/your-feature-name
   ```

6. **Create Pull Request**
   - Go to GitHub and create a PR
   - Fill out the PR template
   - Wait for review

---

## Development Setup

### Prerequisites

- Python 3.8+
- Git
- Virtual environment (recommended)

### Setup Steps

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/BetterAgeVerify.git
cd BetterAgeVerify

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Verify installation
python src/main.py --version
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run specific test file
pytest tests/test_age_estimator.py -v

# Run benchmarks
python benchmarks/benchmark_accuracy.py
python benchmarks/benchmark_edge_cases.py
```

---

## Contribution Guidelines

### General Principles

1. **Privacy First**: All contributions MUST maintain privacy guarantees
2. **Quality Over Quantity**: Well-tested, documented code preferred
3. **Open and Transparent**: Explain your reasoning and approach
4. **Respectful**: Be kind in code reviews and discussions
5. **Attribution**: Credit luvaary and BetterAgeVerify appropriately

### Commit Messages

Follow conventional commit format:

```
<type>: <description>

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding or updating tests
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `chore`: Maintenance tasks

**Examples:**
```
feat: Add support for video batch processing

Implements batch processing for video files to improve throughput
by 3x. Maintains privacy guarantees with per-frame deletion.

Closes #123
```

```
fix: Correct age bin calculation for edge case

Fixed off-by-one error in get_age_bin() for ages exactly matching
bin boundaries. Added test cases to prevent regression.

Fixes #456
```

### Branch Naming

- `feature/` - New features
- `bugfix/` - Bug fixes
- `docs/` - Documentation
- `test/` - Test improvements
- `refactor/` - Code refactoring

Examples:
- `feature/multi-face-detection`
- `bugfix/confidence-calculation`
- `docs/installation-guide`
- `test/edge-case-coverage`

---

## Privacy Requirements

### Non-Negotiable Privacy Rules

**ALL contributions MUST:**

1. **Maintain immediate data deletion**
   - All biometric data deleted within 1 second
   - No exceptions, no workarounds

2. **Prohibit long-term storage**
   - No caching of facial images
   - No biometric data persistence

3. **Ensure anonymized logging**
   - Logs must contain zero biometric data
   - No personally identifiable information

4. **Preserve offline capability**
   - Core functionality must work offline
   - Cloud features must be optional

5. **Comply with "No More Data!" license**
   - All code must respect license terms
   - No license violations permitted

### Privacy Review Checklist

Before submitting, verify:

- [ ] No facial images stored beyond processing
- [ ] No biometric templates cached
- [ ] Deletion timeout enforced (< 1 second)
- [ ] Logs contain no personal data
- [ ] Offline mode still functional
- [ ] Privacy tests passing
- [ ] Documentation updated

**If any box is unchecked, your PR will be rejected.**

---

## Testing Requirements

### Required Tests

**For new features:**
- Unit tests for all new functions
- Integration tests for feature workflows
- Edge case tests for robustness
- Performance tests if applicable

**For bug fixes:**
- Test case reproducing the bug
- Verification test showing fix works
- Regression tests to prevent recurrence

### Test Coverage

- Aim for >80% code coverage
- Critical paths require 100% coverage
- Privacy functions require comprehensive testing

### Running Tests Locally

```bash
# Unit tests
pytest tests/test_age_estimator.py -v
pytest tests/test_utils.py -v

# Coverage report
pytest tests/ --cov=src --cov-report=term-missing

# Specific test
pytest tests/test_age_estimator.py::TestModelArchitectures::test_wideresnet_initialization -v
```

### Writing Good Tests

```python
def test_feature_name():
    """Test description explaining what and why."""
    # Arrange: Set up test data
    estimator = BetterAgeVerifyEstimator()
    test_image = create_test_image()
    
    # Act: Execute the feature
    result = estimator.estimate_age(test_image)
    
    # Assert: Verify expected behavior
    assert result["success"] == True
    assert result["predicted_age"] > 0
    
    # Cleanup: Ensure privacy
    assert test_image is None or test_image.closed
```

---

## Pull Request Process

### Before Submitting

1. **Ensure tests pass**
   ```bash
   pytest tests/ -v
   ```

2. **Check code style**
   ```bash
   black src/ tests/ demos/
   flake8 src/ tests/ demos/
   ```

3. **Update documentation**
   - README.md if user-facing
   - Docstrings for new functions
   - Relevant docs/ files

4. **Add to ROADMAP.md** if applicable

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Performance improvement
- [ ] Refactoring

## Privacy Compliance
- [ ] Maintains immediate data deletion
- [ ] No biometric data storage
- [ ] Anonymized logging only
- [ ] Offline mode preserved
- [ ] Privacy tests passing

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] All tests passing locally
- [ ] Coverage maintained/improved

## Documentation
- [ ] Code comments updated
- [ ] Documentation updated
- [ ] ROADMAP.md updated (if applicable)

## Checklist
- [ ] Code follows project style
- [ ] Self-review completed
- [ ] No breaking changes (or justified)
- [ ] Commit messages are clear

## Related Issues
Closes #(issue number)
```

### Review Process

1. **Automated Checks**: CI/CD runs tests
2. **Code Review**: Maintainer reviews code
3. **Privacy Review**: Privacy compliance verified
4. **Discussion**: Questions and suggestions
5. **Approval**: PR approved or changes requested
6. **Merge**: Merged into main branch

### After Merge

- Your contribution is credited
- Changes included in next release
- You're officially a BetterAgeVerify contributor!

---

## Code Style

### Python Style Guide

Follow PEP 8 with these specifics:

**Formatting:**
- Use `black` for automatic formatting
- Line length: 100 characters (not 80)
- Indentation: 4 spaces (no tabs)

**Naming:**
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

**Imports:**
```python
# Standard library
import sys
from pathlib import Path

# Third-party
import torch
import numpy as np

# Local
from src.config import Config
from src.utils import ImageProcessor
```

**Docstrings:**
```python
def estimate_age(self, image: Image.Image) -> Dict:
    """
    Estimate age from facial image with immediate data deletion.
    
    Args:
        image: PIL Image containing a face
        
    Returns:
        Dictionary containing:
            - success: bool
            - predicted_age: float
            - confidence: float
            - timestamp: float
            
    Raises:
        RuntimeError: If data deletion exceeds timeout
    """
    pass
```

### File Headers

```python
"""
BetterAgeVerify - [Module Name]
Created by luvaary

[Brief description of module purpose]
"""
```

---

## Areas for Contribution

### High Priority

1. **Model Improvements**
   - Better age estimation models
   - Faster inference
   - Improved edge case handling

2. **Edge Case Detection**
   - More robust occlusion detection
   - Better lighting analysis
   - Improved angle detection

3. **Testing**
   - More comprehensive test coverage
   - Real-world dataset testing
   - Stress testing and benchmarks

4. **Documentation**
   - Tutorial videos
   - Translation to other languages
   - Use case examples

### Medium Priority

5. **Performance Optimization**
   - GPU acceleration improvements
   - Batch processing optimizations
   - Memory usage reduction

6. **Platform Support**
   - Mobile integration (iOS, Android)
   - Web browser support (WASM)
   - Embedded systems (Raspberry Pi)

7. **UI/UX**
   - Better demo interfaces
   - Web dashboard
   - Mobile apps

### Research Opportunities

8. **Academic Collaboration**
   - Benchmark against academic datasets
   - Publish research papers
   - Novel age estimation techniques

9. **Fairness and Bias**
   - Demographic fairness analysis
   - Bias detection and mitigation
   - Cross-cultural validation

10. **Privacy Technology**
    - Federated learning
    - Differential privacy
    - Homomorphic encryption

---

## Recognition

### Contributors

All contributors are recognized in:
- README.md contributors section
- Release notes
- Project documentation

### Hall of Fame

Significant contributors may be featured in:
- Project website (when launched)
- Media mentions
- Conference presentations

### How Credit Works

- All commits attributed to authors
- PR descriptions cite contributors
- Documentation credits specific contributions
- luvaary retains project ownership and vision

---

## Questions?

### Getting Help

- **Documentation**: Check `/docs/` folder
- **Issues**: Search existing GitHub issues
- **Discussions**: GitHub Discussions (when available)
- **Email**: Contact project maintainers

### Reporting Bugs

Use this template:

```markdown
**Bug Description**
Clear description of the bug

**To Reproduce**
1. Step one
2. Step two
3. ...

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Windows 10]
- Python Version: [e.g., 3.9.7]
- BetterAgeVerify Version: [e.g., 1.0.0]

**Additional Context**
Screenshots, logs, etc.
```

### Feature Requests

Use this template:

```markdown
**Feature Description**
Clear description of the feature

**Use Case**
Why is this needed? Who benefits?

**Proposed Solution**
How might this work?

**Alternatives Considered**
Other approaches you've thought about

**Additional Context**
Mockups, examples, references
```

---

## License

By contributing to BetterAgeVerify, you agree that your contributions will be licensed under the **"No More Data!" License**.

This means:
- Your code can be used freely
- But privacy requirements must be maintained
- Attribution to luvaary and BetterAgeVerify required
- No biometric data sales or long-term storage

See `LICENSE` for full terms.

---

## Thank You!

**Every contribution makes BetterAgeVerify better.**

Whether you're:
- Fixing a typo
- Adding a feature
- Improving documentation
- Reporting a bug
- Suggesting an idea

**You're helping build the privacy-first, superior alternative to proprietary age verification systems.**

**Together, we're proving that open-source can outperform closed systems while respecting user privacy.**

---

*Contributing guidelines created by luvaary for BetterAgeVerify*  
*Building the global gold standard in age verification, one contribution at a time*

**Ready to contribute? Fork the repo and get started!**

**BetterAgeVerify: Open. Transparent. Superior. Built by the community, for the community.**

