release: python manage.py collectstatic --no-input; python manage.py migrate
web: gunicorn discogportal.wsgi --log-file -
