# Test Suite Documentation

This directory contains comprehensive pytest tests for the assistant chatbot's calendar and tasks functionality.

## Test Files

### `test_events.py`
Comprehensive tests for Google Calendar events functionality:
- **`create_event`**: Tests event creation with various date/datetime formats
- **`view_events`**: Tests event viewing with filters (title, date ranges, calendar ID)
- **`delete_events`**: Tests event deletion with bulk protection, exact matching, and error handling
- **`is_date_only`**: Tests the helper function for date format detection

### `test_tasks.py`
Comprehensive tests for Google Tasks functionality:
- **`create_task`**: Tests task creation with and without due dates
- **`view_tasks`**: Tests task viewing with filters (title, date)
- **`delete_tasks`**: Tests task deletion with various filtering options

### `conftest.py`
Shared pytest fixtures and configuration:
- Mock services for Google Calendar and Tasks APIs
- Sample data fixtures for events and tasks
- Common test utilities and markers

### `test_create_events.py`
Legacy file kept for backward compatibility. All tests have been moved to `test_events.py`.

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Files
```bash
pytest tests/test_events.py
pytest tests/test_tasks.py
```

### Run Tests by Category
```bash
# Unit tests only
pytest -m unit

# Integration tests only
pytest -m integration

# Event-related tests only
pytest -m events

# Task-related tests only
pytest -m tasks
```

### Run Tests with Coverage
```bash
pytest --cov=cal --cov-report=html
```

### Run Tests with Verbose Output
```bash
pytest -v
```

## Test Coverage

The test suite covers:

### Events (`test_events.py`)
- ✅ Event creation with date-only and datetime formats
- ✅ Event creation with mixed formats
- ✅ Event viewing with title filters
- ✅ Event viewing with datetime ranges
- ✅ Event viewing with date-only ranges
- ✅ Event viewing with string time ranges
- ✅ Event deletion by title (exact and partial matching)
- ✅ Event deletion with datetime objects
- ✅ Bulk deletion protection (10+ events)
- ✅ Forced bulk deletion
- ✅ Scoped deletion ("all" events)
- ✅ Custom calendar ID support
- ✅ Default time window handling
- ✅ Error handling for API failures
- ✅ Edge cases (empty titles, no events found)

### Tasks (`test_tasks.py`)
- ✅ Task creation without due date
- ✅ Task creation with due date (timezone-aware and naive)
- ✅ Task viewing with no filters
- ✅ Task viewing with title filters (case-insensitive)
- ✅ Task viewing with date filters
- ✅ Task viewing with combined filters
- ✅ Task deletion by title
- ✅ Task deletion by date
- ✅ Task deletion with combined filters
- ✅ Task deletion with no filters (all tasks)
- ✅ Error handling for missing task lists
- ✅ Error handling for API failures
- ✅ Handling of tasks with missing fields
- ✅ Case-insensitive title matching
- ✅ Tasks with missing due dates

## Test Architecture

### Mocking Strategy
- **Google API Services**: All Google Calendar and Tasks API calls are mocked
- **External Dependencies**: `datetime_utils` module is mocked where necessary
- **Print Statements**: Console output is captured and verified
- **File System**: No real file system operations are performed

### Fixtures
- **`mock_calendar_service`**: Complete mock of Google Calendar API
- **`mock_tasks_service`**: Complete mock of Google Tasks API
- **`sample_datetime`**: Consistent datetime for testing
- **`sample_date`**: Consistent date for testing
- **`sample_events_data`**: Realistic events data for testing
- **`sample_tasks_data`**: Realistic tasks data for testing

### Test Categories
- **Unit Tests**: Fast, isolated tests with mocked dependencies
- **Integration Tests**: Tests that verify component interactions
- **API Tests**: Tests that would require real API access (currently mocked)

## Error Scenarios Tested

### API Errors
- Service unavailable
- Authentication failures
- Invalid parameters
- Rate limiting
- Network timeouts

### Data Validation
- Empty inputs
- Invalid date formats
- Missing required fields
- Malformed API responses

### Edge Cases
- No events/tasks found
- Empty task lists
- Bulk operations
- Timezone handling
- Case sensitivity

## Adding New Tests

### For New Functions
1. Create test class following naming convention: `Test{FunctionName}`
2. Add comprehensive test methods covering:
   - Happy path scenarios
   - Error conditions
   - Edge cases
   - Input validation

### For New Features
1. Add appropriate pytest markers (`@pytest.mark.unit`, `@pytest.mark.integration`)
2. Update fixtures in `conftest.py` if needed
3. Document new test categories in this README

### Best Practices
- Use descriptive test method names
- Test both success and failure scenarios
- Verify side effects (API calls, print statements)
- Use parametrized tests for similar scenarios
- Keep tests independent and isolated

## Continuous Integration

The test suite is designed to run in CI environments:
- No external dependencies required
- Fast execution (all mocked)
- Comprehensive coverage
- Clear failure reporting
- Configurable via `pytest.ini`
