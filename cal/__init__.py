from auth.authentication import get_credentials
from . import events, tasks, parser
from datetime import datetime



def handle_calendar_command(user_input):
    parsed = parser.parse_input(user_input)
    service = get_credentials()

    if parsed['object'] == 'event' or parsed['object'] == 'events':
        if parsed['intention'] == 'create' or parsed['intention'] == 'schedule':
            return events.create_event(parsed['title'], parsed['start'], parsed['end'])
        elif parsed['intention'] == 'view':
            return events.view_events(service, parsed, )
        elif parsed['intention'] == 'delete' or parsed['intention'] == 'remove':
            pass

    elif parsed['object'] == 'task' or parsed['object'] == 'tasks':
        if parsed['intention'] == 'create' or parsed['intention'] == 'schedule':
            return tasks.create_task(parsed['title'], parsed['start'], parsed['date'])
        elif parsed['intention'] == 'view':
            pass
        elif parsed['intention'] == 'delete' or parsed['intention'] == 'remove':
            pass
    # if "event" in user_input:
    #     if "create" in user_input or "schedule" in user_input or "make" in user_input:
    #         return events.create_event(user_input)
    #     elif "view" in user_input:
    #         return events.view_events(user_input)
    #     elif "delete" in user_input or "remove" in user_input:
    #         return events.delete_events()
    #
    # elif "task" in user_input:
    #     if "create" in user_input:
    #         return tasks.create_task()
    #     elif "view" in user_input:
    #         return tasks.view_tasks()
    #     elif "delete" in user_input:
    #         return tasks.delete_tasks()
    #
    # elif "appointment" in user_input:
    #     if "create" in user_input:
    #         return appointments.create_appointment()
    #     elif "view" in user_input:
    #         return appointments.view_appointments()
    #     elif "delete" in user_input:
    #         return appointments.delete_appointments()



