class AppException(Exception):
    """Base exception for the application"""
    pass

class ConfigurationError(AppException):
    """Raised when there is a configuration issue"""
    pass

class DatabaseError(AppException):
    """Raised when a database operation fails"""
    pass

class ValidationError(AppException):
    """Raised when input validation fails"""
    pass

class ResourceNotFoundError(AppException):
    """Raised when a requested resource is not found"""
    pass
