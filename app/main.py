# main.py
from contextlib import asynccontextmanager
import logging
import os
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from app.api.router import api_router
from app.core.database import database
from app.core.config import core_settings
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Database connection on startup
    await database.connect()
    yield
    # Cleanup on shutdown
    await database.close()


app = FastAPI(
    lifespan=lifespan,
    title="Sabzi app",
    description="Your API Description",
    version="1.0.0",
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # allows all methods
    allow_headers=["*"],  # allows all headers
)


# mounts static files
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

# configure logging (optional)
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


# handler for validation errors (HTTP 422)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # logger.error(f"Unexpected error: {exc}", exc_info=True)
    # print(request.headers)
    print(await request.body())
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": [{"field": error["loc"][-1], "message": error["msg"]} for error in exc.errors()],
        },
    )


# global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # rog the error
    # logger.error(f"Unexpected error: {exc}", exc_info=True)
    print("Error handler: ")
    print(exc)

    # return a generic error response
    return JSONResponse(
        status_code=500,
        content={"message": "An unexpected error occurred. Please try again later."},
    )


app.include_router(api_router, prefix="/api")


@app.get("/")
def hi():
    env = os.getenv("ENVIRONMENT", "default_environment")
    # dbpath = os.getenv("DATABASE_URL", "www")
    # print(env)
    # print(dbpath)
    print("AAAAA")

    return {"message": f"Hi there"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        debug=True,
        env_file=".env",
    )
