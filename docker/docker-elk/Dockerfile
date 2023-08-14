FROM python:3.11-slim-buster

WORKDIR /opt/app

COPY requirements.txt .

RUN pip install --upgrade pip \
    && pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT [ "python", "main.py" ]