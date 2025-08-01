from fastapi import FastAPI

app = FastAPI(title="RoboDocAI API")

@app.get("/", tags=["Health Check"])
async def root():
    return {"message": "RoboDocAI API is running."}