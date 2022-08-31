# NetMind Inference Platform

# Introduction

This page describes the NetMind inference platform for serving ML models using Celery and FastAPI.

Below is a summary of potential approaches for deploying (pre)trained models to production:

1. Load model directly in application: this option involves having the pretrained model directly in the main application code. For small models this might be feasible however large models may introduce memory issues. This option also introduces a direct dependency on the model within the main application (coupled).
2. Offline batch prediction: Use cases that do not require near real-time predictions can make use of this option. The model can be used the make predictions for a batch of data in a process that runs at defined intervals (e.g. overnight). The predictions can then be utilized by the application once the batch job is complete. Resource for prediction is only required when the batch process runs which can be beneficial.
3. API: The third option is to deploy the model as its own microservice and communicate with it via an API. This decouples the application from the model and allows it to be utilized from multiple other services. The ML service can serve requests in one of the two ways described below.

Synchronous: the client requests a prediction and must wait for the model service to return a prediction. This is suitable for small models that require a small number of computations, or where the client cannot continue other processing steps without a prediction.

Asynchronous: instead of directly returning a prediction the model service will return a unique identifier for a task. Whilst the prediction task is being completed by the model service the client is free to continue other processing. The result can then be fetched via a results endpoint using the unique task id.

# Architecture

The solution is depicted below:

![Untitled](Untitled.png)

## API Calls

1. Client sends a POST request to the FastAPI prediction endpoint, with the relevant feature information contained in the request body (JSON).
2. The request body is validated by FastAPI against a defined model (i.e. checks if the expected features have been provided). If the validation is successful then a Celery prediction task is created and passed to the configured broker (e.g. RabbitMQ).
3. The unique id is returned to the client if a task is created successfully.
4. The prediction task is delivered to an available worker by the broker. Once delivered the worker generates a prediction using the pretrained ML model.
5. Once a prediction has been generated the result is stored using the Celery backend (Redis).
6. At any point after step 3 the client can begin to poll the FastAPI results endpoint using the unique task id. Once the prediction is ready it will be returned to the client.

Below an example of the FastAPI call to submit a prediction task:

```bash
# Here shell API call to submit a request

curl -d '{"data":"I have been waiting for netmind.ai my whole life", "device":"GPU"}' -H "Content-Type: application/json" -X POST http://127.0.0.1:8000/summarize/predict
```

That will return:

```bash
{"task_id":"57717eec-6202-41fa-95e2-9e05f0b7b2e9","status":"Processing"}
```

And an API call to retrieve the result from a task:

```bash
curl http://localhost:8000/andrea/result/57717eec-6202-41fa-95e2-9e05f0b7b2e9
```

And the result returned is:

```bash
{"task_id":"57717eec-6202-41fa-95e2-9e05f0b7b2e9","status":"Success","result":"Netmind.ai is a web-based search engine powered by a unique algorithm developed by a team of computer scientists known as the \"Netminders\", who search the web for the most interesting content. The algorithm is based on a unique combination of machine learning and advanced computer vision. To search the internet, the netminders use a combination of computer vision and advanced human intelligence, called \"netmind\" to search for content."}
```

# Installation

## Machine SW deployment

The following machines have been allocated for the test platform:

| Node | Machine | Applications |
| --- | --- | --- |
| None 1 | 5.tcp.ngrok.io:24565 | guinicorn, flower |
| Node 2 | 5.tcp.ngrok.io:24556 | Redis, RabbitMQ |
| Node 3 | 5.tcp.ngrok.io:24653 | celery workers |
| Node 4 | 5.tcp.ngrok.io:24653 | celery workers |

## Shared tasks on all machines

Please apply the steps below on all machines:

```bash
# Download Miniconda from repository
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh

chmod +x Miniconda3-latest-Linux-x86_64.sh
./Miniconda3-latest-Linux-x86_64.sh

# Create netmind environment
conda create -n netmind python=3.9
conda activate netmind

# Install libraries required by netmind
pip install -r requirements.txt

# The requirements.txt includes the following # The requirements.txt includes the following 
```

The *requirements.txt* includes the following packages:

```bash
celery[eventlet]
joblib
Pillow
redis
pydantic
uvicorn
fastapi
pynvml
```

## RabbitMQ

RabbitMQ manages the queues for tasks request and dispatching of any task to the appropriate queue. We have installed RabbitMQ on node2.

