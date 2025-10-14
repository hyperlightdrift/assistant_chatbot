"""Pytest configuration and shared fixtures for the test suite."""

import pytest
import sys
import os
from unittest.mock import Mock, MagicMock
from datetime import datetime, date, timedelta

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def mock_calendar_service():
    """Create a comprehensive mock Google Calendar service."""
    service = Mock()
    
    # Mock events operations
    service.events.return_value.insert.return_value.execute.return_value = {
        'id': 'test_event_id',
        'htmlLink': 'https://calendar.google.com/event?eid=test_event_id',
        'summary': 'Test Event',
        'start': {'dateTime': '2024-01-15T10:00:00+00:00'},
        'end': {'dateTime': '2024-01-15T11:00:00+00:00'}
    }
    
    service.events.return_value.list.return_value.execute.return_value = {'items': []}
    service.events.return_value.delete.return_value.execute.return_value = {}
    
    return service


@pytest.fixture
def mock_tasks_service():
    """Create a comprehensive mock Google Tasks service."""
    service = Mock()
    
    # Mock tasklists operations
    service.tasklists.return_value.list.return_value.execute.return_value = {
        'items': [{'id': 'default_tasklist_id', 'title': 'Default List'}]
    }
    
    # Mock tasks operations
    service.tasks.return_value.list.return_value.execute.return_value = {'items': []}
    service.tasks.return_value.insert.return_value.execute.return_value = {
        'id': 'test_task_id',
        'title': 'Test Task',
        'status': 'needsAction'
    }
    service.tasks.return_value.delete.return_value.execute.return_value = {}
    
    return service


@pytest.fixture
def sample_datetime():
    """Provide a sample datetime for testing."""
    return datetime(2024, 1, 15, 10, 30, tzinfo=datetime.now().astimezone().tzinfo)


@pytest.fixture
def sample_date():
    """Provide a sample date for testing."""
    return date(2024, 1, 15)


@pytest.fixture
def sample_events_data():
    """Provide sample events data for testing."""
    return {
        'items': [
            {
                'id': 'event1',
                'summary': 'Meeting 1',
                'start': {'dateTime': '2024-01-15T10:00:00+00:00'},
                'end': {'dateTime': '2024-01-15T11:00:00+00:00'}
            },
            {
                'id': 'event2',
                'summary': 'Meeting 2',
                'start': {'dateTime': '2024-01-15T14:00:00+00:00'},
                'end': {'dateTime': '2024-01-15T15:00:00+00:00'}
            },
            {
                'id': 'event3',
                'summary': 'All Day Event',
                'start': {'date': '2024-01-16'},
                'end': {'date': '2024-01-16'}
            }
        ]
    }


@pytest.fixture
def sample_tasks_data():
    """Provide sample tasks data for testing."""
    return {
        'items': [
            {
                'id': 'task1',
                'title': 'Meeting preparation',
                'status': 'needsAction',
                'due': '2024-01-15T00:00:00Z'
            },
            {
                'id': 'task2',
                'title': 'Buy groceries',
                'status': 'completed',
                'due': '2024-01-16T00:00:00Z'
            },
            {
                'id': 'task3',
                'title': 'Project meeting',
                'status': 'needsAction'
                # No due date
            }
        ]
    }


@pytest.fixture
def mock_datetime_utils():
    """Mock the datetime_utils module."""
    with pytest.MonkeyPatch().context() as m:
        # Mock commonly used datetime_utils functions
        m.setattr('cal.events.datetime_utils.iso_with_offset', 
                 lambda dt: dt.isoformat())
        m.setattr('cal.events.datetime_utils.day_bounds', 
                 lambda d: ('2024-01-15T00:00:00+00:00', '2024-01-15T23:59:59+00:00'))
        yield m


# Test markers for different test categories
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "api: mark test as requiring API access"
    )
