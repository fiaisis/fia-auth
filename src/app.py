"""
Module containing the fast api app. Uvicorn loads this to start the api
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from src.exception_handlers import auth_error_handler
from src.exceptions import AuthenticationError
from src.routers import ROUTER

app = FastAPI()
ALLOWED_ORIGINS = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ROUTER)

app.add_exception_handler(AuthenticationError, auth_error_handler)
