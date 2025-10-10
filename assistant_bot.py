import re
from cal import handle_calendar_command
import joke


def request_manager():
    """Main request handling loop with improved error handling."""
    print("🤖 Assistant Chatbot - Ready to help!")
    print("Commands: 'joke', 'calendar [action]', or 'quit' to exit\n")
    
    while True:
        try:
            request = input("What would you like me to do? ").strip()
            
            if not request:
                continue
                
            request_lower = request.lower()
            
            # Handle quit commands
            if any(word in request_lower for word in ['quit', 'exit', 'bye', 'goodbye']):
                print("👋 Goodbye!")
                break
            
            # Handle joke requests
            if re.search(r'\b(joke|funny|laugh)\b', request_lower):
                joke.tell_joke()
                continue
            
            # Handle calendar requests
            if re.search(r'\b(calendar|event|task|schedule|meeting|appointment)\b', request_lower):
                handle_calendar_command(request)
                continue
            
            # Handle unknown commands
            print("❓ I didn't understand that. Try:")
            print("  • 'tell me a joke'")
            print("  • 'calendar view events'")
            print("  • 'calendar create event called Meeting tomorrow at 2pm'")
            print("  • 'quit' to exit\n")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}\n")




if __name__ == "__main__":
    request_manager()
