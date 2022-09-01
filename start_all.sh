#!/bin/bash
# This script is to be used in case celery workers and gunicor are executed in the same node
# Stop current running celery servers
echo "Stopping celery...."
#
ps auxww | grep 'celery_tasks worker' | grep -v grep | awk '{print $2}' | xargs kill -9
# stop current gunicorn
echo "Stopping gunicorn....."
ps auxww | grep 'gunicorn' | grep -v grep | awk '{print $2}' | xargs kill -9
sleep 2
echo "Launch celery..."	
# launch celery 
# Use default queue for CPU workers
celery -A celery_tasks worker -P prefork -Q celery -l INFO --detach --logfile celery.log &
# GPU workers if GPU is available
conda run -n summarize celery -A celery_tasks worker -P eventlet -Q Summarization -l INFO --detach --logfile celery.log &
celery -A celery_tasks worker -P eventlet -Q Translation -l INFO --detach --logfile celery.log &
conda run -n codegen celery -A celery_tasks worker -P eventlet -Q Generation -l INFO --detach --logfile celery.log &
tail celery.log
echo
# launch  gunicorn
echo "launch gunicorn..."
gunicorn app:api -w 1 -k uvicorn.workers.UvicornWorker --daemon --error-logfile gunicorn.err --access-logfile gunicorn.log &
sleep 1
tail gunicorn.log
echo
tail -f celery.log
# ngrok to expose ports
# remove old tunnel
#sudo -H -u protago bash -c "ps auxww | grep 'ngrok http 8000' | grep -v grep | awk '{print \$2}' | xargs kill -9"
#echo "Starting tunnel on port 8000...."
#sleep 2
#sudo -H -u protago bash -c 'nohup /home/protago/ngrok http 8000 --log=stdout > ~/ngrok.log &'
#sleep 2
#sudo -H -u protago bash -c "tail  ~/ngrok.log"

