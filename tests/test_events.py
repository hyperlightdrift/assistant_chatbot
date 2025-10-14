"""Comprehensive pytest tests for calendar events functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cal.events import create_event, view_events, delete_events, is_date_only
from exceptions import AssistantError


class TestIsDateOnly:
    """Test the is_date_only helper function."""
    
    def test_is_date_only_with_date_string(self):
        """Test that date-only strings return True."""
        assert is_date_only("2024-01-15") is True
        assert is_date_only("2024-12-31") is True
    
    def test_is_date_only_with_datetime_string(self):
        """Test that datetime strings return False."""
        assert is_date_only("2024-01-15T10:30:00") is False
        assert is_date_only("2024-01-15T10:30:00Z") is False
        assert is_date_only("2024-01-15T10:30:00+00:00") is False
    
    def test_is_date_only_edge_cases(self):
        """Test edge cases for is_date_only."""
        assert is_date_only("") is True  # Empty string has no T
        assert is_date_only("just text") is True  # No T in text


class TestCreateEvent:
    """Test the create_event function."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock Google Calendar service."""
        service = Mock()
        service.events.return_value.insert.return_value.execute.return_value = {
            'id': 'test_event_id',
            'htmlLink': 'https://calendar.google.com/event?eid=test_event_id',
            'summary': 'Test Event'
        }
        return service
    
    def test_create_event_with_date_only(self, mock_service):
        """Test creating an all-day event with date-only format."""
        with patch('builtins.print') as mock_print:
            create_event(mock_service, "Test Event", "2024-01-15", "2024-01-15")
            
            # Verify the service was called correctly
            mock_service.events.assert_called_once()
            insert_call = mock_service.events.return_value.insert
            
            # Check the calendar ID
            assert insert_call.call_args[1]['calendarId'] == 'primary'
            
            # Check the event body structure
            event_body = insert_call.call_args[1]['body']
            assert event_body['summary'] == "Test Event"
            assert event_body['start']['date'] == "2024-01-15"
            assert event_body['end']['date'] == "2024-01-15"
            
            # Verify print was called
            mock_print.assert_called_once()
    
    def test_create_event_with_datetime(self, mock_service):
        """Test creating an event with datetime format."""
        with patch('builtins.print') as mock_print:
            create_event(mock_service, "Meeting", "2024-01-15T10:00:00", "2024-01-15T11:00:00")
            
            # Verify the service was called correctly
            insert_call = mock_service.events.return_value.insert
            event_body = insert_call.call_args[1]['body']
            
            assert event_body['summary'] == "Meeting"
            assert event_body['start']['dateTime'] == "2024-01-15T10:00:00"
            assert event_body['end']['dateTime'] == "2024-01-15T11:00:00"
            
            mock_print.assert_called_once()
    
    def test_create_event_mixed_formats(self, mock_service):
        """Test creating an event with mixed date/datetime formats."""
        with patch('builtins.print') as mock_print:
            create_event(mock_service, "Mixed Event", "2024-01-15", "2024-01-15T11:00:00")
            
            # Should use datetime format when either start or end has time
            insert_call = mock_service.events.return_value.insert
            event_body = insert_call.call_args[1]['body']
            
            assert event_body['start']['dateTime'] == "2024-01-15"
            assert event_body['end']['dateTime'] == "2024-01-15T11:00:00"
    
    def test_create_event_api_error(self, mock_service):
        """Test create_event handles API errors."""
        # Mock API to raise an exception
        mock_service.events.return_value.insert.return_value.execute.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            create_event(mock_service, "Test Event", "2024-01-15", "2024-01-15")
    
    def test_create_event_empty_title(self, mock_service):
        """Test creating an event with empty title."""
        with patch('builtins.print') as mock_print:
            create_event(mock_service, "", "2024-01-15", "2024-01-15")
            
            insert_call = mock_service.events.return_value.insert
            event_body = insert_call.call_args[1]['body']
            assert event_body['summary'] == ""


