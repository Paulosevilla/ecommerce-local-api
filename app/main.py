
from fastapi import FastAPI
from app.modules.users_module import router as users_router
from app.modules.products_module import router as products_router

app = FastAPI(title="E-commerce Local API", version="0.1.0")

@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}

app.include_router(users_router, prefix="/users", tags=["users"])
app.include_router(products_router, prefix="/products", tags=["products"])
