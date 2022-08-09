from pydantic import BaseModel
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from celery.result import AsyncResult
import logging

from celery_tasks.tasks import andrea_summarize_predict, distilbart_summarize_predict, distilbart_summarize_predict_device
#from models import Customer, Task, Prediction

app = FastAPI()

#class Payload(BaseModel):
#  """ Features for prediction """
#  data: str

class Payload(BaseModel):
  """ Features for prediction """
  data: str
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



@app.post('/summarize/predict', response_model=Task, status_code=202)
async def summarize(payload: Payload):
    """Create celery prediction task. Return task_id to client in order to retrieve result"""
    task_id = distilbart_summarize_predict.delay(payload.data, payload.device)
    print(f"Task id: {task_id}")
    return {'task_id': str(task_id), 'status': 'Processing'}


@app.get('/summarize/result/{task_id}', response_model=TextGeneration, status_code=200, 
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

@app.post('/codegen/predict', response_model=Task, status_code=202)
async def codegen(payload: Payload):
    """Create celery prediction task. Return task_id to client in order to retrieve result"""
    task_id = codegen_predict.delay(payload.data)
    #print(f"Task id: {task_id}")
    return {'task_id': str(task_id), 'status': 'Processing'}


@app.get('/codegen/result/{task_id}', response_model=TextGeneration, status_code=200, 
  responses={202: {'model': Task, 'description': 'Accepted: Not Ready'}})
async def codegen_result(task_id: str):
    """Fetch result for given task_id"""
    print(f"Fetching result for {task_id}....")
    task = AsyncResult(task_id)
    if not task.ready():
      #print(app.url_path_for('predict'))
      return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return {'task_id': task_id, 'status': 'Success', 'result': str(result)}



@app.post('/andrea/predict', response_model=Task, status_code=202)
async def andrea_summarize(payload: Payload):
    """Create celery prediction task. Return task_id to client in order to retrieve result"""
    task_id = andrea_summarize_predict.delay(payload.data)
    #print(f"Task id: {task_id}")
    return {'task_id': str(task_id), 'status': 'Processing'}


@app.get('/andrea/result/{task_id}', response_model=TextGeneration, status_code=200, 
  responses={202: {'model': Task, 'description': 'Accepted: Not Ready'}})
async def andrea_summarize_result(task_id: str):
    """Fetch result for given task_id"""
    print(f"Fetching result for {task_id}....")
    task = AsyncResult(task_id)
    if not task.ready():
      #print(app.url_path_for('predict'))
      return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return {'task_id': task_id, 'status': 'Success', 'result': str(result)}
