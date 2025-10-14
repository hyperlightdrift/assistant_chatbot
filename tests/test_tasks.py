"""Comprehensive pytest tests for Google Tasks functionality."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, date, timedelta
import sys
import os

# Add parent directory to path to import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cal.tasks import create_task, view_tasks, delete_tasks
from exceptions import AssistantError


class TestCreateTask:
    """Test the create_task function."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock Google Tasks service."""
        service = Mock()
        
        # Mock tasklists().list()
        service.tasklists.return_value.list.return_value.execute.return_value = {
            'items': [{'id': 'default_tasklist_id', 'title': 'Default List'}]
        }
        
        # Mock tasks().insert()
        service.tasks.return_value.insert.return_value.execute.return_value = {
            'id': 'test_task_id',
            'title': 'Test Task',
            'status': 'needsAction'
        }
        
        return service
    
    def test_create_task_basic(self, mock_service):
        """Test creating a basic task without due date."""
        with patch('builtins.print') as mock_print:
            result = create_task(mock_service, "Test Task")
            
            # Verify the task was created correctly
            assert result['id'] == 'test_task_id'
            assert result['title'] == 'Test Task'
            assert result['status'] == 'needsAction'
            
            # Verify service calls
            mock_service.tasklists.assert_called_once()
            mock_service.tasks.assert_called_once()
            
            # Check the task body sent to API
            insert_call = mock_service.tasks.return_value.insert
            task_body = insert_call.call_args[1]['body']
            assert task_body['title'] == 'Test Task'
            assert task_body['status'] == 'needsAction'
            assert 'due' not in task_body
            
            # Verify print was called
            mock_print.assert_called_with("Task created: Test Task")
    
    def test_create_task_with_due_date(self, mock_service):
        """Test creating a task with due date."""
        due_date = datetime(2024, 1, 15, 10, 30)
        
        with patch('builtins.print') as mock_print:
            result = create_task(mock_service, "Task with Due Date", date=due_date)
            
            # Check the task body includes due date
            insert_call = mock_service.tasks.return_value.insert
            task_body = insert_call.call_args[1]['body']
            
            assert task_body['title'] == 'Task with Due Date'
            assert task_body['due'] == '2024-01-15T10:30:00Z'
    
    def test_create_task_with_timezone_aware_due_date(self, mock_service):
        """Test creating a task with timezone-aware due date."""
        # Create timezone-aware datetime
        due_date = datetime(2024, 1, 15, 10, 30, tzinfo=datetime.now().astimezone().tzinfo)
        
        with patch('builtins.print') as mock_print:
            result = create_task(mock_service, "Task with TZ Due Date", date=due_date)
            
            insert_call = mock_service.tasks.return_value.insert
            task_body = insert_call.call_args[1]['body']
            
            # Should use the timezone-aware datetime as-is
            expected_due = due_date.isoformat()
            assert task_body['due'] == expected_due
    
    def test_create_task_no_task_lists(self, mock_service):
        """Test create_task when no task lists exist."""
        # Mock empty task lists response
        mock_service.tasklists.return_value.list.return_value.execute.return_value = {'items': []}
        
        with pytest.raises(AssistantError, match="No task lists found"):
            create_task(mock_service, "Test Task")
    
    def test_create_task_api_error_during_list(self, mock_service):
        """Test create_task when tasklists().list() fails."""
        mock_service.tasklists.return_value.list.return_value.execute.side_effect = Exception("API Error")
        
        with pytest.raises(AssistantError, match="Failed to create task: API Error"):
            create_task(mock_service, "Test Task")
    
    def test_create_task_api_error_during_insert(self, mock_service):
        """Test create_task when tasks().insert() fails."""
        mock_service.tasks.return_value.insert.return_value.execute.side_effect = Exception("Insert Error")
        
        with pytest.raises(AssistantError, match="Failed to create task: Insert Error"):
            create_task(mock_service, "Test Task")
    
    def test_create_task_empty_title(self, mock_service):
        """Test creating a task with empty title."""
        with patch('builtins.print') as mock_print:
            result = create_task(mock_service, "")
            
            insert_call = mock_service.tasks.return_value.insert
            task_body = insert_call.call_args[1]['body']
            assert task_body['title'] == ""
    
    def test_create_task_uses_first_tasklist(self, mock_service):
        """Test that create_task uses the first available task list."""
        # Mock multiple task lists
        mock_service.tasklists.return_value.list.return_value.execute.return_value = {
            'items': [
                {'id': 'first_list', 'title': 'First List'},
                {'id': 'second_list', 'title': 'Second List'}
            ]
        }
        
        with patch('builtins.print'):
            create_task(mock_service, "Test Task")
            
            # Should use the first task list
            insert_call = mock_service.tasks.return_value.insert
            assert insert_call.call_args[1]['tasklist'] == 'first_list'


