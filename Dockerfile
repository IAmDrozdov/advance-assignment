FROM python:3.14-slim

WORKDIR /app

RUN pip install uv

COPY requirements.txt .

RUN uv pip install --system --no-cache -r requirements.txt gunicorn

COPY app/ ./app/

RUN mkdir -p /app/data

ENV HOST=0.0.0.0
ENV PORT=8000
ENV WORKERS=4

VOLUME ["/app/data"]

EXPOSE 8000

CMD gunicorn app.main:app \
    --bind ${HOST}:${PORT} \
    --workers ${WORKERS} \
    --worker-class uvicorn.workers.UvicornWorker