```bash
# RabbitMQ installation: as on https://www.rabbitmq.com/install-debian.html#apt-cloudsmith
#!/usr/bin/sh

sudo apt-get install curl gnupg apt-transport-https -y

## Team RabbitMQ's main signing key
curl -1sLf "https://keys.openpgp.org/vks/v1/by-fingerprint/0A9AF2115F4687BD29803A206B73A36E6026DFCA" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/com.rabbi>
## Launchpad PPA that provides modern Erlang releases
curl -1sLf "https://keyserver.ubuntu.com/pks/lookup?op=get&search=0xf77f1eda57ebb1cc" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/net.launchpad.ppa.rabbit>
## PackageCloud RabbitMQ repository
curl -1sLf "https://packagecloud.io/rabbitmq/rabbitmq-server/gpgkey" | sudo gpg --dearmor | sudo tee /usr/share/keyrings/io.packagecloud.rabbitmq.gpg > /dev/null

## Add apt repositories maintained by Team RabbitMQ
sudo tee /etc/apt/sources.list.d/rabbitmq.list <<EOF

## Provides modern Erlang/OTP releases
##
## "bionic" as distribution name should work for any reasonably recent Ubuntu or Debian release.
## See the release to distribution mapping table in RabbitMQ doc guides to learn more.
deb [signed-by=/usr/share/keyrings/net.launchpad.ppa.rabbitmq.erlang.gpg] http://ppa.launchpad.net/rabbitmq/rabbitmq-erlang/ubuntu jammy main
deb-src [signed-by=/usr/share/keyrings/net.launchpad.ppa.rabbitmq.erlang.gpg] http://ppa.launchpad.net/rabbitmq/rabbitmq-erlang/ubuntu jammy main

## Provides RabbitMQ
##
## "bionic" as distribution name should work for any reasonably recent Ubuntu or Debian release.
## See the release to distribution mapping table in RabbitMQ doc guides to learn more.
deb [signed-by=/usr/share/keyrings/io.packagecloud.rabbitmq.gpg] https://packagecloud.io/rabbitmq/rabbitmq-server/ubuntu/ jammy main
deb-src [signed-by=/usr/share/keyrings/io.packagecloud.rabbitmq.gpg] https://packagecloud.io/rabbitmq/rabbitmq-server/ubuntu/ jammy main
EOF

## Update package indices
sudo apt-get update -y

## Install Erlang packages
sudo apt-get install -y erlang-base \
                        erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
                        erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
                        erlang-runtime-tools erlang-snmp erlang-ssl \
                        erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl

## Install rabbitmq-server and its dependencies
sudo apt-get install rabbitmq-server -y --fix-missing
```

Once RabbitMQ is installed, proceed to configuration for NetMind:

```bash
# Customize logging level and log directory in the configuration file 
nano /etc/rabbitmq/rabbitmq.conf

# For production config, follow the guide below at: https://www.rabbitmq.com/production-checklist.html
# list users 
sudo rabbitmqctl list_users
sudo rabbitmqctl add_user netmind
sudo rabbitmqctl set_permissions 'netmind' '.*' '.*' '.*'

#sudo rabbitmqctl change_password 'netmind' 'NetMind@2022'
# Logs
tail -f /var/log/rabbitmq/rabbit.log

# Launch
systemctl start rabbitmq-server

#expose the 5679 port

ngrok tcp 5672 > /dev/null &
```

The log file will show the following:

```bash

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

## Redis

Redis is a key store that is used to store the tasks results returned by the celery workers (installed on node2).

```jsx
# Redis installation
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg

echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

sudo apt-get update
sudo apt-get install redis

# test your installation
redis-cli ping

# expose the TCP port with ngrok
ngrok tcp 6379 > /dev/null &

# launch Redis
redis-server --daemonize yes
```

The log file will show:

```bash

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
```

## Celery workers

The steps below are for the machines that are assigned to run celery workers (node3/4):

```jsx
# Verify NVIDIA installation and CUDA version by running the following:
nvidia-smi

# Cuda support
conda install pytorch torchvision torchaudio cudatoolkit=11.6 -c pytorch -c conda-forge

# deploy netmind (this does not include the model large files that have to be downloaded from AWS repository)
git clone git@github.com:santamm/netmind-inference.git

