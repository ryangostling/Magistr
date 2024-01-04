class HTTPException(Exception):
    pass

class BadRequest(HTTPException):
    pass

class Unauthorized(HTTPException):
    pass

class Forbidden(HTTPException):
    pass

class TooManyRequests(HTTPException):
    pass

class ServiceUnavailable(HTTPException):
    pass

