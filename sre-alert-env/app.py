from fastapi import FastAPI

app = FastAPI(title="Cloud Infrastructure Alert Manager")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "status": "Cloud Alert Manager Env is running",
        "version": "1.0.0",
    }
