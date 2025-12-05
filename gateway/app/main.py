from fastapi import FastAPI, Request, HTTPException
import os
import httpx
import uvicorn

app = FastAPI()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

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

#async para que pueda anteder a muchos al mismo tiempo
@app.api_route("/proxy/{path:path}")
async def proxy(path: str, request: Request):
    """
    Redirige cualquier petición que llegue a /proxy/ hacia el Backend
    """
    #arma url a partir de path y guarda los parametros de la request
    url_destino = f"{BACKEND_URL}/{path}"
    params = dict(request.query_params)

    #httpx se hace pasar por cliente con Asyncclient
    async with httpx.AsyncClient() as client:
        #manda request a la url y devuelve su respuesta
        try:
            proxy_req = await client.request(
                method=request.method,
                url=url_destino,
                params=params,
                timeout=5.0
            )
            return proxy_req.json()
            
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="No se pudo conectar con el Backend")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    
    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)