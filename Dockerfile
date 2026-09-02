FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HOST=0.0.0.0 \
    PORT=8000 \
    ENVIRONMENT=production \
    DATABASE_URL=sqlite:////srv/sentinel/data/sentinel.db

WORKDIR /srv/sentinel

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend
COPY frontend ./frontend
COPY scripts ./scripts

RUN mkdir -p /srv/sentinel/data

EXPOSE 8000

CMD ["sh", "-c", "cd /srv/sentinel/backend && python run.py"]
