# NetMind Inference platform description (draft)

# Intro

This page walks through our proposal for the NetMind inference platform for serving ML models using Celery and FastAPI.

Below is a summary of potential approaches for deploying (pre)trained models to production:

1. Load model directly in application: this option involves having the pretrained model directly in the main application code. For small models this might be feasible however large models may introduce memory issues. This option also introduces a direct dependency on the model within the main application (coupled).
2. Offline batch prediction: Use cases that do not require near real-time predictions can make use of this option. The model can be used the make predictions for a batch of data in a process that runs at defined intervals (e.g. overnight). The predictions can then be utilized by the application once the batch job is complete. Resource for prediction is only required when the batch process runs which can be beneficial.
3. API: The third option is to deploy the model as its own microservice and communicate with it via an API. This decouples the application from the model and allows it to be utilized from multiple other services. The ML service can serve requests in one of the two ways described below.

Synchronous: the client requests a prediction and must wait for the model service to return a prediction. This is suitable for small models that require a small number of computations, or where the client cannot continue other processing steps without a prediction.

Asynchronous: instead of directly returning a prediction the model service will return a unique identifier for a task. Whilst the prediction task is being completed by the model service the client is free to continue other processing. The result can then be fetched via a results endpoint using the unique task id.

# Proposed Architecture

The solution proposed is depicted below:

![Untitled](Untitled.png)

## Process Description

1. Client sends a POST request to the FastAPI prediction endpoint, with the relevant feature information contained in the request body (JSON).
2. The request body is validated by FastAPI against a defined model (i.e. checks if the expected features have been provided). If the validation is successful then a Celery prediction task is created and passed to the configured broker (e.g. RabbitMQ).
3. The unique id is returned to the client if a task is created successfully.

Below an example of the FastAPI call to submit a prediction task:

```python
@app.post('/predict', response_model=Task, status_code=202)
async def submit(query: Query):
    """Create celery prediction task. Return task_id to client in order to retrieve result"""
    task_id = predict.delay(query.sentence)
    #print(f"Task id: {task_id}")
    return {'task_id': str(task_id), 'status': 'Processing'}
```

1. The prediction task is delivered to an available worker by the broker. Once delivered the worker generates a prediction using the pretrained ML model.
2. Once a prediction has been generated the result is stored using the Celery backend (Redis).
3. At any point after step 3 the client can begin to poll the FastAPI results endpoint using the unique task id. Once the prediction is ready it will be returned to the client.

Below an example of a FastAPI call to retrieve model predictions:

```python
@app.get('/result/{task_id}', response_model=Prediction, status_code=200,
	responses={202: {'model': Task, 'description': 'Accepted: Not Ready'}})
async def predict_result(task_id: str):
    """Fetch result for given task_id"""
    print(f"Fetching result for {task_id}....")
    task = AsyncResult(task_id)
    if not task.ready():
      return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return {'task_id': task_id, 'status': 'Success', 'result': str(result)}
```

## Project Structure

The project structure is depicted below:

```jsx
celery_netmind
│   app.py
│   README.md
│   test_client.py
│
├───celery_tasks
│   │   tasks.py
│   │   worker.py
│   │   __init__.py
│   │
│   ├───ml_models
│   │   │   <model-1 subdir>
│   │   │   <model-2 subdir>
|   |   |   . . . . .
|   │   │   <model-n subdir>
|
```

- _app.py_: FastAPI application including route definitions.
-
- _test_client.py_: Script used for testing the set-up. We’ll cover this in more detail later.
- *celery_task_app\tasks.py:* Contains Celery task definition, specifically the prediction task in our case*.*
- *celery_task_app\worker.py:* Defines the celery app instance and associated config.
- *celery_task_app\ml_models\models.py:* Machine learning models wrapper classese used to load pretrained models and serve predictions.

## Deployment

### RabbitMQ

```bash
rabbitmq-server

##  ##      RabbitMQ 3.10.5
##  ##
##########  Copyright (c) 2007-2022 VMware, Inc. or its affiliates.
######  ##
##########  Licensed under the MPL 2.0. Website: https://rabbitmq.com

  Erlang:      25.0 [jit]
  TLS Library: OpenSSL - OpenSSL 1.1.1o  3 May 2022

  Doc guides:  https://rabbitmq.com/documentation.html
  Support:     https://rabbitmq.com/contact.html
  Tutorials:   https://rabbitmq.com/getstarted.html
  Monitoring:  https://rabbitmq.com/monitoring.html

  Logs: /opt/homebrew/var/log/rabbitmq/rabbit@localhost.log
        /opt/homebrew/var/log/rabbitmq/rabbit@localhost_upgrade.log
        <stdout>

  Config file(s): (none)

  Starting broker... completed with 7 plugins.
```

