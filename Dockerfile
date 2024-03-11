FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=merlin.settings.production

CMD python manage.py collectstatic --noinput && python manage.py migrate --noinput && python manage.py update_access_permissions && gunicorn --bind 0.0.0.0:8000 merlin.wsgi:application --reload
