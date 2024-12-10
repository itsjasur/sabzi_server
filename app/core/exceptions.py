# # app/core/exceptions.py
# from fastapi import HTTPException, status


# class CustomException(HTTPException):
#     def __init__(
#         self,
#         status_code: int,
#         message: str,
#         error_code: str = None,
#         extra: dict = None,
#     ):
#         super().__init__(status_code=status_code, detail=message)
#         self.error_code = error_code
#         self.extra = extra


# # Common exceptions you might use
# class NotFoundException(CustomException):
#     def __init__(self, message: str, error_code: str = "NOT_FOUND", extra: dict = None):
#         super().__init__(
#             status_code=status.HTTP_404_NOT_FOUND,
#             message=message,
#             error_code=error_code,
#             extra=extra,
#         )


# class ConflictException(CustomException):
#     def __init__(self, message: str, error_code: str = "CONFLICT", extra: dict = None):
#         super().__init__(
#             status_code=status.HTTP_409_CONFLICT,
#             message=message,
#             error_code=error_code,
#             extra=extra,
#         )