class TestViewTasks:
    """Test the view_tasks function."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock Google Tasks service."""
        service = Mock()
        
        # Mock tasklists().list()
        service.tasklists.return_value.list.return_value.execute.return_value = {
            'items': [{'id': 'default_tasklist_id', 'title': 'Default List'}]
        }
        
        return service
    
    @pytest.fixture
    def sample_tasks_response(self):
        """Sample tasks response from Google Tasks API."""
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
    
    def test_view_tasks_no_filter(self, mock_service, sample_tasks_response):
        """Test viewing all tasks without any filter."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_response
        
        with patch('builtins.print') as mock_print:
            view_tasks(mock_service)
            
            # Should print all tasks
            assert mock_print.call_count == 4  # Header + 3 tasks
            mock_print.assert_any_call("\nFound 3 task(s):")
            mock_print.assert_any_call("• Meeting preparation (Due: 2024-01-15T00:00:00Z, Status: needsAction)")
            mock_print.assert_any_call("• Buy groceries (Due: 2024-01-16T00:00:00Z, Status: completed)")
            mock_print.assert_any_call("• Project meeting (Due: No due date, Status: needsAction)")
    
    def test_view_tasks_filter_by_title(self, mock_service, sample_tasks_response):
        """Test viewing tasks filtered by title."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_response
        
        with patch('builtins.print') as mock_print:
            view_tasks(mock_service, title="meeting")
            
            # Should only show tasks with "meeting" in title (case insensitive)
            assert mock_print.call_count == 3  # Header + 2 matching tasks
            mock_print.assert_any_call("\nFound 2 task(s):")
            mock_print.assert_any_call("• Meeting preparation (Due: 2024-01-15T00:00:00Z, Status: needsAction)")
            mock_print.assert_any_call("• Project meeting (Due: No due date, Status: needsAction)")
    
    def test_view_tasks_filter_by_date(self, mock_service, sample_tasks_response):
        """Test viewing tasks filtered by date."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_response
        
        filter_date = datetime(2024, 1, 15)
        
        with patch('builtins.print') as mock_print:
            view_tasks(mock_service, date=filter_date)
            
            # Should only show tasks due on 2024-01-15
            assert mock_print.call_count == 2  # Header + 1 matching task
            mock_print.assert_any_call("\nFound 1 task(s):")
            mock_print.assert_any_call("• Meeting preparation (Due: 2024-01-15T00:00:00Z, Status: needsAction)")
    
    def test_view_tasks_filter_by_title_and_date(self, mock_service, sample_tasks_response):
        """Test viewing tasks filtered by both title and date."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_response
        
        filter_date = datetime(2024, 1, 15)
        
        with patch('builtins.print') as mock_print:
            view_tasks(mock_service, title="meeting", date=filter_date)
            
            # Should show tasks with "meeting" in title AND due on 2024-01-15
            assert mock_print.call_count == 2  # Header + 1 matching task
            mock_print.assert_any_call("\nFound 1 task(s):")
            mock_print.assert_any_call("• Meeting preparation (Due: 2024-01-15T00:00:00Z, Status: needsAction)")
    
    def test_view_tasks_no_matches(self, mock_service, sample_tasks_response):
        """Test viewing tasks when no matches are found."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_response
        
        with patch('builtins.print') as mock_print:
            view_tasks(mock_service, title="nonexistent")
            
            # Should print no matches message
            mock_print.assert_called_once_with("No matching tasks found.")
    
    def test_view_tasks_no_tasks_exist(self, mock_service):
        """Test viewing tasks when no tasks exist."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = {'items': []}
        
        with patch('builtins.print') as mock_print:
            view_tasks(mock_service)
            
            mock_print.assert_called_once_with("No tasks found.")
    
    def test_view_tasks_no_task_lists(self, mock_service):
        """Test view_tasks when no task lists exist."""
        mock_service.tasklists.return_value.list.return_value.execute.return_value = {'items': []}
        
        with pytest.raises(AssistantError, match="No task lists found"):
            view_tasks(mock_service)
    
    def test_view_tasks_api_error(self, mock_service):
        """Test view_tasks when API call fails."""
        mock_service.tasklists.return_value.list.return_value.execute.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            view_tasks(mock_service)
    
    def test_view_tasks_handles_missing_fields(self, mock_service):
        """Test view_tasks handles tasks with missing fields gracefully."""
        tasks_with_missing_fields = {
            'items': [
                {
                    'id': 'task1',
                    'title': 'Complete Task',
                    'status': 'needsAction',
                    'due': '2024-01-15T00:00:00Z'
                },
                {
                    'id': 'task2',
                    # Missing title
                    'status': 'completed'
                },
                {
                    'id': 'task3',
                    'title': 'Another Task'
                    # Missing status and due
                }
            ]
        }
        mock_service.tasks.return_value.list.return_value.execute.return_value = tasks_with_missing_fields
        
        with patch('builtins.print') as mock_print:
            view_tasks(mock_service)
            
            assert mock_print.call_count == 4  # Header + 3 tasks
            mock_print.assert_any_call("• Complete Task (Due: 2024-01-15T00:00:00Z, Status: needsAction)")
            mock_print.assert_any_call("• Untitled (Due: No due date, Status: completed)")
            mock_print.assert_any_call("• Another Task (Due: No due date, Status: unknown)")


