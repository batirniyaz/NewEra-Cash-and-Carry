from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.auth.superuser import create_superuser
from app.database import create_tables
from app import router



@asynccontextmanager
async def lifespan(main_app: FastAPI):
    await create_tables()
    await create_superuser()

    try:
        yield
    finally:
        pass


app = FastAPI(
    title="Assignment API Implementation",
    version="0.1",
    summary="This is an API implementation for an assignment from programming subject",
    lifespan=lifespan,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(router)

