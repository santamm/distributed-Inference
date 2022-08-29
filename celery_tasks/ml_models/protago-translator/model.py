from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch
from pathlib import Path
import os

class ProtagoTranslator:

    def __init__(self, device=-1):
        
        self.max_input_length = 128
        self.max_target_length = 128
        self.model_name_or_path = os.path.dirname(__file__)+'/m2m'
        #self.device = torch.device('cuda:1' if torch.cuda.is_available() else 'cpu')
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name_or_path)
        if device>=0:
            self.device = torch.device(f'cuda:{device}')
            self.model.to(self.device)
        else:
            self.device = 'cpu'
        self.model.eval()

    def gene(self, text, source='en', target='zh'):
        #print('Trans Input: {} to {}, {}'.format(source, target, text))
        #print(f"Generating translation from {source} to {target}....")
        #print(f"Loading Tokenizer from {self.model_name_or_path}...")
        tokenizer = AutoTokenizer.from_pretrained(self.model_name_or_path, src_lang=source, tgt_lang=target,
                                                  use_fast=True)
        model_inputs = tokenizer(text, max_length=self.max_input_length, truncation=True, padding=True,
                                 return_tensors="pt")
        model_inputs.to(self.device)
        output = self.model.generate(**model_inputs, forced_bos_token_id=tokenizer.get_lang_id(target))
        result = tokenizer.decode(output[0], skip_special_tokens=True)
        print('Trans Output: {}'.format(result))
        return result


#translator = Translator()