
FROM python:3.12-slim

WORKDIR /app

COPY chatbot_backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY chatbot_backend/ .

EXPOSE 8000

CMD ["uvicorn", "agronova:app", "--host", "0.0.0.0", "--port", "8000"]
