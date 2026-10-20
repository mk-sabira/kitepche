from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, analyze, books, assistant, auth
from app.core.config import settings


# //getting books cover from FE

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Retry-After"],
)

#routes

app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(books.router)
app.include_router(assistant.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Kyrgyz Readability Analyzer API is alive"}