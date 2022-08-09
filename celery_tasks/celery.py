from celery import Celery
import os
import json
from pathlib import Path



with open(Path(os.path.dirname(__file__)).parent/"config.json") as cfg_file:
        worker_dict = json.load(cfg_file)

celery_broker_url = worker_dict ["celery_broker_url"]
celery_backend_url = worker_dict ["celery_backend_url"]


app = Celery('netmind_model',
  broker=celery_broker_url,
  backend=celery_backend_url ,
  include=['celery_tasks.tasks']
)


app.conf.update({

    'task_serializer': 'json',
    'result_serializer': 'json',
    'accept_content': ['json'],
    'worker_prefetch_multiplier': 1,
    'task_acks_late': True,
    'task_track_started': True,
    'result_expires': 604800,  # one week
    'task_reject_on_worker_lost': True,
    #'task_queue_max_priority': 10
})


if __name__ == '__main__':
  app.start()