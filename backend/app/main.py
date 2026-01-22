from fastapi import FastAPI

app = FastAPI(
    title="Library Management System",
    description="MVP API for managing books, users, and borrow logs",
    version="0.1.0",
)


@app.get("/")
async def root():
    return {"message": "Library Management System API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
