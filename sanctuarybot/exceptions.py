class DatabaseError(Exception):
    """Exception raised for database errors."""

    def __init__(self, message, command=None):
        self.message = message
        self.command = command


class ConfigError(Exception):
    """Exception raised for errors in configuration"""

    def __init__(self, message):
        self.message = message
