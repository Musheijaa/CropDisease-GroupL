# project/Dockerfile

FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY project/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY project/ .

EXPOSE 8080

CMD ["python", "manage.py", "runserver", "0.0.0.0:8080"]
