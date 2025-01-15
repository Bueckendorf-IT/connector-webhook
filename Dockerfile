FROM python:3.9.21-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PORT 8000

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:${PORT}", "main:app"]