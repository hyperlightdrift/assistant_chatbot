"""Task management functionality for Google Tasks API."""

from datetime import datetime
from . import datetime_utils
from exceptions import AssistantError
# from ..exceptions import AssistantError


def create_task(service, title: str, start: str = None, date: datetime = None):
    """
    Create a task in Google Tasks.
    
    Args:
        service: Google Tasks API service
        title: Task title
        start: Start time (ISO string)
        date: Due date (datetime object)
    """
    try:
        task_body = {
            'title': title,
            'status': 'needsAction'
        }
        
        if date:
            # Convert datetime to RFC3339 string for Tasks API
            due_date = date.isoformat() + 'Z' if not date.tzinfo else date.isoformat()
            task_body['due'] = due_date
        
        # Get the default task list
        tasklists = service.tasklists().list().execute()
        tasklist_items = tasklists.get('items', [])
        
        if not tasklist_items:
            raise AssistantError("No task lists found. Please create a task list in Google Tasks first.")
        
        tasklist_id = tasklist_items[0]['id']
        
        created_task = service.tasks().insert(
            tasklist=tasklist_id, 
            body=task_body
        ).execute()
        
        print(f"Task created: {created_task.get('title')}")
        return created_task
        
    except Exception as e:
        raise AssistantError(f"Failed to create task: {str(e)}")


def delete_tasks(service, title: str = None, date: datetime = None):
    """
    Delete tasks matching criteria.
    
    Args:
        service: Google Tasks API service
        title: Task title to match (optional)
        date: Date to filter by (optional)
    """
    try:
        # Get the default task list
        tasklists = service.tasklists().list().execute()
        tasklist_items = tasklists.get('items', [])
        
        if not tasklist_items:
            raise AssistantError("No task lists found. Please create a task list in Google Tasks first.")
        
        tasklist_id = tasklist_items[0]['id']
        
        # List tasks
        tasks = service.tasks().list(tasklist=tasklist_id).execute()
        task_items = tasks.get('items', [])
        
        if not task_items:
            print("No tasks found.")
            return
        
        # Filter tasks
        tasks_to_delete = []
        for task in task_items:
            if title and title.lower() not in task.get('title', '').lower():
                continue
            if date:
                task_due = task.get('due')
                if not task_due:
                    continue
                # Compare dates (simplified)
                if not task_due.startswith(date.strftime('%Y-%m-%d')):
                    continue
            tasks_to_delete.append(task)
        
        if not tasks_to_delete:
            print("No matching tasks found.")
            return
        
        # Delete tasks
        deleted_count = 0
        for task in tasks_to_delete:
            service.tasks().delete(tasklist=tasklist_id, task=task['id']).execute()
            deleted_count += 1
        
        print(f"Deleted {deleted_count} task(s).")
        
    except Exception as e:
        raise AssistantError(f"Failed to delete tasks: {str(e)}")


def view_tasks(service, title: str = None, date: datetime = None):
    """
    View tasks matching criteria.
    
    Args:
        service: Google Tasks API service
        title: Task title to filter by (optional)
        date: Date to filter by (optional)
    """
    try:
        # Get the default task list
        tasklists = service.tasklists().list().execute()
        tasklist_items = tasklists.get('items', [])
        
        if not tasklist_items:
            raise AssistantError("No task lists found. Please create a task list in Google Tasks first.")
        
        tasklist_id = tasklist_items[0]['id']
        
        # List tasks
        tasks = service.tasks().list(tasklist=tasklist_id).execute()
        task_items = tasks.get('items', [])
        
        if not task_items:
            print("No tasks found.")
            return
        
        # Filter and display tasks
        matching_tasks = []
        for task in task_items:
            if title and title.lower() not in task.get('title', '').lower():
                continue
            if date:
                task_due = task.get('due')
                if not task_due:
                    continue
                if not task_due.startswith(date.strftime('%Y-%m-%d')):
                    continue
            matching_tasks.append(task)
        
        if not matching_tasks:
            print("No matching tasks found.")
            return
        
        print(f"\nFound {len(matching_tasks)} task(s):")
        for task in matching_tasks:
            title_str = task.get('title', 'Untitled')
            due_str = task.get('due', 'No due date')
            status_str = task.get('status', 'unknown')
            print(f"• {title_str} (Due: {due_str}, Status: {status_str})")
        
    except Exception as e:
        raise AssistantError(f"Failed to view tasks: {str(e)}")