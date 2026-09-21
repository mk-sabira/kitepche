from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import health, analyze, books

# //getting books cover from FE

app = FastAPI()

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


# it gets the covers
# app.mount("/books", StaticFiles(directory="../frontend/public/books"), name="books")

#routes

app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(books.router)

@app.get("/")
def read_root():
    return {"message": "Kyrgyz Readability Analyzer API is alive"}