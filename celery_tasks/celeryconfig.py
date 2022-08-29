
# Celery confiiguration file
import os
import json
from pathlib import Path



broker_url = "pyamqp://guest@localhost//"
result_backend = "redis://localhost"


task_serializer =  'json'
result_serializer = 'json'
accept_content =  ['json']
worker_prefetch_multiplier = 1
task_acks_late = True
task_track_started = True
result_expires = 604800  # one week
task_reject_on_worker_lost = True
#'task_queue_max_priority': 10

task_routes = {
    'celery_tasks.tasks_gpu.AndreaSummarize': {'queue': 'Summarization'},
    'celery_tasks.tasks_gpu.ProtagoTranslator': {'queue': 'Translation'},
    'celery_tasks.tasks_gpu.ProtagoTranslator': {'queue': 'Generation'},
    'celery_tasks.tasks_cpu.*': {'queue': 'celery'}
}