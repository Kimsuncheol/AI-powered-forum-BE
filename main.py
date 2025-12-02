from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware

from app.api import routes_auth, routes_user
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
api_router = APIRouter()
api_router.include_router(routes_auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(routes_user.router, prefix="/auth", tags=["users"]) # Keeping /auth prefix for /me to match old structure if desired, or move to /users

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": "Hello FastAPI"}