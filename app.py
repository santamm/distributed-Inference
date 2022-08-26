from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from celery import Celery
from celery.result import AsyncResult
import logging



app = Celery()
app.config_from_object('celery_tasks.celeryconfig')


api = FastAPI()

#class Payload(BaseModel):
#  """ Features for prediction """
#  data: str

class Payload(BaseModel):
  """ Features for prediction """
  data: str
  device: str

class GenerationPayload(BaseModel):
  """ Features for prediction """
  data: str
  filling_method: str
  device: str

class Task(BaseModel):
    """ Celery task representation """
    task_id: str
    status: str


class TextGeneration(BaseModel):
    """ Prediction task result """
    task_id: str
    status: str
    result: str



@api.post('/protago_translate/predict', response_model=Task, status_code=202)
async def translate(payload: Payload):
    """Create celery prediction task. Return task_id to client in order to retrieve result"""
    #task_id = protago_translate.delay(payload.data, payload.device)
    print(f"Requested summarization on {payload.device}")
    task_id = app.send_task('celery_tasks.tasks.ProtagoTranslator', [payload.data, payload.device])
    print(f"Task id: {task_id}")
    return {'task_id': str(task_id), 'status': 'Processing'}


@api.get('/protago_translate/result/{task_id}', response_model=TextGeneration, status_code=200, 
  responses={202: {'model': Task, 'description': 'Accepted: Not Ready'}})
async def translate_result(task_id: str):
    """Fetch result for given task_id"""
    print(f"Fetching result for {task_id}....")
    task = AsyncResult(task_id)
    if not task.ready():
      #print(app.url_path_for('predict'))
      return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return {'task_id': task_id, 'status': 'Success', 'result': str(result)}


@api.post('/summarize/predict', response_model=Task, status_code=202)
async def summarize(payload: Payload):
    """Create celery prediction task. Return task_id to client in order to retrieve result"""
    #task_id = distilbart_summarize_predict.delay(payload.data, payload.device)
    task_id = app.send_task('celery_tasks.tasks.DistilBartSummarize', [payload.data, payload.device])
    print(f"Task id: {task_id}")
    return {'task_id': str(task_id), 'status': 'Processing'}


@api.get('/summarize/result/{task_id}', response_model=TextGeneration, status_code=200, 
  responses={202: {'model': Task, 'description': 'Accepted: Not Ready'}})
async def summarize_result(task_id: str):
    """Fetch result for given task_id"""
    print(f"Fetching result for {task_id}....")
    task = AsyncResult(task_id)
    if not task.ready():
      #print(app.url_path_for('predict'))
      return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return {'task_id': task_id, 'status': 'Success', 'result': str(result)}

@api.post('/protago_generate/predict', response_model=Task, status_code=202)
async def generate(payload: GenerationPayload):
    """Create celery prediction task. Return task_id to client in order to retrieve result"""
    #task_id = protago_generate.delay(payload.data, payload.filling_method, payload.device)
    task_id = app.send_task('celery_tasks.tasks.ProtagoGenerator', [payload.data, payload.device])

    print(f"Task id: {task_id}")
    return {'task_id': str(task_id), 'status': 'Processing'}


@api.get('/protago_generate/result/{task_id}', response_model=TextGeneration, status_code=200, 
  responses={202: {'model': Task, 'description': 'Accepted: Not Ready'}})
async def generate_result(task_id: str):
    """Fetch result for given task_id"""
    print(f"Fetching result for {task_id}....")
    task = AsyncResult(task_id)
    if not task.ready():
      #print(app.url_path_for('predict'))
      return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return {'task_id': task_id, 'status': 'Success', 'result': str(result)}



@api.post('/andrea/predict', response_model=Task, status_code=202)
async def andrea_summarize(payload: Payload):
    """Create celery prediction task. Return task_id to client in order to retrieve result"""
    #task_id = andrea_summarize_predict.delay(payload.data)
    #print(f"Task id: {task_id}")
    
    # Call task name celery_tasks.tasks.AndreaSummarize
    #celeryapp.tasks.append(
    task_id = app.send_task('celery_tasks.tasks.AndreaSummarize', [payload.data, payload.device])  # Send task by name
    #)
    logging.info(f"Task Request sent {task_id }")
    
    return {'task_id': str(task_id), 'status': 'Processing'}


@api.get('/andrea/result/{task_id}', response_model=TextGeneration, status_code=200, 
  responses={202: {'model': Task, 'description': 'Accepted: Not Ready'}})
async def andrea_summarize_result(task_id: str):
    """Fetch result for given task_id"""
    print(f"Fetching result for {task_id}....")
    task = AsyncResult(task_id)
    if not task.ready():
      #print(app.url_path_for('predict'))
      return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()#[0]['summary_text']
    return {'task_id': task_id, 'status': 'Success', 'result': str(result)}
