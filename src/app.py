"""
Module containing the fast api app. Uvicorn loads this to start the api
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

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
