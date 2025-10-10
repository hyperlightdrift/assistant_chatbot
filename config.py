import os
from typing import Optional


class Config:
    """Configuration management for the assistant chatbot."""
    
    # Google Calendar API settings
    GOOGLE_CREDENTIALS_FILE = os.getenv(
        'GOOGLE_CREDENTIALS_FILE', 
        'internal/client_secret_923056037784-8o1j30uv5os6j6plbs0mitentaq6vkgh.apps.googleusercontent.com.json'
    )
    GOOGLE_TOKEN_FILE = os.getenv('GOOGLE_TOKEN_FILE', 'token.json')
    
    # Application settings
    DEFAULT_CALENDAR_ID = os.getenv('DEFAULT_CALENDAR_ID', 'primary')
    DEFAULT_TIMEZONE = os.getenv('DEFAULT_TIMEZONE', 'America/Denver')
    MAX_EVENTS_PER_REQUEST = int(os.getenv('MAX_EVENTS_PER_REQUEST', '50'))
    MAX_DELETE_THRESHOLD = int(os.getenv('MAX_DELETE_THRESHOLD', '10'))
    DEFAULT_WINDOW_DAYS = int(os.getenv('DEFAULT_WINDOW_DAYS', '365'))
    
    # API settings
    JOKE_API_URL = os.getenv('JOKE_API_URL', 'https://icanhazdadjoke.com/')
    
    @classmethod
    def get_credentials_path(cls) -> str:
        """Get the full path to the credentials file."""
        return os.path.join(os.getcwd(), cls.GOOGLE_CREDENTIALS_FILE)
    
    @classmethod
    def get_token_path(cls) -> str:
        """Get the full path to the token file."""
        return os.path.join(os.getcwd(), cls.GOOGLE_TOKEN_FILE)
