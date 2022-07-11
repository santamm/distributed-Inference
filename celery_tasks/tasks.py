from celery import Task
import logging
import os
#from transformers import pipeline
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from .celery import app

# Class to initialize model in memory
class SummarizePredictTask(Task):
    """
    Abstraction of Celery's Task class to support loading ML model.

    """
    
    abstract = True

    def __init__(self):
        super().__init__()
        self.tokenizer = None
        self.model = None

    def __call__(self, *args, **kwargs):
        """
        Load model on first call (i.e. first task processed)
        Avoids the need to load model on each task request
        """
        if not self.model:
            logging.info('Loading Model...')
            #module_import = importlib.import_module(self.path[0])
            #model_obj = getattr(module_import, self.path[1])
            #self.model = model_obj()

            print(f"Current dir: {os.path.abspath(os.getcwd())}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.path[0])
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.path[0])   
            
            logging.info('Model loaded')
        return self.run(*args, **kwargs)



@app.task(ignore_result=False,
          bind=True,
          base=SummarizePredictTask,
          path=('celery_tasks/ml_models/distilbart-cnn-12-6', 'distilbart-cnn-12-6'),
          name='{}.{}'.format(__name__, 'distilbart-cnn-12-6')
          )
def summarize_predict(self, data):
    """
    Essentially run method of PredictTask
    """
    inputs = self.tokenizer([data], max_length=1024, return_tensors="pt")
    summary_ids = self.model.generate(inputs["input_ids"], num_beams=2, min_length=0, max_length=64)
    prediction = self.tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]
    #prediction = self.model(data)
    return prediction
