FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHON_UNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 

WORKDIR /build
COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHON_UNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 

ARG USER_APP=user-runtime

RUN groupadd -r ${USER_APP} \
    && useradd -m -r -g ${USER_APP} ${USER_APP}

COPY --from=builder /root/.local /home/${USER_APP}/.local

ENV PATH="/home/${USER_APP}/.local/bin:${PATH}"
WORKDIR /app
COPY . .

RUN chown -R ${USER_APP}:${USER_APP} /app
USER ${USER_APP}
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --retries=3 --start-period=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()" || exit 1

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]