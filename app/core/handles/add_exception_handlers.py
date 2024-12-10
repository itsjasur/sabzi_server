# # app/core/handlers.py
# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse

# from app.core.exceptions import CustomException


# def add_exception_handlers(app: FastAPI) -> None:
#     @app.exception_handler(CustomException)
#     async def custom_exception_handler(request: Request, exc: CustomException):
#         return JSONResponse(
#             status_code=exc.status_code,
#             content={
#                 "success": False,
#                 "message": exc.detail,
#                 "error_code": exc.error_code,
#                 "extra": exc.extra,
#                 "path": request.url.path,
#             },
#         )
