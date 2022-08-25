from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelWithLMHead, pipeline
#import joblib
import os
from pathlib import Path
import logging
import json
import torch

model_checkpoint = "facebook/bart-large-cnn"


#with open(Path(os.path.dirname(__file__))/"model.json") as model_config:
#        model_dict = json.load(model_config)


#MODEL = model_dict['model_file_name']
#MODEL_PATH = Path(os.path.dirname(__file__))/MODEL

class AndreaSummarize:

    """ Wrapper for loading and serving pre-trained model"""

    def __init__(self):
        self.model_name_or_path = os.path.dirname(__file__)
        #print(self.model_name_or_path)
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path)
        
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name_or_path)
        self.model.load_state_dict(torch.load(self.model_name_or_path+"/pytorch_model.bin", map_location='cpu'))
        
        self.device = torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
        self.summarizer = pipeline("summarization", model=self.model, tokenizer=self.tokenizer,
            do_sample=True, no_repeat_ngram_size=3,
            max_length=1024,
            batch_size=1,
            device = 1 if torch.cuda.is_available() else -1  # -1 means running on CPU
            )

    def predict(self, data):
        """
        
        """

        #tokens = self.tokenizer(data, return_tensors='pt', max_length=384, truncation=True, padding='max_length')
        #prediction = self.tokenizer.decode(output[0], skip_special_tokens=True)

        prediction = self.summarizer(data, num_beams=5, truncation=True)
        return prediction

