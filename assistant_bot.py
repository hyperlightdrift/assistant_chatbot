import re
from cal import handle_calendar_command
import joke


def request_manager():
    while True:
        request = input("What would you like me to do? ").lower()

        if re.search("joke", request):
            joke.tell_joke()

        if re.search("calendar", request):
            handle_calendar_command(request)

        else:
            break




if __name__ == "__main__":
    request_manager()
