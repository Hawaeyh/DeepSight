from fastapi import FastAPI

app = FastAPI(
    title="ML7-VIDS DeepSight API",
    version="1.0.0",
)

@app.get("/")
def root():
    return {
        "project": "ML7-VIDS DeepSight System",
        "status": "Running",
        "version": "1.0.0"
    }