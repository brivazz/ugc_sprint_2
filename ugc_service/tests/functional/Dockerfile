FROM python:3.11-slim-buster

WORKDIR /tests/functional

COPY requirements.txt requirements.txt

RUN  pip install --upgrade pip \
     && pip install -r requirements.txt --no-cache-dir

COPY . .

ENTRYPOINT ["sh", "run_tests.sh" ]