# REPEAT FOR ALL MODELS!!
# download model large file from AWS repository
cd netmind-inference/celery_tasks/ml_models/protago-codegen
# this is for code generation model
aws s3 cp s3://gpt-genji/gptj/saved_model/ ./saved_model --recursive
```

For each model deployed make sure their additional requirements are installed:

```jsx
cd netmind-inference/celery_tasks/ml_models/model-1
pip install -r requirements.txt
```

If the models requires different versions of any python package to run (for example different transformers), you will have to create separate conda environments for those. One example of this is in the `celery_start.sh` script below:

```bash
#!/bin/bash
ps auxww | grep 'celery_tasks worker' | awk '{print $2}' | xargs kill -9
sleep 2
# Separate GPU workers from CPU workers
# Selecting pre-fork and setting the concurrency level to the number of CPU cores is the best option for CPU bound tasks.
# CPU workers

conda run -n summarize celery -A celery_tasks worker -P eventlet -Q Summarization_cpu -l INFO --detach --logfile celery.log &
celery -A celery_tasks worker -P eventlet -Q Translation_cpu -l INFO --detach --logfile celery.log &
conda run -n codegen celery -A 
celery_tasks worker -P eventlet -Q Generation_cpu -l INFO --detach --logfile celery.log &
# default queue
celery -A celery_tasks worker -P prefork -Q celery -l INFO --detach --logfile celery.log &

# GPU workers if GPU is available
conda run -n summarize celery -A celery_tasks worker -P eventlet -Q Summarization -l INFO --detach --logfile celery.log &
celery -A celery_tasks worker -P eventlet -Q Translation -l INFO --detach --logfile celery.log &
conda run -n codegen celery -A celery_tasks worker -P eventlet -Q Generation -l INFO --detach --logfile celery.log &

# If you need to use different virtual environments, use conda run -n <venv> celery --version
ps -ef | grep celery

tail -f celery.log
```

In the script above you can notice that the *Summarization* and *Generation* tasks are running on separate python virtual environments.

Moreover, it is a good practice to assign different queues/workers to CPU and GPU tasks to avoid models being moved from CPU→GPU and GPU→CPU continously.

## API Server (gunicorn)

We use *gunicorn* as FastAPI server. 

Unicorn is an ASGI web server implementation for Python.

Until recently Python has lacked a minimal low-level server/application interface for async frameworks. The [ASGI specification](https://asgi.readthedocs.io/en/latest/) fills this gap, and means we're now able to start building a common set of tooling usable across all async frameworks.

You can install with the script below:

```bash
sudo apt-get install gunicorn

# if on different mnachine from celery then look at this document on how to run on different machines
# https://medium.com/@tanchinhiong/separating-celery-application-and-worker-in-docker-containers-f70fedb1ba6d
# or this one
# https://groups.google.com/g/celery-users/c/E37wUyOcd3I
pip install celery

# Start
gunicorn app:api -w 1 -k uvicorn.workers.UvicornWorker --daemon --error-logfile gunicorn.err --access-logfile gunicorn.log
```

# Configuration

## Celery workers

The celery configuration is stored in the *[celeryconfig.py](http://celeryconfig.py)* file that is deployed on the celery servers and the api servers (to allow for task dispatching to queues):

```python
# RabbitMQ, use local or global address depending on networking
broker_url = "pyamqp://netmind:netmind@0.tcp.ngrok.io:10567//"
#Redis
result_backend = "redis://6.tcp.ngrok.io:12937"

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
    'celery_tasks.tasks_gpu.ProtagoGenerator': {'queue': 'Generation'},
    'celery_tasks.tasks_cpu.AndreaSummarize': {'queue': 'Summarization_cpu'},
    'celery_tasks.tasks_cpu.ProtagoTranslator': {'queue': 'Translation_cpu'},
    'celery_tasks.tasks_cpu.ProtagoGenerator': {'queue': 'Generation_cpu'}
  #  'celery_tasks.tasks_cpu.*': {'queue': 'celery'}
}
```

### Typical Project Structure

A sample of a project deployment is depicted below:

```jsx
netmind_inference
│
├───celery_tasks
│   │   tasks_cpu.py
│   │   tasks_gpu.py
│   │   celery.py
│   │   celeryconfig.py
│   │   __init__.py
│   │
│   ├───ml_models
│   │   ├─── model-1
|   |   |   | model.py
|   |   |   | pytorch_model.bin
|   |   |   | .... 
│   │   ├─── model-2
|   |   |   . . . . . 
|   │   ├─── model-n
|   |   |   . . . . . 
```

- *celery_tasks/tasks_cpu.py:*  celery task definitions, sassigned to execution on cpu
- *celery_tasks/tasks_cpu.py: c*elery task definitions, assigned to execution on gpu
- *celery_tasks/celery.py:* Defines the celery app instance and loads the config.
- *celery_tasks/celeryconfig.py:* configuration file for queues/tasks, message broker and results store
- *celery_tasks/ml_models/<model-x>/model.py:* Machine learning models wrapper classese used to load pretrained models and serve predictions.
- *celery_tasks/ml_models/<model-x>/pytorch_model.bin:* Machine learning pre-trained file (can be different format)

## FastAPI

We use FastAPI to send requests to execute a task (assuming we know the task name exposed in the *tasks_gpu.py or tasks_cpu.py* files). The following snipped is included in the *[app.py](http://app.py)* file that defines the FastAPI interface: 

```bash
app = Celery()
app.config_from_object('celeryconfig')
api = FastAPI()

