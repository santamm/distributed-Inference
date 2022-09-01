from celery import Celery


app = Celery(include=['celery_tasks.tasks_cpu', 'celery_tasks.tasks_gpu'])
app.config_from_object('celery_tasks.celeryconfig')


if __name__ == '__main__':
  app.start()