### Redis

````bash
redis-server
86827:C 08 Jul 2022 16:24:10.202 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
86827:C 08 Jul 2022 16:24:10.202 # Redis version=7.0.0, bits=64, commit=00000000, modified=0, pid=86827, just started
86827:C 08 Jul 2022 16:24:10.202 # Warning: no config file specified, using the default config. In order to specify a config file use redis-server /path/to/redis.conf
86827:M 08 Jul 2022 16:24:10.202 * Increased maximum number of open files to 10032 (it was originally set to 2560).
86827:M 08 Jul 2022 16:24:10.202 * monotonic clock: POSIX clock_gettime
                _._
           _.-``__ ''-._
      _.-``    `.  `_.  ''-._           Redis 7.0.0 (00000000/0) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     PID: 86827
  `-._    `-._  `-./  _.-'    _.-'
 |`-._`-._    `-.__.-'    _.-'_.-'|
 |    `-._`-._        _.-'_.-'    |           https://redis.io
  `-._    `-._`-.__.-'_.-'    _.-'
 |`-._`-._    `-.__.-'    _.-'_.-'|
 |    `-._`-._        _.-'_.-'    |
  `-._    `-._`-.__.-'_.-'    _.-'
      `-._    `-.__.-'    _.-'
          `-._        _.-'
              `-.__.-'

86827:M 08 Jul 2022 16:24:10.204 # WARNING: The TCP backlog setting of 511 cannot be enforced because kern.ipc.somaxconn is set to the lower value of 128.
86827:M 08 Jul 2022 16:24:10.204 # Server initialized
86827:M 08 Jul 2022 16:24:10.204 * The AOF directory appendonlydir doesn't exist
86827:M 08 Jul 2022 16:24:10.204 * Loading RDB produced by version 7.0.0
86827:M 08 Jul 2022 16:24:10.204 * RDB age 324 seconds
86827:M 08 Jul 2022 16:24:10.204 * RDB memory usage when created 1.22 Mb
86827:M 08 Jul 2022 16:24:10.204 * Done loading RDB, keys loaded: 37, keys expired: 0.
86827:M 08 Jul 2022 16:24:10.204 * DB loaded from disk: 0.000 seconds
86827:M 08 Jul 2022 16:24:10.204 * Ready to accept connections
````

### Celery workers:

Launch celery workers (on each celery dedicated machine): the configuration of the celery server is stored in the `celery.py`file under the `celery_tasks` directory (in this case all servers are installed on `localhost`):

```python
from celery import Celery

app = Celery('hf_model',
  broker='pyamqp://guest@localhost//',
  backend='redis://localhost',
  include=['celery_tasks.tasks']
)

if __name__ == '__main__':
  app.start()
```

```bash
celery -A celery_tasks worker -l INFO

-------------- celery@Maurizios-MacBook-Pro.local v5.0.5 (singularity)
--- ***** -----
-- ******* ---- macOS-12.4-arm64-arm-64bit 2022-07-10 16:35:40
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         hf_model:0x104b0b430
- ** ---------- .> transport:   amqp://guest:**@localhost:5672//
- ** ---------- .> results:     redis://localhost/
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery


[tasks]
  . celery_tasks.tasks.distilbart-cnn-12-6

[2022-07-10 16:35:40,947: INFO/MainProcess] Connected to amqp://guest:**@127.0.0.1:5672//
[2022-07-10 16:35:40,955: INFO/MainProcess] mingle: searching for neighbors
[2022-07-10 16:35:41,973: INFO/MainProcess] mingle: all alone
[2022-07-10 16:35:41,988: INFO/MainProcess] celery@Maurizios-MacBook-Pro.local ready.
```

### FastAPI

Finally, launch the FastAPI web server:

```bash
uvicorn app:app

INFO:     Started server process [17807]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## Users API to run prediction tasks

The first part is choosing which model to run:

```python
ENDPOINT = https://api-inference.netmind.com/models/<MODEL_ID>
```

Below an example of Python code to run to submit a task:

```python
import json
import requests
API_URL = "https://api-inference.netmind.com/models/gpt2"
headers = {"Authorization": f"Bearer {API_TOKEN}"}
"""
def query(payload):
    data = json.dumps(payload)
    response = requests.request("POST", API_URL, headers=headers, data=data)
    return json.loads(response.content.decode("utf-8"))
data = query("Can you please let us know more details about your ")
"""

#base_uri = r'http://127.0.0.1:8000'
predict_task_uri = API_URL + '/predict'
task = requests.post(predict_task_uri, headers=headers, json=data)
print(task.json())
task_id = task.json()['task_id']
```

