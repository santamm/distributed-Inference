#!/bin/bash
ps auxww | grep 'celery_tasks worker' | awk '{print $2}' | xargs kill -9
sleep 2
conda run -n summarize celery -A celery_tasks worker -P eventlet -Q Summarization -l INFO --detach --logfile celery.log &
celery -A celery_tasks worker -P eventlet -Q Translation -l INFO --detach --logfile celery.log &
conda run -n codegen celery -A celery_tasks worker -P eventlet -Q Generation -l INFO --detach --logfile celery.log &
celery -A celery_tasks worker -P eventlet -Q celery -l INFO --detach --logfile celery.log &

# If you need to use different virtual environments, use conda run -n <venv> celery --version
ps -ef | grep celery