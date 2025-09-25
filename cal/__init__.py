from auth.authentication import get_credentials
from . import events, tasks, parser
from datetime import datetime



def handle_calendar_command(user_input):
    parsed = parser.parse_input(user_input)
    service = get_credentials()

    if parsed['object'] == 'event' or parsed['object'] == 'events':
        if parsed['intention'] == 'create' or parsed['intention'] == 'schedule':
            return events.create_event(service, parsed['title'], parsed['start'], parsed['end'])
        elif parsed['intention'] == 'view':
            return events.view_events(service, parsed, )
        elif parsed['intention'] == 'delete' or parsed['intention'] == 'remove':
            return events.delete_events(service, parsed['title'], parsed['start'], parsed['end'],
                                        parsed['scope'], parsed['forced'])

    elif parsed['object'] == 'task' or parsed['object'] == 'tasks':
        if parsed['intention'] == 'create' or parsed['intention'] == 'schedule':
            return tasks.create_task(parsed['title'], parsed['start'], parsed['date'])
        elif parsed['intention'] == 'view':
            pass
        elif parsed['intention'] == 'delete' or parsed['intention'] == 'remove':
            pass
