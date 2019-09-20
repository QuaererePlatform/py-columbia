#!/usr/bin/env sh

if test -z "$COLUMBIA_APP"; then
    echo "COLUMBIA_APP environment variable must be set."
    exit 1
fi
case $COLUMBIA_APP in
    api)
        echo "Creating/Upgrading database"
        flask db init
        echo "Running the API app"
        exec gunicorn -c "python:columbia.config.gunicorn_config" "columbia.app:create_app()"
        ;;
    tasks)
        echo "Running the tasks app"
        exec celery -A columbia.tasks worker -l info
        ;;
    scheduler)
        echo "Running the tasks scheduler app"
        exec celery -A columbia.tasks beat -l info
        ;;
     *)
        echo "Invalid app: $COLUMBIA_APP"
        exit 2
esac