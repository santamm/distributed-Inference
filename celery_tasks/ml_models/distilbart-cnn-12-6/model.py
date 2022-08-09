import joblib
import os
from pathlib import Path
import logging
import json
import torch


from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
model_checkpoint = "facebook/bart-large-cnn"


with open(Path(os.path.dirname(__file__))/"model.json") as model_config:
        model_dict = json.load(model_config)


#MODEL = model_dict['model_file_name']
#MODEL_PATH = Path(os.path.dirname(__file__))/MODEL

class DistilBartSummarize:

    """ Wrapper for loading and serving pre-trained model"""

    def __init__(self):
        self.model, self.tokenizer = self._load_model_from_path(model_checkpoint)
        self.device = None

    @staticmethod
    def _load_model_from_path(path):
        logging.info("Loading model checkpoint "+model_checkpoint)
        tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
        model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)
        
        #generator = pipeline(task="summarization", model=model, tokenizer=tokenizer)
        #model = pipeline("summarization", model=model_checkpoint)
        return model, tokenizer

    def predict(self, inputs):
        """
        
        """
        #prediction = self.model(data, max_length=130, min_length=30, do_sample=False)
        
        #inputs = self.tokenizer(data, max_length=1024, return_tensors="pt")
        #if device:
        #    print(f"Moving inputs to GPU: {device}")
        #    inputs.to(device)
        #summary_ids = self.model.generate(inputs["input_ids"], num_beams=2, min_length=0, max_length=64)
        summary_ids = self.model.generate(inputs, num_beams=2, min_length=0, max_length=64)
        summary = self.tokenizer.batch_decode(summary_ids, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]

        return summary