and retrieve results:

```python
predict_result_uri = API_URL + '/result/' + task_id
attempts = 0
result = None
while attempts < max_attempts:
	attempts += 1
  #print(f"Retrieving {predict_result_uri}")
  result_response = requests.get(predict_result_uri)
  #print(result_response)
  if result_response.status_code == 200:
		result = result_response.json()
    break
  sleep(poll_interval)
return result
```

# Base User Functionalities

- User Registration/Login
- List/Description of available models for inference
- Model Demo (video)
- Model Inference interactive test (for each model)
- Get API Key
- How-to guide to submit API inference request in Python/curl
- FAQ

### User Registration

Similar to training platform (on invite using an invite code). Data gathered:

- Name
- Surname
- Organization
- Email
- Invite code

### User Login

Same as training platform

### List/Description of available models for inference

Model list on Inference Home Page

One page per model, including:

- Model Name/id
- Model description including reference to published papers, performance metrics, inference time

### Model Inference example

- Hosted Inference test, with pre-existing examples in a drop-down lis

### Get API Key

User can download an API key to access our inference APIs to integrate NLP, audio and computer vision models deployed for inference via simple API calls. For invitation users, the API key can be sent in the acknowledgement email (paying customers will be required to subscribe to a paid plan).

Usage will be similar to HuffingFace APIs:

```python
import requests
import json

def netmind_submit(data, model_id, api_token):
	headers = {"Authorization": f"Bearer {api_token}"}
	API_URL = f"https://api-inference.netmind.com/models/predict/{model_id}"
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()

model_id = "distilbert-base-uncased"
api_token = "api_XXXXXXXX" # get yours during registration
taskid = netmind_inference("The goal of life is [MASK].", model_id, api_token)

def netmind_retrieve(task_id, model_id, api_token):
	headers = {"Authorization": f"Bearer {api_token}"}
	API_URL = f"https://api-inference.netmind.com/models/result/{model_id}"

	attempts = 0
	result = None
	while attempts < max_attempts:
		attempts += 1
	  result_response = requests.get(API_URL)
	  if result_response.status_code == 200:
			result = result_response.json()
	    break
	  sleep(poll_interval)
	return result
```

# Scaling further using Kubernetes

When working with Python, [Celery is a popular option for a job queuing system](https://docs.celeryproject.org/en/stable/), as it can be paired with [a message broker such as RabbitMQ](https://www.rabbitmq.com/) to connect the app that adds the tasks (producer) and the worker processing the jobs (consumers). Moreover, you can process tasks quicker if you have several worker processes running simultaneously.

However, we usually face two problems with the above architecture:

1. workers might consume resources, even when idle.
2. we don’t have a mechanism to scale up workers based on the queue length.

In Kubernetes, you can scale your app's instances with [the Horizontal Pod Autoscaler (HPA).](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)

The Horizontal Pod Autoscaler (HPA) can be configured to increase and decrease the number of replicas based on metrics such as CPU and memory.

You could increment the Pods and consume messages quicker when the queue is full. If the queue is empty, you can scale your workers down to zero and save on resources. However, Kubernetes only scales Pods on metrics such as CPU and memory and it does not understand custom metrics (like the length of the queue) out of the box.

We will follow an approach like using an event-driven autoscaler such as [KEDA](https://keda.sh/) to collect and expose metrics to Kubernetes from databases (MySQL, Postgres), message queues (RabbitMQ, AWS SQS), telemetry systems (AWS Cloudwatch, Azure Monitor), etc.

The data will then be used in combination with the Horizontal Pod Autoscaler to create more Pods when the queue is full.

A full description and implementation of this approach can be found [here](https://learnk8s.io/scaling-celery-rabbitmq-kubernetes) and [here](https://github.com/yolossn/flask-celery-microservice).

# References

[\*Celery - Distributed Task Queue](https://docs.celeryq.dev/en/stable/).\*

[\*RabbitMQ is the most widely deployed open source message broker](https://www.rabbitmq.com/).\*

[\*Serving ML Models in Production with FastAPI and Celery](https://towardsdatascience.com/deploying-ml-models-in-production-with-fastapi-and-celery-7063e539a5db).\*

[\*Scaling Celery workers with RabbitMQ on Kubernetes](https://learnk8s.io/scaling-celery-rabbitmq-kubernetes).\*

[_Redis: a vibrant, open source database._](https://redis.io/)

_[Kubernetes Event-driven Autoscaling](https://keda.sh/)._
