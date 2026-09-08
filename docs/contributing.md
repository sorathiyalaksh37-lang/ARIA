# Contributing to ARIA

Thank you for your interest in contributing to ARIA (AI-powered Rapid Incident Assessment)! This document provides guidelines for contributing to the project.

---

## Table of Contents

1. [Code of Conduct](#code-of-conduct)
2. [Getting Started](#getting-started)
3. [Development Workflow](#development-workflow)
4. [Code Standards](#code-standards)
5. [Testing Guidelines](#testing-guidelines)
6. [Pull Request Process](#pull-request-process)
7. [Issue Guidelines](#issue-guidelines)
8. [Documentation](#documentation)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of age, body size, disability, ethnicity, gender identity, experience level, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Expected Behavior

- Use welcoming and inclusive language
- Be respectful of differing viewpoints
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards others

### Unacceptable Behavior

- Trolling, insulting comments, or personal attacks
- Public or private harassment
- Publishing others' private information
- Other conduct that could reasonably be considered inappropriate

---

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+ with PostGIS
- Redis 7.0+
- Git
- Docker (optional)

### Fork and Clone

```bash
# Fork the repository on GitHub
# Then clone your fork
git clone https://github.com/YOUR_USERNAME/ARIA.git
cd ARIA

# Add upstream remote
git remote add upstream https://github.com/sorathiyalaksh37-lang/ARIA.git
```

### Set Up Development Environment

```bash
# Backend
cd backend
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Frontend
cd frontend
npm install
```

### Environment Configuration

```bash
# Copy example env
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env.development

# Edit with your values (use test API keys for development)
```

---

## Development Workflow

### 1. Create a Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

### Branch Naming Convention

- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/updates
- `chore/` - Maintenance tasks

Examples:
- `feature/add-voice-transcription`
- `fix/hospital-ranking-bug`
- `docs/update-api-guide`

### 2. Make Changes

```bash
# Make your changes
# Write tests
# Update documentation
```

### 3. Commit Your Changes

Follow conventional commits:

```bash
git add .
git commit -m "feat: add voice transcription support"
```

**Commit Message Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Formatting (no code change)
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance

**Examples:**
```bash
git commit -m "feat(backend): add WebSocket reconnection logic"
git commit -m "fix(frontend): resolve map marker clustering issue"
git commit -m "docs: update deployment guide for AWS"
git commit -m "test(agents): add unit tests for triage agent"
```

### 4. Keep Your Branch Updated

```bash
# Fetch upstream changes
git fetch upstream

# Rebase on main
git rebase upstream/main

# Or merge if preferred
git merge upstream/main
```

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

---

## Code Standards

### Python (Backend)

**Style Guide:** PEP 8

**Formatting:**
```bash
# Format with black
black app/

# Sort imports
isort app/

# Lint
flake8 app/
pylint app/
```

**Type Hints:**
```python
# Always use type hints
from typing import List, Optional

async def get_hospitals(
    city: str,
    radius_km: float = 10.0
) -> List[Hospital]:
    """Get hospitals in a city.
    
    Args:
        city: City name
        radius_km: Search radius in kilometers
        
    Returns:
        List of Hospital objects
    """
    pass
```

**Docstrings:**
```python
def calculate_eta(distance_km: float, traffic_level: str) -> float:
    """Calculate estimated time of arrival.
    
    Uses ML model to predict ETA based on distance and traffic.
    
    Args:
        distance_km: Distance in kilometers
        traffic_level: Traffic level (LOW, MODERATE, HIGH, SEVERE)
        
    Returns:
        ETA in minutes
        
    Raises:
        ValueError: If distance is negative
        
    Example:
        >>> calculate_eta(5.0, "MODERATE")
        12.5
    """
    pass
```

**Async/Await:**
```python
# Use async for I/O operations
async def fetch_hospitals():
    async with session.get(url) as response:
        return await response.json()

# Use await for async functions
hospitals = await fetch_hospitals()
```

### TypeScript/JavaScript (Frontend)

**Style Guide:** Airbnb JavaScript Style Guide

**Formatting:**
```bash
# Format
npm run format

# Lint
npm run lint

# Type check
npm run type-check
```

**Component Structure:**
```typescript
import React, { useState, useEffect } from 'react';
import { Hospital } from '../types';

interface HospitalListProps {
  city: string;
  onSelect: (hospital: Hospital) => void;
}

export const HospitalList: React.FC<HospitalListProps> = ({ 
  city, 
  onSelect 
}) => {
  const [hospitals, setHospitals] = useState<Hospital[]>([]);
  const [loading, setLoading] = useState(false);
  
  useEffect(() => {
    fetchHospitals();
  }, [city]);
  
  const fetchHospitals = async () => {
    setLoading(true);
    try {
      const data = await api.getHospitals(city);
      setHospitals(data);
    } catch (error) {
      console.error('Failed to fetch hospitals:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div>
      {/* Component JSX */}
    </div>
  );
};
```

### SQL

```sql
-- Use meaningful table/column names
-- Add comments for complex queries
-- Use CTEs for readability

WITH nearby_hospitals AS (
  SELECT 
    id,
    name,
    ST_Distance(location, incident_location) AS distance
  FROM hospitals
  WHERE ST_DWithin(location, incident_location, 50000)
)
SELECT * FROM nearby_hospitals
WHERE distance < 10000
ORDER BY distance
LIMIT 10;
```

---

## Testing Guidelines

### Backend Tests

**Location:** `backend/tests/`

**Run Tests:**
```bash
cd backend
pytest tests/ -v
pytest tests/ -v --cov=app  # With coverage
```

**Test Structure:**
```python
import pytest
from app.services.ml_service import get_ml_service

@pytest.mark.asyncio
async def test_predict_severity():
    """Test severity prediction."""
    ml_service = get_ml_service()
    
    result = await ml_service.predict_severity(
        description="Critical car accident",
        location="Mumbai",
        incident_type="ACCIDENT"
    )
    
    assert result["severity"] == "CRITICAL"
    assert result["confidence"] > 0.7

@pytest.fixture
def sample_incident():
    """Fixture for test incident."""
    return {
        "description": "Test incident",
        "location": (19.0760, 72.8777),
        "type": "MEDICAL"
    }
```

**Coverage Target:** >80%

### Frontend Tests

**Location:** `frontend/src/**/__tests__/`

**Run Tests:**
```bash
cd frontend
npm test
npm test -- --coverage
```

**Test Structure:**
```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import { HospitalList } from '../HospitalList';

describe('HospitalList', () => {
  it('renders hospital list', () => {
    render(<HospitalList city="Mumbai" onSelect={jest.fn()} />);
    expect(screen.getByText('Hospitals')).toBeInTheDocument();
  });
  
  it('calls onSelect when hospital clicked', () => {
    const onSelect = jest.fn();
    render(<HospitalList city="Mumbai" onSelect={onSelect} />);
    
    const hospital = screen.getByText('City Hospital');
    fireEvent.click(hospital);
    
    expect(onSelect).toHaveBeenCalled();
  });
});
```

### Integration Tests

```python
@pytest.mark.integration
async def test_full_incident_workflow():
    """Test complete incident workflow."""
    # Create incident
    incident = await create_incident(test_data)
    
    # Process through agents
    result = await orchestrator.execute(incident)
    
    # Verify results
    assert result.approval_status == "APPROVED"
    assert result.selected_hospital is not None
```

---

## Pull Request Process

### Before Submitting

**Checklist:**
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] All tests pass
- [ ] No console warnings/errors
- [ ] Branch is up to date with main

### Submit Pull Request

1. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create PR on GitHub**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your fork and branch
   - Fill in the PR template

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Other (specify)

## Related Issue
Closes #123

## Changes Made
- Added X feature
- Fixed Y bug
- Updated Z documentation

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Screenshots (if applicable)
[Add screenshots]

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests pass
- [ ] No breaking changes
```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs
   - Tests must pass
   - Linting must pass
   - Coverage must meet threshold

2. **Code Review**
   - At least 1 approval required
   - Address reviewer comments
   - Update code as needed

3. **Merge**
   - Squash and merge preferred
   - Delete branch after merge

---

## Issue Guidelines

### Creating Issues

**Bug Report:**
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Go to '...'
2. Click on '...'
3. See error

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- OS: [e.g., macOS 12.0]
- Browser: [e.g., Chrome 95]
- Version: [e.g., v1.0.0]

## Screenshots
[If applicable]

## Additional Context
Any other relevant information
```

**Feature Request:**
```markdown
## Feature Description
Clear description of the feature

## Problem It Solves
What problem does this solve?

## Proposed Solution
How should it work?

## Alternatives Considered
Other approaches considered

## Additional Context
Any other relevant information
```

### Issue Labels

- `bug` - Something isn't working
- `feature` - New feature request
- `documentation` - Documentation improvements
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention needed
- `priority: high` - High priority
- `priority: low` - Low priority
- `wontfix` - Will not be fixed

---

## Documentation

### Documentation Standards

**Location:**
- Technical docs: `docs/`
- API docs: Auto-generated from code
- README: Project root

**Format:** Markdown

**Structure:**
```markdown
# Title

## Overview
Brief description

## Table of Contents
- [Section 1](#section-1)
- [Section 2](#section-2)

## Section 1
Content...

### Subsection
More content...

## Examples
```code examples```

## References
Links to related docs
```

### API Documentation

**FastAPI:**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class IncidentCreate(BaseModel):
    """Incident creation schema.
    
    Attributes:
        description: Incident description
        location: GPS coordinates (lat, lon)
        incident_type: Type of incident
    """
    description: str
    location: tuple[float, float]
    incident_type: str

@router.post("/incidents", response_model=IncidentResponse)
async def create_incident(
    incident: IncidentCreate,
    current_user: User = Depends(get_current_user)
) -> IncidentResponse:
    """Create a new incident.
    
    Creates an incident and triggers the AI workflow.
    
    Args:
        incident: Incident data
        current_user: Authenticated user
        
    Returns:
        Created incident with ID
        
    Raises:
        HTTPException: If validation fails
        
    Example:
        ```bash
        curl -X POST /api/v1/incidents \\
          -H "Authorization: Bearer TOKEN" \\
          -d '{"description":"Car accident",...}'
        ```
    """
    pass
```

### Updating Documentation

When making changes:
1. Update relevant documentation
2. Add examples if applicable
3. Update API docs if endpoints change
4. Check for broken links
5. Run spell check

---

## Community

### Communication Channels

- **GitHub Issues:** Bug reports, feature requests
- **GitHub Discussions:** Questions, ideas
- **Pull Requests:** Code contributions

### Getting Help

1. Check existing documentation
2. Search closed issues
3. Ask in GitHub Discussions
4. Create a new issue if needed

### Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Recognized in project documentation

---

## Development Tips

### Debugging

**Backend:**
```python
# Use logging
import logging
logger = logging.getLogger(__name__)

logger.debug("Debug info")
logger.info("Info message")
logger.warning("Warning")
logger.error("Error occurred")

# Use debugger
import pdb; pdb.set_trace()
```

**Frontend:**
```typescript
// Use console
console.log('Debug:', data);
console.error('Error:', error);

// Use debugger
debugger;

// React DevTools
// Browser extension
```

### Performance

- Profile slow code
- Optimize database queries
- Use caching where appropriate
- Minimize external API calls
- Implement pagination

### Security

- Never commit secrets
- Validate all inputs
- Use parameterized queries
- Implement rate limiting
- Follow OWASP guidelines

---

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- MAJOR.MINOR.PATCH (e.g., 1.2.3)

### Release Checklist

- [ ] All tests pass
- [ ] Documentation updated
- [ ] CHANGELOG updated
- [ ] Version bumped
- [ ] Tagged in Git
- [ ] Deployed to staging
- [ ] Smoke tests pass
- [ ] Deployed to production

---

## License

By contributing to ARIA, you agree that your contributions will be licensed under the project's license.

---

## Questions?

If you have questions about contributing:
1. Check this guide
2. Search existing issues
3. Ask in GitHub Discussions
4. Create a new issue

---

**Thank you for contributing to ARIA! 🚀**

Every contribution, no matter how small, helps make emergency response faster and more efficient.
