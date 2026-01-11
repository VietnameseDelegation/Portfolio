from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add parent directory to path so we can import from dao, models, etc.
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.routes import users, products, orders, etl

app = FastAPI(title="OrderSystem API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React Dev Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(etl.router, prefix="/api/etl", tags=["ETL"])

@app.get("/")
def read_root():
    return {"message": "OrderSystem API is running"}
