from fastapi import FastAPI

from app.api.changes import router as changes_router
from app.api.outcomes import router as outcomes_router


app = FastAPI(
    title="SEO Daily Counter-Strategy System",
    description="Deterministic SEO observation, diagnosis, action, and outcome system",
    version="1.0.0",
)

app.include_router(changes_router)
app.include_router(outcomes_router)


@app.get("/health")
def health():
    return {"status": "healthy"}