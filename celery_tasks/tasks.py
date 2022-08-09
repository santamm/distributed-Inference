from celery import Task
import torch
import numpy as np
import logging
import os

import joblib
import importlib
import base64
from PIL import Image
import io
import pynvml


# Cuda free memory
def get_memory_free_MiB(gpu_index):
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(int(gpu_index))
    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    return mem_info.free // 1024 ** 2


def get_device():
    """
    Give a GPU to run the model
    Returns the GPU with most memory available
    """
    n_gpu = torch.cuda.device_count()
    if n_gpu>0:
        return f"cuda:{np.argmin(torch.cuda.max_memory_allocated(device=device)/1e9 for device in range(n_gpu))}"
    else:
        return None
    

from .celery import app

class BartLargeCnnSummarizePredictTask(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.

    """
    
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None
        self.device = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        device_requested = args[1] # can be either 'GPU' or 'CPU'
        if not self.model or (device_requested=='GPU' and self.device is None):
            logging.info('Loading Model...')
            module_import = importlib.import_module(self.path[0])
            model_obj = getattr(module_import, self.path[1])
            self.model = model_obj()
            print(f"Requested on {device_requested}")
            # this object should be loaded to GPU if available
            #device = "cuda:0" if torch.cuda.is_available() else "cpu"
            print(f"Model {type(self.model).__name__} loaded.")
            print(f"Model: {type(self.model.model).__name__}, Tokenizer: {type(self.model.tokenizer).__name__}")
            if (torch.cuda.device_count()>0) and device_requested=='GPU':
                self.device = get_device()
                print(f"Moving model to GPU: {self.device}")
                self.model.model.to(self.device) 
            #    self.model.tokenizer.to('cuda:0') 

        return self.run(*args, **kwargs)
# use a different task for each model to prevent a task to load different models in memory
@app.task(ignore_result=False,
          bind=True,
          base=BartLargeCnnSummarizePredictTask,
          path=('celery_tasks.ml_models.distilbart-cnn-12-6.model', 'DistilBartSummarize'),
          name='{}.{}'.format(__name__, 'DistilBartSummarize')
          )
def distilbart_summarize_predict(self, data, device_request):
    """
    Essentially run method of PredictTask
    """


    inputs = self.model.tokenizer(data, max_length=1024, return_tensors="pt")
    if self.device:
            print(f"Moving inputs to GPU: {self.device}")
            inputs.to(self.device)
    data = inputs['input_ids']        
    summary = self.model.predict(data)


    return summary


class BartLargeCnnSummarizePredictTaskDevice(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.

    """
    
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.model:
            logging.info('Loading Model...')
            module_import = importlib.import_module(self.path[0])
            model_obj = getattr(module_import, self.path[1])
            self.model = model_obj()
            logging.info('Model loaded')
        return self.run(*args, **kwargs)

# use a different task for each model to prevent a task to load different models in memory
@app.task(ignore_result=False,
          bind=True,
          base=BartLargeCnnSummarizePredictTaskDevice,
          path=('celery_tasks.ml_models.distilbart-cnn-12-6.model', 'DistilBartSummarize'),
          name='{}.{}'.format(__name__, 'DistilBartSummarizeDevice')
          )
def distilbart_summarize_predict_device(self, data, device):
    """
    Essentially run method of PredictTask
    """
    
    summary = self.model.predict(data)
    return summary

# Class to initialize model in memory
class Codet5SummarizePredictTask(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.

    """
    
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.model:
            logging.info('Loading Model...')
            module_import = importlib.import_module(self.path[0])
            model_obj = getattr(module_import, self.path[1])
            self.model = model_obj()
            
            logging.info('Model loaded')
        return self.run(*args, **kwargs)

# use a different task for each model to prevent a task to load different models in memory
@app.task(ignore_result=False,
          bind=True,
          base=Codet5SummarizePredictTask,
          path=('celery_tasks.ml_models.codet5-large-ntp-py.model', 'Codet5Summarize'),
          name='{}.{}'.format(__name__, 'distilbart-cnn-12-6')
          )
def codet5_predict(self, data):
    """
    Essentially run method of PredictTask
    """
    summary = self.model.predict(data)
    return summary


# Class to initialize model in memory
class CodeGenPredictTask(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.

    """
    
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.model:
            logging.info('Loading Model...')
            module_import = importlib.import_module(self.path[0])
            model_obj = getattr(module_import, self.path[1])
            self.model = model_obj()
            
            logging.info('Model loaded')
        return self.run(*args, **kwargs)

@app.task(ignore_result=False,
          bind=True,
          base=CodeGenPredictTask,
          path=('celery_tasks.ml_models.codet5-large-ntp-py.model', 'CodeGen'),
          name='{}.{}'.format(__name__, 'codet5-large-ntp-py')
          )
def codegen_generate(self, data):
    """
    Essentially run method of PredictTask
    """

    prediction = self.model.predict(data)
    return prediction


class AndreaSummarizePredictTask(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.

    """
    
    abstract = True

    def __init__(self):
        super().__init__()
        #self.tokenizer = None
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.model:
            logging.info('Loading Model...')
            module_import = importlib.import_module(self.path[0])
            model_obj = getattr(module_import, self.path[1])
            self.model = model_obj()
            logging.info('Model loaded')
        return self.run(*args, **kwargs)

# use a different task for each model to prevent a task to load different models in memory
@app.task(ignore_result=False,
          bind=True,
          base=AndreaSummarizePredictTask,
          #path=('celery_tasks/ml_models/andrea-summarization', 'andrea-summarization.z'),
          path=('celery_tasks.ml_models.andrea-summarization.model', 'AndreaSummarize'),
          name='{}.{}'.format(__name__, 'AndreaSummarize')
          )
def andrea_summarize_predict(self, data):
    """
    Essentially run method of PredictTask
    """
    
    summary = self.model.predict(data)
    return summary



class ShinkaiGANImagePredictTask(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.

    """
    
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.model:
            logging.info('Loading Model...')
            module_import = importlib.import_module(self.path[0])
            model_obj = getattr(module_import, self.path[1])
            self.model = model_obj()
            
            logging.info('Model loaded')
        return self.run(*args, **kwargs)


@app.task(ignore_result=False,
          bind=True,
          base=ShinkaiGANImagePredictTask,
          path=('celery_tasks.ml_models.AnimeBackgroundGAN-Shinkai.model', 'ShinkaiGAN'),
          name='{}.{}'.format(__name__, 'ShinkaiGAN')
          )
def shinkaiGAN_generate(self, data):
    """
    Essentially run method of PredictTask
    data: input tensor
    """
    # Convert image to a string otherwise the celery work won't serialize it
    #img_str = io.BytesIO(base64.b64decode(data))
    image = self.model.inference(data)

    return image








