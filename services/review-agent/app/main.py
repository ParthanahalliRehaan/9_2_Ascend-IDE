from fastapi import FastAPI

app = FastAPI(title="review-agent")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "review-agent"}