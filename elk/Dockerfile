FROM python:3.11-slim-buster

WORKDIR /opt/app

COPY requirements.txt .


RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT  gunicorn main:app -w $WORKERS -k uvicorn.workers.UvicornWorker --bind $FAST_API_HOST:$FAST_API_PORT