class TestViewEvents:
    """Test the view_events function."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock Google Calendar service."""
        service = Mock()
        return service
    
    @pytest.fixture
    def sample_events_response(self):
        """Sample events response from Google Calendar API."""
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
                }
            ]
        }
    
    def test_view_events_with_title_filter(self, mock_service, sample_events_response):
        """Test viewing events with title filter."""
        mock_service.events.return_value.list.return_value.execute.return_value = sample_events_response
        
        with patch('builtins.print'):
            view_events(mock_service, {'title': 'Meeting'})
            
            # Verify the service was called with correct parameters
            list_call = mock_service.events.return_value.list
            assert list_call.call_args[1]['calendarId'] == 'primary'
            assert list_call.call_args[1]['q'] == 'Meeting'
            assert list_call.call_args[1]['singleEvents'] is True
            assert list_call.call_args[1]['orderBy'] == 'startTime'
    
    def test_view_events_with_datetime_range(self, mock_service, sample_events_response):
        """Test viewing events with datetime range."""
        mock_service.events.return_value.list.return_value.execute.return_value = sample_events_response
        
        start_dt = datetime(2024, 1, 15, 9, 0)
        end_dt = datetime(2024, 1, 15, 17, 0)
        
        with patch('builtins.print'), \
             patch('cal.events.datetime_utils.iso_with_offset') as mock_iso:
            mock_iso.side_effect = ['2024-01-15T09:00:00+00:00', '2024-01-15T17:00:00+00:00']
            
            view_events(mock_service, {'start': start_dt, 'end': end_dt})
            
            list_call = mock_service.events.return_value.list
            assert 'timeMin' in list_call.call_args[1]
            assert 'timeMax' in list_call.call_args[1]
    
    def test_view_events_with_date_only(self, mock_service, sample_events_response):
        """Test viewing events with date-only range."""
        mock_service.events.return_value.list.return_value.execute.return_value = sample_events_response
        
        test_date = date(2024, 1, 15)
        
        with patch('builtins.print'), \
             patch('cal.events.datetime_utils.day_bounds') as mock_day_bounds:
            mock_day_bounds.return_value = ('2024-01-15T00:00:00+00:00', '2024-01-15T23:59:59+00:00')
            
            view_events(mock_service, {'date': test_date})
            
            list_call = mock_service.events.return_value.list
            assert 'timeMin' in list_call.call_args[1]
            assert 'timeMax' in list_call.call_args[1]
    
    def test_view_events_with_string_range(self, mock_service, sample_events_response):
        """Test viewing events with string time range."""
        mock_service.events.return_value.list.return_value.execute.return_value = sample_events_response
        
        with patch('builtins.print'):
            view_events(mock_service, {
                'start': '2024-01-15T09:00:00+00:00',
                'end': '2024-01-15T17:00:00+00:00'
            })
            
            list_call = mock_service.events.return_value.list
            assert list_call.call_args[1]['timeMin'] == '2024-01-15T09:00:00+00:00'
            assert list_call.call_args[1]['timeMax'] == '2024-01-15T17:00:00+00:00'
    
    def test_view_events_no_events_found(self, mock_service):
        """Test viewing events when no events are found."""
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': []}
        
        with patch('builtins.print') as mock_print:
            view_events(mock_service, {})
            
            # Should not print anything when no events found
            mock_print.assert_not_called()
    
    def test_view_events_custom_calendar_id(self, mock_service, sample_events_response):
        """Test viewing events with custom calendar ID."""
        mock_service.events.return_value.list.return_value.execute.return_value = sample_events_response
        
        with patch('builtins.print'):
            view_events(mock_service, {}, calendar_id='custom_calendar_id')
            
            list_call = mock_service.events.return_value.list
            assert list_call.call_args[1]['calendarId'] == 'custom_calendar_id'


