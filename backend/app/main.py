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
    return {"message": "Usted esta en el backend"}

@app.get("/health")
def health_check():
    """
    Si app esta viva, devuelve ok
    """
    return {"status": "ok"}

@app.get("/data")
def read_data():
    """
    Devuelve datos de el pod en el que se encuentra, va a ser util en el futuro
    """
    return {
        "service": "backend-dummy",
        "status": "success",
        "message": "Datos del sistema recuperados",
        "server_info": {
            "hostname": socket.gethostname(),  #Nombre del contenedor/pod
            "ip": socket.gethostbyname(socket.gethostname()) #Ip del contenedor/pod
        }
    }

if __name__ == "__main__":
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)