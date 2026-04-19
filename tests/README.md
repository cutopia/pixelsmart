# PixelSmart Test Suite

This directory contains automated tests for PixelSmart Phase 1 functionality.

## Test Coverage

The test suite covers all major components of the Phase 1 implementation:

### Canvas Module (`tests/test_canvas.py`)
- Canvas initialization and dimensions
- Default transparent background
- Drawing tools (pencil, eraser)
- Flood fill algorithm (basic, boundary, same-color edge cases)
- Color picker functionality
- Zoom level bounds

### Palette Manager (`tests/test_palette.py`)
- Palette initialization with 16 colors
- Adding/removing custom colors
- Current color selection
- Minimum color count enforcement
- Save/load palette to/from JSON files
- Handling of transparent color special case

### File I/O Module (`tests/test_fileio.py`)
- Saving projects with and without palettes
- Loading projects from .pxsmart files
- Auto-extension handling (.pxsmart)
- Complete save/load cycles
- Non-existent file handling
- State preservation (zoom, offset)

### Integration Tests (`tests/test_integration.py`)
- Complete user workflows
- Multiple save/load cycles
- Palette persistence across cycles
- Canvas state preservation

## Running Tests

### Using the test runner script:
```bash
./run_tests.sh
```

### Manually with pytest:
```bash
# Activate virtual environment if available
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_canvas.py -v

# Run specific test
pytest tests/test_canvas.py::test_flood_fill_basic -v
```

## Test Results

All 34 tests pass successfully:
- 10 canvas tests
- 9 palette manager tests  
- 9 file I/O tests
- 5 integration tests

## Adding New Tests

When adding new functionality:

1. Create a test in the appropriate `test_*.py` file
2. Use descriptive test names: `test_<functionality>_<scenario>`
3. Test edge cases and error conditions
4. Keep tests independent (no shared state)
5. Use fixtures from `conftest.py` when needed

## Continuous Integration

The test suite is designed to run in CI/CD pipelines. Add this to your workflow:

```yaml
- name: Run tests
  run: |
    source .venv/bin/activate
    pytest tests/ -v --cov=pixelsmart --cov-report=xml
```
