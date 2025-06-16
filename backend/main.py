from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import analyst

app = FastAPI(
    title="PatentAI Analyst API",
    version="3.0.0-FINAL",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# --- THE DEFINITIVE CORS FIX ---
# This middleware is added to the main 'app' object.
# It applies to ALL routes that are included in the app,
# including everything inside the 'analyst' router.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # The origin of your React frontend
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (POST, GET, etc.)
    allow_headers=["*"],  # Allow all headers
)
# -----------------------------

# All endpoints from 'analyst.py' are now covered by the middleware above.
app.include_router(analyst.router, prefix="/api")

@app.get("/", tags=["Root"], include_in_schema=False)
def read_root():
    return {"message": "PatentAI Analyst API is running and CORS is correctly configured."}