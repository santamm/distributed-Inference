from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from pathlib import Path
import os


class ProtagoGenerator:

    def __init__(self, device=-1):
        self.tokenizer = AutoTokenizer.from_pretrained(os.path.dirname(__file__)+"/saved_model")
        self.model = AutoModelForCausalLM.from_pretrained(os.path.dirname(__file__)+"/saved_model")
        if device>=0:
            self.device = torch.device(f'cuda:{device}')
            self.model.to(self.device)
            self.model.half()
        else:
            self.device = 'cpu'
        self.model.eval()
        self.maxLength = 200  # @param {type:"number"}
        self.temperature = 0.4  # @param {type:"number"}
        self.top_k = 50  # @param {type:"number"}
        self.top_p = 0.9  # @param {type:"number"}
        self.repetition_penalty = 1.13  # @param {type:"number"}
        self.repetition_penalty_range = 512  # @param {type:"number"}
        self.repetition_penalty_slope = 3.33  # @param {type:"number"}

    def gene(self, text):
        print('Code Input: {}'.format(text))
        tokens = self.tokenizer(text, return_tensors="pt").input_ids.long()
        tokens.to(self.device)
        generated_tokens = self.model.generate(tokens, use_cache=True, do_sample=True, top_k=50,
                                               temperature=0.3, top_p=0.9, repetition_penalty=1.125, min_length=1,
                                               max_length=len(tokens[0]) + 400,
                                               pad_token_id=self.tokenizer.eos_token_id)
        last_tokens = generated_tokens[0]
        generated_text = self.tokenizer.decode(last_tokens[:-1],skip_special_tokens=True)
        print('Code Output: {}'.format(generated_text))
        return generated_text

    def genFunction(self, text):
        print('Code Input: {}'.format(text))
        tokens = self.tokenizer(text, return_tensors='pt').input_ids.long()
        tokens.to(self.device)
        generated_tokens = self.model.generate(tokens, use_cache=True, do_sample=True, top_k=50,
                                               temperature=0.3, top_p=0.9, repetition_penalty=1.125, min_length=1,
                                               max_length=len(tokens[0]) + 400,
                                               pad_token_id=self.tokenizer.eos_token_id)
        last_tokens = generated_tokens[0]
        gene = self.tokenizer.decode(last_tokens[tokens.shape[1]:],skip_special_tokens=True)
        generated_text = text + gene.split('\n\n\n')[0]
        print('Code Output: {}'.format(generated_text))
        return generated_text

    def genLines(self, text):
        print('Code Input: {}'.format(text))
        tokens = self.tokenizer(text, return_tensors='pt').input_ids.long()
        tokens.to(self.device)
        generated_tokens = self.model.generate(tokens, use_cache=True, do_sample=True, top_k=50,
                                               temperature=0.3, top_p=0.9, repetition_penalty=1.125, min_length=1,
                                               max_length=len(tokens[0]) + 400,
                                               pad_token_id=self.tokenizer.eos_token_id)
        last_tokens = generated_tokens[0]
        gene = self.tokenizer.decode(last_tokens[tokens.shape[1]:],skip_special_tokens=True)
        generated_text = text + '\n'.join(gene.split('\n')[0: 3])
        print('Code Output: {}'.format(generated_text))
        return generated_text


#code_generator = Generator()