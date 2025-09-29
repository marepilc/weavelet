# Claude Development Rules for Weavelet

## Development Approach
- **Always start from tests (TDD)**: Write tests first, then implement functionality
- **Strict typing**: Use type hints throughout the codebase, ensure mypy passes with strict settings
- **Package manager**: Use `uv` for all dependency management and virtual environment operations

## Code Quality Tools
- **Linting**: Use `ruff` for linting and code formatting
- **Type checking**: Use `mypy` with strict configuration
- **Testing**: Use `pytest` for all tests

## Commands to Run
Before considering any task complete, always run these commands:

```bash
# Install/sync dependencies
uv sync

# Run tests (TDD - write these first!)
.venv/bin/python -m pytest

# Type checking
.venv/bin/python -m mypy weavelet

# Linting and formatting
.venv/bin/python -m ruff check weavelet
.venv/bin/python -m ruff format weavelet
```

## Development Workflow
1. Write failing tests first (TDD)
2. Implement minimal code to make tests pass
3. Run type checking with mypy
4. Run linting with ruff
5. Refactor if needed while keeping tests green
6. Only then consider the task complete

## Project Structure
- Core functionality in `weavelet/`
- Tests in `tests/`
- Examples in root or `examples/`
- Use absolute imports in tests: `from weavelet import ...`

## Type Hints
- All functions must have return type annotations
- All parameters must have type hints
- Use `typing` module for complex types
- Prefer `list[str]` over `List[str]` (Python 3.12+ syntax)

## Testing
- Test file naming: `test_*.py`
- Use descriptive test names that explain the behavior
- Test both happy path and edge cases
- Mock external dependencies when needed