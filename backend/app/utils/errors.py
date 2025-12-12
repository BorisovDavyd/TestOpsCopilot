from fastapi import HTTPException, status


class LLMServiceError(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_502_BAD_GATEWAY):
        super().__init__(status_code=status_code, detail=detail)


class ValidationError(HTTPException):
    def __init__(self, detail: str, status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY):
        super().__init__(status_code=status_code, detail=detail)
