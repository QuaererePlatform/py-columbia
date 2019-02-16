#!/usr/bin/env sh

if test -z "$COLUMBIA_APP"; then
    echo "COLUMBIA_APP environment variable must be set."
    exit 1
fi
case $COLUMBIA_APP in
    api)
        echo "Running the API app"
        exec gunicorn -w 4 -b 0.0.0.0:5000 columbia.api:app
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