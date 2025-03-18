from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.configurations.database import create_db_and_tables, global_init
from src.routers import v1_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    global_init()
    # Run Alembic migrations (this replaces direct table creation)
    await create_db_and_tables()
    yield


app = FastAPI(
    title="Book Library App",
    description="Учебное приложение для MTS Shad",
    version="0.0.1",
    default_response_class=ORJSONResponse,
    responses={404: {"description": "Not found!"}},
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.get("/")
async def root():
    return {"message": "Book Library API is running. Visit /api/v1/docs or /api/v1/redoc for documentation"}


@app.get("/ping")
async def ping():
    return {"ping": "pong"}

app.include_router(v1_router)
