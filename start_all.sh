#!/bin/bash

# Stop current running celery servers
echo "Stopping celery...."
#
ps auxww | grep 'celery_tasks worker' | awk '{print $2}' | xargs kill -9
# stop current gunicorn
echo "Stopping gunicorn....."
pkill gunicorn
echo "Launch celery..."	
# launch celery 
# -P eventlet required to use GPUs in celery tasks (https://docs.celeryq.dev/en/stable/userguide/concurrency/eventlet.html)
celery -A celery_tasks worker -P eventlet -l INFO --detach --logfile ~/celery.log &
sleep 1
tail ~/celery.log
echo
# launch  gunicorn
echo "launch gunicorn..."
gunicorn app:app -w 4 -k uvicorn.workers.UvicornWorker --error-logfile ~/gunicorn.err --access-logfile ~/gunicorn.log &
sleep 1
tail ~/gunicorn.log
echo
# ngrok to expose ports
# remove old tunnel
sudo -H -u protago bash -c "ps auxww | grep 'ngrok http 8000' | grep -v grep | awk '{print \$2}' | xargs kill -9"
echo "Starting tunnel on port 8000...."
sleep 2
sudo -H -u protago bash -c 'nohup /home/protago/ngrok http 8000 --log=stdout > ~/ngrok.log &'
sleep 2
sudo -H -u protago bash -c "tail  ~/ngrok.log"

