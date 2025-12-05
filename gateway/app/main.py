from fastapi import FastAPI
import os
import socket
import uvicorn

app = FastAPI()

@app.get("/")
def home():
    """
    Root del gateway
    """
    return {"message": "Usted esta en el gateway"}

@app.get("/health")
def health_check():
    """
    Si app esta viva, devuelve ok
    """
    return {"status": "ok"}

if __name__ == "__main__":
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)