class TestDeleteEvents:
    """Test the delete_events function."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock Google Calendar service."""
        service = Mock()
        return service
    
    @pytest.fixture
    def sample_events_for_deletion(self):
        """Sample events that can be deleted."""
        return {
            'items': [
                {'id': 'event1', 'summary': 'Meeting 1'},
                {'id': 'event2', 'summary': 'Meeting 2'},
                {'id': 'event3', 'summary': 'Different Event'}
            ]
        }
    
    def test_delete_events_by_title(self, mock_service, sample_events_for_deletion):
        """Test deleting events by title."""
        mock_service.events.return_value.list.return_value.execute.return_value = sample_events_for_deletion
        mock_service.events.return_value.delete.return_value.execute.return_value = {}
        
        with patch('builtins.print') as mock_print:
            result = delete_events(
                mock_service, 
                title="Meeting", 
                start="2024-01-15T00:00:00+00:00",
                end="2024-01-15T23:59:59+00:00",
                scoped=None,
                forced=False
            )
            
            assert result['status'] == 'deleted'
            assert result['deleted_count'] == 2  # Two events with "Meeting" in title
            
            # Verify delete was called for matching events
            assert mock_service.events.return_value.delete.call_count == 2
            mock_print.assert_called_with("Deleted 2 event(s).")
    
    def test_delete_events_exact_title_match(self, mock_service, sample_events_for_deletion):
        """Test deleting events with exact title match."""
        mock_service.events.return_value.list.return_value.execute.return_value = sample_events_for_deletion
        mock_service.events.return_value.delete.return_value.execute.return_value = {}
        
        with patch('builtins.print'):
            result = delete_events(
                mock_service,
                title="Meeting 1",  # Exact match
                start="2024-01-15T00:00:00+00:00",
                end="2024-01-15T23:59:59+00:00",
                scoped=None,
                forced=False
            )
            
            assert result['deleted_count'] == 1
            assert mock_service.events.return_value.delete.call_count == 1
    
    def test_delete_events_with_datetime_objects(self, mock_service, sample_events_for_deletion):
        """Test deleting events with datetime objects."""
        mock_service.events.return_value.list.return_value.execute.return_value = sample_events_for_deletion
        mock_service.events.return_value.delete.return_value.execute.return_value = {}
        
        start_dt = datetime(2024, 1, 15, 9, 0)
        end_dt = datetime(2024, 1, 15, 17, 0)
        
        with patch('builtins.print'):
            result = delete_events(
                mock_service,
                title=None,
                start=start_dt,
                end=end_dt,
                scoped=None,
                forced=False
            )
            
            # Should delete all events in the time range
            assert result['deleted_count'] == 3
    
    def test_delete_events_bulk_protection(self, mock_service):
        """Test bulk deletion protection."""
        # Create many events to trigger bulk protection
        many_events = {
            'items': [{'id': f'event{i}', 'summary': f'Event {i}'} for i in range(15)]
        }
        mock_service.events.return_value.list.return_value.execute.return_value = many_events
        
        with patch('builtins.print') as mock_print:
            result = delete_events(
                mock_service,
                title=None,
                start="2024-01-15T00:00:00+00:00",
                end="2024-01-15T23:59:59+00:00",
                scoped=None,
                forced=False
            )
            
            assert result['status'] == 'too_many_matches'
            assert result['count'] == 15
            
            # Should not delete anything
            mock_service.events.return_value.delete.assert_not_called()
            mock_print.assert_called()
    
    def test_delete_events_force_bulk_deletion(self, mock_service):
        """Test forced bulk deletion bypasses protection."""
        many_events = {
            'items': [{'id': f'event{i}', 'summary': f'Event {i}'} for i in range(15)]
        }
        mock_service.events.return_value.list.return_value.execute.return_value = many_events
        mock_service.events.return_value.delete.return_value.execute.return_value = {}
        
        with patch('builtins.print'):
            result = delete_events(
                mock_service,
                title=None,
                start="2024-01-15T00:00:00+00:00",
                end="2024-01-15T23:59:59+00:00",
                scoped=None,
                forced=True  # Force deletion
            )
            
            assert result['status'] == 'deleted'
            assert result['deleted_count'] == 15
            assert mock_service.events.return_value.delete.call_count == 15
    
    def test_delete_events_scoped_all(self, mock_service):
        """Test deleting all events with scoped='all'."""
        many_events = {
            'items': [{'id': f'event{i}', 'summary': f'Event {i}'} for i in range(15)]
        }
        mock_service.events.return_value.list.return_value.execute.return_value = many_events
        mock_service.events.return_value.delete.return_value.execute.return_value = {}
        
        with patch('builtins.print'):
            result = delete_events(
                mock_service,
                title=None,
                start="2024-01-15T00:00:00+00:00",
                end="2024-01-15T23:59:59+00:00",
                scoped="all",  # Delete all
                forced=False
            )
            
            assert result['status'] == 'deleted'
            assert result['deleted_count'] == 15
    
    def test_delete_events_no_matches(self, mock_service):
        """Test deleting events when no matches are found."""
        mock_service.events.return_value.list.return_value.execute.return_value = {'items': []}
        
        with patch('builtins.print') as mock_print:
            result = delete_events(
                mock_service,
                title="Non-existent Event",
                start="2024-01-15T00:00:00+00:00",
                end="2024-01-15T23:59:59+00:00",
                scoped=None,
                forced=False
            )
            
            # Should not delete anything
            mock_service.events.return_value.delete.assert_not_called()
            # The function doesn't return anything when no matches, but also doesn't print
    
    def test_delete_events_custom_calendar_id(self, mock_service, sample_events_for_deletion):
        """Test deleting events from custom calendar."""
        mock_service.events.return_value.list.return_value.execute.return_value = sample_events_for_deletion
        mock_service.events.return_value.delete.return_value.execute.return_value = {}
        
        with patch('builtins.print'):
            delete_events(
                mock_service,
                title="Meeting",
                start="2024-01-15T00:00:00+00:00",
                end="2024-01-15T23:59:59+00:00",
                scoped=None,
                forced=False,
                calendar_id='custom_calendar_id'
            )
            
            # Verify list was called with custom calendar ID
            list_call = mock_service.events.return_value.list
            assert list_call.call_args[1]['calendarId'] == 'custom_calendar_id'
            
            # Verify delete was called with custom calendar ID
            delete_call = mock_service.events.return_value.delete
            assert all(call[1]['calendarId'] == 'custom_calendar_id' 
                      for call in delete_call.call_args_list)
    
    def test_delete_events_default_time_window(self, mock_service, sample_events_for_deletion):
        """Test deleting events with default time window when no bounds provided."""
        mock_service.events.return_value.list.return_value.execute.return_value = sample_events_for_deletion
        mock_service.events.return_value.delete.return_value.execute.return_value = {}
        
        with patch('builtins.print'):
            delete_events(
                mock_service,
                title="Meeting",
                start=None,  # No start time
                end=None,    # No end time
                scoped=None,
                forced=False
            )
            
            # Should use default time window
            list_call = mock_service.events.return_value.list
            assert 'timeMin' in list_call.call_args[1]
            assert 'timeMax' in list_call.call_args[1]
    
    def test_delete_events_api_error(self, mock_service):
        """Test delete_events handles API errors."""
        mock_service.events.return_value.list.return_value.execute.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            delete_events(
                mock_service,
                title="Test",
                start="2024-01-15T00:00:00+00:00",
                end="2024-01-15T23:59:59+00:00",
                scoped=None,
                forced=False
            )
