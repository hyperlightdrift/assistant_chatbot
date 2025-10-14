from auth.authentication import get_calendar_service, get_tasks_service
from . import events, tasks, parser
from datetime import datetime



def handle_calendar_command(user_input):
    parsed = parser.parse_input(user_input)

    if parsed['object'] == 'event' or parsed['object'] == 'events':
        service = get_calendar_service()
        if parsed['intention'] == 'create' or parsed['intention'] == 'schedule':
            return events.create_event(service, parsed['title'], parsed['start'], parsed['end'])
        elif parsed['intention'] == 'view':
            return events.view_events(service, parsed)
        elif parsed['intention'] == 'delete' or parsed['intention'] == 'remove':
            return events.delete_events(service, parsed['title'], parsed['start'], parsed['end'],
                                        parsed['scope'], parsed['force'])

    elif parsed['object'] == 'task' or parsed['object'] == 'tasks':
        tasks_service = get_tasks_service()
        if parsed['intention'] == 'create' or parsed['intention'] == 'schedule':
            return tasks.create_task(tasks_service, parsed['title'], parsed['date'])
        elif parsed['intention'] == 'view':
            return tasks.view_tasks(tasks_service, parsed['title'], parsed['date'])
        elif parsed['intention'] == 'delete' or parsed['intention'] == 'remove':
            return tasks.delete_tasks(tasks_service, parsed['title'], parsed['date'])
