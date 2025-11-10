FROM python:3.13-slim

RUN python -m pip install --upgrade pip

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .


RUN mkdir -p /var/www/static /var/www/media && \
    adduser --disabled-password --gecos '' appuser &&  \
    chown -R appuser:appuser /app /var/www && \
    chmod -R 755 /app


USER appuser


CMD ["gunicorn", "app.wsgi:application", "--bind", "0.0.0.0:8000"]