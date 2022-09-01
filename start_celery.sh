#!/bin/bash
ps auxww | grep 'celery_tasks worker' | grep -v grep | awk '{print $2}' | xargs kill -9
sleep 2
# Separate GPU workers from CPU workers
# Selecting pre-fork and setting the concurrency level to the number of CPU cores is the best option for CPU bound tasks.
# CPU workers

conda run -n summarize celery -A celery_tasks worker -P eventlet -Q Summarization_cpu -l INFO --detach --logfile celery.log &
celery -A celery_tasks worker -P eventlet -Q Translation_cpu -l INFO --detach --logfile celery.log &
conda run -n codegen celery -A celery_tasks worker -P eventlet -Q Generation_cpu -l INFO --detach --logfile celery.log &
# default queue
celery -A celery_tasks worker -P prefork -Q celery -l INFO --detach --logfile celery.log &


# GPU workers if GPU is available
conda run -n summarize celery -A celery_tasks worker -P eventlet -Q Summarization -l INFO --detach --logfile celery.log &
celery -A celery_tasks worker -P eventlet -Q Translation -l INFO --detach --logfile celery.log &
conda run -n codegen celery -A celery_tasks worker -P eventlet -Q Generation -l INFO --detach --logfile celery.log &

# If you need to use different virtual environments, use conda run -n <venv> celery --version
ps -ef | grep celery

tail -f celery.log