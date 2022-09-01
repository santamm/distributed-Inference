#!/bin/bash
# stop current gunicorn
echo "Stopping gunicorn....."
ps auxww | grep 'gunicorn' | grep -v grep | awk '{print $2}' | xargs kill -9
sleep 1
# launch  gunicorn
echo "launch gunicorn..."
gunicorn app:api -w 1 -k uvicorn.workers.UvicornWorker --daemon --error-logfile gunicorn.err --access-logfile gunicorn.log
sleep 1

tail -f gunicorn.err
