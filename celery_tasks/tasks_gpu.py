from celery import Task
import torch
import numpy as np
import logging
import importlib
#import base64
import pynvml

from .celery import app


# Cuda free memory

def get_memory_free_MiB(gpu_index):
    pynvml.nvmlInit()
    handle = pynvml.nvmlDeviceGetHandleByIndex(int(gpu_index))
    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
    return mem_info.free // 1024 ** 2


def get_device():
    """
    Returns a GPU to run the model on
    Returns the index the GPU (index) with most memory available, -1 if no GPU is available
    """
    # np.argmin(torch.cuda.max_memory_allocated(device=device)/1e9 for device in range(torch.cuda.device_count())) if torch.cuda.is_available() else -1
    n_gpu = torch.cuda.device_count()
    if n_gpu>0:
        return np.argmax([get_memory_free_MiB(device) for device in range(n_gpu)])
    else:
        return -1 # no GPU available
    

class AndreaSummarizePredictTask_GPU(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.

    """
    
    abstract = True

    def __init__(self):
        super().__init__()
        #self.tokenizer = None
        self.model = None
        self.device = -1 # device where the model is running (-1 for cpu, or GPU index)

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        
        device = get_device()
        if device==-1:
            return "GPU Not available. Please try to run on CPU."

        if not self.model:
            logging.info('Loading Model...')
            module_import = importlib.import_module(self.path[0])
            model_obj = getattr(module_import, self.path[1])
            self.model = model_obj(device)
            self.device = device
            logging.info(f'Model loaded on device {device}')
        return self.run(*args, **kwargs)

# use a different task for each model to prevent a task to load different models in memory
@app.task(ignore_result=False,
          bind=True,
          base=AndreaSummarizePredictTask_GPU,
          #path=('celery_tasks/ml_models/andrea-summarization', 'andrea-summarization.z'),
          path=('celery_tasks.ml_models.andrea-summarization.model', 'AndreaSummarize'),
          name='{}.{}'.format(__name__, 'AndreaSummarize')
          )
def andrea_summarize_predict(self, data):
    """
    Essentially run method of PredictTask
    data: text to translate
    on_device: run model on device , can be 'CPU' or 'GPU'
    """
    summary = self.model.predict(data)
    return summary

class ProtagoTranslatorTask_GPU(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.

    """
    
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None
        self.device = -1

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        device = get_device()
        if device==-1:
            return "GPU Not available. Please try to run on CPU."

        if not self.model:
            logging.info('Loading Model...')
            module_import = importlib.import_module(self.path[0])
            model_obj = getattr(module_import, self.path[1])
            self.model = model_obj(device)
            self.device = device
            #print(f"Requested on {device_requested}")
            # this object should be loaded to GPU if available
            #device = "cuda:0" if torch.cuda.is_available() else "cpu"
            print(f"Model {type(self.model).__name__} loaded on device {device}.")
            #print(f"Model: {type(self.model.model).__name__}, Tokenizer: {type(self.model.tokenizer).__name__}")
            #if (torch.cuda.device_count()>0) and device_requested=='GPU':
            #    self.device = get_device()
            #    print(f"Moving model to GPU: {self.device}")
            #    self.model.model.to(self.device) 
            #    self.model.tokenizer.to('cuda:0') 

        return self.run(*args, **kwargs)
# use a different task for each model to prevent a task to load different models in memory
@app.task(ignore_result=False,
          bind=True,
          base=ProtagoTranslatorTask_GPU,
          path=('celery_tasks.ml_models.protago-translator.model', 'ProtagoTranslator'),
          name='{}.{}'.format(__name__, 'ProtagoTranslator')
          )
def protago_translate(self, data):
    """
    Essentially run method of PredictTask
    """
    result = self.model.gene(data)

    return result


class ProtagoGeneratorTask_GPU(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.

    """
    
    abstract = True

    def __init__(self):
        super().__init__()
        self.model = None
        self.device = -1

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        device = get_device()
        if device==-1:
            return "GPU Not available. Please try to run on CPU."
        if not self.model:
            logging.info('Loading Model...')
            module_import = importlib.import_module(self.path[0])
            model_obj = getattr(module_import, self.path[1])
            self.model = model_obj(device)
            self.device = device
            #print(f"Requested on {device_requested}")
            # this object should be loaded to GPU if available
            #device = "cuda:0" if torch.cuda.is_available() else "cpu"
            print(f"Model {type(self.model).__name__} loaded on device 'cuda:{device}'.")
            #print(f"Model: {type(self.model.model).__name__}, Tokenizer: {type(self.model.tokenizer).__name__}")
            #if (torch.cuda.device_count()>0) and device_requested=='GPU':
            #    self.device = get_device()
            #    print(f"Moving model to GPU: {self.device}")
            #    self.model.model.to(self.device) 
            #    self.model.tokenizer.to('cuda:0') 

        return self.run(*args, **kwargs)
# use a different task for each model to prevent a task to load different models in memory
@app.task(ignore_result=False,
          bind=True,
          base=ProtagoTranslatorTask_GPU,
          path=('celery_tasks.ml_models.protago-codegen.model', 'ProtagoGenerator'),
          name='{}.{}'.format(__name__, 'ProtagoGenerator')
          )
def protago_generate(self, data, filling_method):
    """
    Essentially run method of PredictTask
    """

    #inputs = self.model.tokenizer(data, max_length=1024, return_tensors="pt")
    #if self.device:
    #        print(f"Moving inputs to GPU: {self.device}")
    #        inputs.to(self.device)
    #data = inputs['input_ids']
    if filling_method=='Function':
        print("Generating Function...")
        result = self.model.genFunction(data)
    if filling_method=='Two Lines':
        print("Generating Two Lines...")
        result = self.model.genLines(data)
    else:
        result = self.model.gene(data)

    return result


