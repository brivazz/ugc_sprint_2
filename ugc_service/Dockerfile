FROM python:3.11-slim-buster

WORKDIR /opt/app
ENV PYTHONPATH=/opt/app/src

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT gunicorn main:app -w $UGC_2_WORKERS \
          -k uvicorn.workers.UvicornWorker \
          --bind $UGC_2_API_HOST:$UGC_2_API_PORT
