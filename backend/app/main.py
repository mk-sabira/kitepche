from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, analyze, books, assistant
from app.core.database import Base, engine
from app.models.book import Book  # noqa: F401

# //getting books cover from FE

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#routes

app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(books.router)
app.include_router(assistant.router)

@app.get("/")
def read_root():
    return {"message": "Kyrgyz Readability Analyzer API is alive"}