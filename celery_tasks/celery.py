from celery import Celery

app = Celery('hf_model',
  broker='pyamqp://guest@localhost//',
  backend='redis://localhost',
  include=['celery_tasks.tasks']
)


if __name__ == '__main__':
  app.start()