class TestDeleteTasks:
    """Test the delete_tasks function."""
    
    @pytest.fixture
    def mock_service(self):
        """Create a mock Google Tasks service."""
        service = Mock()
        
        # Mock tasklists().list()
        service.tasklists.return_value.list.return_value.execute.return_value = {
            'items': [{'id': 'default_tasklist_id', 'title': 'Default List'}]
        }
        
        return service
    
    @pytest.fixture
    def sample_tasks_for_deletion(self):
        """Sample tasks that can be deleted."""
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
                },
                {
                    'id': 'task4',
                    'title': 'Different task',
                    'status': 'needsAction',
                    'due': '2024-01-20T00:00:00Z'
                }
            ]
        }
    
    def test_delete_tasks_by_title(self, mock_service, sample_tasks_for_deletion):
        """Test deleting tasks by title."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_for_deletion
        mock_service.tasks.return_value.delete.return_value.execute.return_value = {}
        
        with patch('builtins.print') as mock_print:
            delete_tasks(mock_service, title="meeting")
            
            # Should delete 2 tasks with "meeting" in title
            assert mock_service.tasks.return_value.delete.call_count == 2
            
            # Verify correct tasks were deleted
            delete_calls = mock_service.tasks.return_value.delete.call_args_list
            deleted_ids = [call[1]['task'] for call in delete_calls]
            assert 'task1' in deleted_ids  # Meeting preparation
            assert 'task3' in deleted_ids  # Project meeting
            
            mock_print.assert_called_with("Deleted 2 task(s).")
    
    def test_delete_tasks_by_date(self, mock_service, sample_tasks_for_deletion):
        """Test deleting tasks by date."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_for_deletion
        mock_service.tasks.return_value.delete.return_value.execute.return_value = {}
        
        filter_date = datetime(2024, 1, 15)
        
        with patch('builtins.print') as mock_print:
            delete_tasks(mock_service, date=filter_date)
            
            # Should delete 1 task due on 2024-01-15
            assert mock_service.tasks.return_value.delete.call_count == 1
            
            delete_call = mock_service.tasks.return_value.delete.call_args
            assert delete_call[1]['task'] == 'task1'
            
            mock_print.assert_called_with("Deleted 1 task(s).")
    
    def test_delete_tasks_by_title_and_date(self, mock_service, sample_tasks_for_deletion):
        """Test deleting tasks by both title and date."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_for_deletion
        mock_service.tasks.return_value.delete.return_value.execute.return_value = {}
        
        filter_date = datetime(2024, 1, 15)
        
        with patch('builtins.print') as mock_print:
            delete_tasks(mock_service, title="meeting", date=filter_date)
            
            # Should delete 1 task: "Meeting preparation" due on 2024-01-15
            assert mock_service.tasks.return_value.delete.call_count == 1
            
            delete_call = mock_service.tasks.return_value.delete.call_args
            assert delete_call[1]['task'] == 'task1'
            
            mock_print.assert_called_with("Deleted 1 task(s).")
    
    def test_delete_tasks_no_filter(self, mock_service, sample_tasks_for_deletion):
        """Test deleting all tasks when no filter is provided."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_for_deletion
        mock_service.tasks.return_value.delete.return_value.execute.return_value = {}
        
        with patch('builtins.print') as mock_print:
            delete_tasks(mock_service)
            
            # Should delete all tasks
            assert mock_service.tasks.return_value.delete.call_count == 4
            
            mock_print.assert_called_with("Deleted 4 task(s).")
    
    def test_delete_tasks_no_matches(self, mock_service, sample_tasks_for_deletion):
        """Test deleting tasks when no matches are found."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_for_deletion
        mock_service.tasks.return_value.delete.return_value.execute.return_value = {}
        
        with patch('builtins.print') as mock_print:
            delete_tasks(mock_service, title="nonexistent")
            
            # Should not delete anything
            mock_service.tasks.return_value.delete.assert_not_called()
            mock_print.assert_called_with("No matching tasks found.")
    
    def test_delete_tasks_no_tasks_exist(self, mock_service):
        """Test deleting tasks when no tasks exist."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = {'items': []}
        
        with patch('builtins.print') as mock_print:
            delete_tasks(mock_service)
            
            mock_service.tasks.return_value.delete.assert_not_called()
            mock_print.assert_called_with("No tasks found.")
    
    def test_delete_tasks_no_task_lists(self, mock_service):
        """Test delete_tasks when no task lists exist."""
        mock_service.tasklists.return_value.list.return_value.execute.return_value = {'items': []}
        
        with pytest.raises(AssistantError, match="No task lists found"):
            delete_tasks(mock_service)
    
    def test_delete_tasks_api_error_during_list(self, mock_service):
        """Test delete_tasks when tasklists().list() fails."""
        mock_service.tasklists.return_value.list.return_value.execute.side_effect = Exception("API Error")
        
        with pytest.raises(Exception, match="API Error"):
            delete_tasks(mock_service)
    
    def test_delete_tasks_api_error_during_tasks_list(self, mock_service):
        """Test delete_tasks when tasks().list() fails."""
        mock_service.tasks.return_value.list.return_value.execute.side_effect = Exception("Tasks API Error")
        
        with pytest.raises(Exception, match="Tasks API Error"):
            delete_tasks(mock_service)
    
    def test_delete_tasks_api_error_during_delete(self, mock_service, sample_tasks_for_deletion):
        """Test delete_tasks when tasks().delete() fails."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_for_deletion
        mock_service.tasks.return_value.delete.return_value.execute.side_effect = Exception("Delete Error")
        
        with pytest.raises(Exception, match="Delete Error"):
            delete_tasks(mock_service, title="meeting")
    
    def test_delete_tasks_case_insensitive_title(self, mock_service, sample_tasks_for_deletion):
        """Test that task deletion is case insensitive."""
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_for_deletion
        mock_service.tasks.return_value.delete.return_value.execute.return_value = {}
        
        with patch('builtins.print') as mock_print:
            delete_tasks(mock_service, title="MEETING")
            
            # Should still match "meeting" tasks (case insensitive)
            assert mock_service.tasks.return_value.delete.call_count == 2
            mock_print.assert_called_with("Deleted 2 task(s).")
    
    def test_delete_tasks_handles_missing_due_dates(self, mock_service):
        """Test delete_tasks handles tasks with missing due dates."""
        tasks_with_missing_due = {
            'items': [
                {
                    'id': 'task1',
                    'title': 'Task with due date',
                    'due': '2024-01-15T00:00:00Z'
                },
                {
                    'id': 'task2',
                    'title': 'Task without due date'
                    # No due field
                }
            ]
        }
        mock_service.tasks.return_value.list.return_value.execute.return_value = tasks_with_missing_due
        mock_service.tasks.return_value.delete.return_value.execute.return_value = {}
        
        filter_date = datetime(2024, 1, 15)
        
        with patch('builtins.print') as mock_print:
            delete_tasks(mock_service, date=filter_date)
            
            # Should only delete task with due date matching the filter
            assert mock_service.tasks.return_value.delete.call_count == 1
            
            delete_call = mock_service.tasks.return_value.delete.call_args
            assert delete_call[1]['task'] == 'task1'
            
            mock_print.assert_called_with("Deleted 1 task(s).")
    
    def test_delete_tasks_uses_first_tasklist(self, mock_service, sample_tasks_for_deletion):
        """Test that delete_tasks uses the first available task list."""
        # Mock multiple task lists
        mock_service.tasklists.return_value.list.return_value.execute.return_value = {
            'items': [
                {'id': 'first_list', 'title': 'First List'},
                {'id': 'second_list', 'title': 'Second List'}
            ]
        }
        mock_service.tasks.return_value.list.return_value.execute.return_value = sample_tasks_for_deletion
        mock_service.tasks.return_value.delete.return_value.execute.return_value = {}
        
        with patch('builtins.print'):
            delete_tasks(mock_service, title="meeting")
            
            # Should use the first task list for all operations
            list_call = mock_service.tasks.return_value.list
            assert list_call.call_args[1]['tasklist'] == 'first_list'
            
            delete_calls = mock_service.tasks.return_value.delete.call_args_list
            assert all(call[1]['tasklist'] == 'first_list' for call in delete_calls)
