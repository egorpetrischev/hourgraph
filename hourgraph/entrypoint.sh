set -e  # Выход при ошибке

apply_migrations() {
    echo "Checking for migrations..."
    if python manage.py showmigrations | grep -q '\[ \]'; then
        echo "Applying migrations..."
        python manage.py migrate
        python manage.py migrate django_celery_beat
    else
        echo "All migrations have been applied."
    fi
}

create_superuser() {
    if [ -z "$DJANGO_SUPERUSER_EMAIL" ]; then
        echo "DJANGO_SUPERUSER_EMAIL not set. Skipping superuser creation."
        return
    fi

    echo "Checking for superuser..."
    if ! python manage.py shell -c "from hourgraph.models import Users; print(Users.objects.filter(email='$DJANGO_SUPERUSER_EMAIL').exists())" | grep -q "True"; then
        echo "Creating superuser..."
        python manage.py createsuperuser \
            --noinput \
            --email "$DJANGO_SUPERUSER_EMAIL" \
            --username "$DJANGO_SUPERUSER_USERNAME" || echo "Superuser creation skipped"
    else
        echo "Superuser already exists."
    fi
}

case "$1" in
    django)
        apply_migrations
        create_superuser
        echo "Starting Django server..."
        exec python manage.py runserver 0.0.0.0:8000
        ;;
    celery_worker)
        apply_migrations
        echo "Starting Celery worker..."
        exec celery -A celeryconfig.app:celery worker -l INFO
        ;;
    celery_beat)
        apply_migrations
        echo "Starting Celery beat..."
        exec celery -A celeryconfig.app:celery beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ;;
    *)
        echo "Usage: $0 {django|celery_worker|celery_beat}"
        exit 1
        ;;
esac