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



# commands = {
#     "joke": tell_joke,
#     "weather": get_weather,
#     "time": get_time,
# }
#
# user_input = input("What can I help with? ").lower()
#
# for keyword, action in commands.items():
#     if keyword in user_input:
#         action()
#         break
# else:
#     print("Sorry, I didn't understand that.")



if __name__ == "__main__":
    request_manager()
