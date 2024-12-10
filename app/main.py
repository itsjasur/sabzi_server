# main.py

import json
import os
from typing import Any, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn
from app.api.router import api_router
from app.core.config import core_settings


# is_prod = any("run" in arg.lower() for arg in sys.argv)
# current_env = ".env.staging" if is_prod else ".env"
# load_dotenv(current_env)


app = FastAPI(
    title=core_settings.app_name,
    description="Your API Description",
    version="1.0.0",
)


# Handle generic exceptions
@app.exception_handler(HTTPException)
async def general_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": str(exc.detail),
        },
    )


class StandardResponse(BaseModel):
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None


@app.middleware("http")
async def format_response(request: Request, call_next):
    # Call the next middleware/route handler
    response = await call_next(request)

    # If response is already JSONResponse, get the body
    if isinstance(response, JSONResponse):
        response_body = response.body.decode()
        import json

        response_data = json.loads(response_body)

        # If response is already formatted, return as is
        if isinstance(response_data, dict) and "success" in response_data:
            return response

        # Format the response
        formatted_response = {
            "success": 200 <= response.status_code < 300,
            "data": response_data,
            "error": None if 200 <= response.status_code < 300 else "Request failed",
        }

        return JSONResponse(content=formatted_response, status_code=response.status_code, headers=dict(response.headers))

    return response


app.include_router(api_router, prefix="/api")


@app.get("/")
def hi():
    env = os.getenv("ENVIRONMENT", "default_environment")
    print(f"{core_settings.app_name} runing")
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
