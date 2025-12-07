from fastapi import FastAPI, Request, HTTPException, Response
import os
import httpx
import uvicorn
import time
from collections import defaultdict

app = FastAPI()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))

# In-memory storage
request_counts = defaultdict(list)  # {IP: [timestamps]}
metrics = {"total_requests": 0, "blocked_requests": 0, "banned_ips": set()}


@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    if request.url.path in ["/metrics", "/health", "/favicon.ico"]:
        return await call_next(request)

    client_ip = request.client.host
    now = time.time()

    # Clean up old timestamps
    request_counts[client_ip] = [t for t in request_counts[client_ip] if now - t < 60]

    metrics["total_requests"] += 1

    if len(request_counts[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        metrics["blocked_requests"] += 1
        metrics["banned_ips"].add(client_ip)
        return Response(content="Too Many Requests", status_code=429)

    request_counts[client_ip].append(now)

    response = await call_next(request)
    return response


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


@app.get("/metrics")
def get_metrics():
    """
    Devuelve metricas de uso
    """
    return {
        "total_requests": metrics["total_requests"],
        "blocked_requests": metrics["blocked_requests"],
        "banned_ips_count": len(metrics["banned_ips"]),
        "banned_ips_list": list(metrics["banned_ips"]),
    }


# async para que pueda anteder a muchos al mismo tiempo
@app.api_route(
    "/proxy/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"],
)
async def proxy(path: str, request: Request):
    """
    Redirige cualquier petición que llegue a /proxy/ hacia el Backend
    """
    # arma url a partir de path y guarda los parametros de la request
    url_destino = f"{BACKEND_URL}/{path}"
    params = dict(request.query_params)

    # httpx se hace pasar por cliente con Asyncclient
    async with httpx.AsyncClient() as client:
        # manda request a la url y devuelve su respuesta
        try:
            # Read body for non-GET requests
            content = await request.body()

            proxy_req = await client.request(
                method=request.method,
                url=url_destino,
                params=params,
                content=content,
                headers=request.headers,
                timeout=5.0,
            )
            return proxy_req.json()

        except httpx.ConnectError:
            raise HTTPException(
                status_code=503, detail="No se pudo conectar con el Backend"
            )
        except Exception as e:
            # If JSON decoding fails or other errors
            raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":

    uvicorn.run("app.main:app", host="0.0.0.0", port=8001, reload=True)
