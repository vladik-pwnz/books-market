from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.configurations.database import global_init
from src.routers import v1_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Running global_init() at startup...")
    global_init()
    yield
    print("🛑 FastAPI is shutting down...")

app = FastAPI(
    title="Book Library App",
    description="Учебное приложение для MTS Shad",
    version="0.0.1",
    default_response_class=ORJSONResponse,
    responses={404: {"description": "Not found!"}},
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    lifespan=lifespan
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
    return {"message": "Book Library API is running. Visit http://localhost:8000/api/v1/redoc for documentation"}

app.include_router(v1_router)
