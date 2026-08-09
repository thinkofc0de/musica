
from fastapi import FastAPI

app = FastAPI(
    title="Music Agent",
    description="LangGraph-based personalized music assistant",
    version="0.1.0"
)


@app.get("/")
def root():
    return {
        "status": "online",
        "message": "Music Agent is running"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
