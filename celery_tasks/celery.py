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


if __name__ == '__main__':
  app.start()