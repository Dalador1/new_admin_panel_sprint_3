#!/bin/sh


# Применяем миграции
echo "Applying database migrations..."
python manage.py migrate --noinput

# Собираем статические файлы
echo "Collecting static files..."
python manage.py collectstatic  --noinput

# Создаём суперпользователя, если его нет
echo "Creating superuser..."
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
if not User.objects.filter(username='${DJANGO_SUPERUSER_USERNAME}').exists():
    User.objects.create_superuser(
        username='${DJANGO_SUPERUSER_USERNAME}',
        email='${DJANGO_SUPERUSER_EMAIL}',
        password='${DJANGO_SUPERUSER_PASSWORD}'
    )
"

# Запускаем uWSGI с конфигурационным файлом
echo "Starting uWSGI server..."
exec uwsgi --ini /app/uwsgi.ini 