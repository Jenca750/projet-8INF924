FROM python:3.11-slim

WORKDIR /app

# Install docker CLI for the ntfy socket management if needed, but the python docker sdk works via socket natively
# We might need curl for testing
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
