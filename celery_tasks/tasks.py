from celery import Task
import logging
import os

import joblib
import importlib
import base64
from PIL import Image
import io



from .celery import app

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
          path=('celery_tasks.ml_models.summarize_python_codet5_base.model', 'Codet5Summarize'),
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








