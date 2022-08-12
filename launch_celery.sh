#!/bin/bash
ps auxww | grep 'celery_tasks worker' | awk '{print $2}' | xargs kill -9
sleep 1
celery -A celery_tasks worker -P eventlet -l INFO --detach --logfile celery.log &

