from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from app.routers.colleges import router
import os

load_dotenv()

# ── App setup ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="CollegePath API",
    description="College recommendation engine for Jharkhand and West Bengal based on JEE / WBJEE ranks.",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Allows the React dev server (localhost:5173) to call this API.
# In production, replace with your actual deployed frontend URL.

origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────

app.include_router(router)

# ── Root ──────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "message": "Welcome to CollegePath API",
        "docs": "/docs",
        "health": "/api/health",
    }