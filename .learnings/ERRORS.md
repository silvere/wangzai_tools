# Errors Log

Record command failures, exceptions, and unexpected behaviors here.

## Format

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**Logged**: ISO-8601 timestamp
**Priority**: high
**Status**: pending
**Area**: frontend | backend | infra | tests | docs | config

### Summary
One-line description of the error

### Details
Full error message, stack trace, and context

### Root Cause
What actually caused the error

### Solution
How it was fixed or worked around

### Prevention
How to avoid this in the future

### Metadata
- Source: command | api | integration
- Related Files: path/to/file.ext
- Tags: tag1, tag2
```

---
