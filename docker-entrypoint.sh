#!/bin/bash
#python manage.py migrate        # Apply database migrations
#python manage.py collectstatic --clear --noinput # clearstatic files
python manage.py collectstatic --noinput  # collect static files

# Prepare log files and start outputting logs to stdout
touch /var/logs/gunicorn.log
touch /var/logs/access.log
tail -n 0 -f /var/logs/*.log &
echo Starting nginx
# Start Gunicorn processes
echo Starting Gunicorn.
exec gunicorn portal.wsgi:application \
    --name paddlepaddle_portal \
    --bind unix:django_app.sock \
    --workers 5 \
    --log-level=info \
    --log-file=/var/logs/gunicorn.log \
    --access-logfile=/var/logs/access.log &
exec service nginx start