class Payload(BaseModel):
  """ Features for prediction """
  data: str
  device: str

@api.post('/protago_translate/predict', response_model=Task, status_code=202)
async def translate(payload: Payload):
    """Create celery prediction task. Return task_id to client in order to retrieve result"""
    print(f"Requested summarization on {payload.device}")
    if payload.device=='GPU':
      task_id = app.send_task('celery_tasks.tasks_gpu.ProtagoTranslator', [payload.data])
    else:
      task_id = app.send_task('celery_tasks.tasks_cpu.ProtagoTranslator', [payload.data])
    print(f"Task id: {task_id}")
    return {'task_id': str(task_id), 'status': 'Processing'}
```

The results for the submitted task can then be retrieved asynchronously with the following code, assuming we know the *task_id* generated when the request was submitted:

```python
class TextGeneration(BaseModel):
    """ Prediction task result """
    task_id: str
    status: str
    result: str

@api.get('/protago_translate/result/{task_id}', response_model=TextGeneration, status_code=200, 
  responses={202: {'model': Task, 'description': 'Accepted: Not Ready'}})
async def translate_result(task_id: str):
    """Fetch result for given task_id"""
    print(f"Fetching result for {task_id}....")
    task = AsyncResult(task_id)
    if not task.ready():
      return JSONResponse(status_code=202, content={'task_id': str(task_id), 'status': 'Processing'})
    result = task.get()
    return {'task_id': task_id, 'status': 'Success', 'result': str(result)}
```

## Users API to run prediction tasks

The first part is choosing which model to run:

```python
ENDPOINT = https://api-inference.netmind.com/models/<MODEL_ID>
```

Below an example of Python code to run to submit a task:

and retrieve results:

# Further Developments

## API Keys

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

## Scaling further using Kubernetes

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

[*Celery - Distributed Task Queue](https://docs.celeryq.dev/en/stable/).*

[*RabbitMQ is the most widely deployed open source message broker](https://www.rabbitmq.com/).*

[*Serving ML Models in Production with FastAPI and Celery](https://towardsdatascience.com/deploying-ml-models-in-production-with-fastapi-and-celery-7063e539a5db).*

[*Scaling Celery workers with RabbitMQ on Kubernetes](https://learnk8s.io/scaling-celery-rabbitmq-kubernetes).*

[*Redis: a vibrant, open source database.*](https://redis.io/)

*[Kubernetes Event-driven Autoscaling](https://keda.sh/).*

[*Scaling Celery - Sending Tasks To Remote Machines*](https://avilpage.com/2014/11/scaling-celery-sending-tasks-to-remote.html#)

[*Flower: Real-time Celery web-monitor*](https://docs.celeryq.dev/en/stable/userguide/monitoring.html#id8)

*[Separating Celery application and worker in Docker containers](https://medium.com/@tanchinhiong/separating-celery-application-and-worker-in-docker-containers-f70fedb1ba6d)*

*[An ASGI web server, for Python.](https://www.uvicorn.org/)*

*[Use of Celery in Serverless systems for scaling AI workloads](https://ignitarium.com/use-of-celery-in-serverless-systems-forscaling-ai-workloads/)*
