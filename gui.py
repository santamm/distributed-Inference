import numpy as np
import gradio as gr
import requests
import time
import os
from functools import partial


#api_uri = os.environ["API_URI"]
api_uri= "http://127.0.0.1:8000" 

demo = gr.Blocks()


translate_uri = '/protago_translate/predict'
translate_results_uri = '/protago_translate/result/'


summarize_uri = '/andrea/predict'
summarize_results_uri = '/andrea/result/'
summarize_description = """
The following model is an abstractive summarization model trained on the SummScreen ForeverDreaming dataset, consisting of community generated transcripts of many different genres of TV shows, matched with their respecrtive summaries taken from Wikipedia and TVMaze. This specific model was fine-tuned starting from checkpoints of a BART summarization model trained on the CNN/DailyMail dataset available on HuggingFace. The input sequence is 1024 and the output sequence 384. For each input transcript, we performed content selection on the input sequence based on the LexRank algorithm (with threshold 0.1) applied to the similarity matrix for all sentences in the transcript calculated using a SentenceBERT model multi-purpose model. The highest scoring sentences extracted in this way have been retained for each input transcript up to 1024 tokens, and then fed into the model for fine-tuning on abstractive summarization.
"""


generate_uri = '/protago_generate/predict'
generate_results_uri = '/protago_generate/result/'
generate_description = """
Netmind Easy Coding” api powered by Genji-python, a GPT-j-6b model trained on Pile Corpus.<br>
“Netmind Easy Coding” understands context include function name, comments, and code itself. It synthesizes code to match the given the context. Note that PolyCoder passes 17.68% test cases in HumanEval benchmark with 100 repetitions. When playing with our api, you may need to repeat several times before geting the right answer.
"""

_text1 = """Hong Kong (CNN)Hong Kong has recorded its sharpest annual drop in population, with experts blaming the decline on strict Covid control measures and a political crackdown that have taken the shine off a financial hub long advertised as "Asia's world city."
The city's total population fell from 7.41 million people to 7.29 million, a 1.6% decrease, the Census and Statistics Department said Thursday.
That's the steepest decline since the government began tracking figures in 1961.
Though authorities attributed some of that to a "natural" decrease -- more deaths than births -- experts said the figures also reflected an exodus that has accelerated in the past few years amid periods of massive social upheaval that have included anti-government protests and the coronavirus pandemic.
Around 113,200 residents left Hong Kong over the past year, the department said, compared to 89,200 the year before. The figures include expatriates and other non-permanent residents.
"""
_text2 = "Your name is Maurizio"

_func1 = "def HelloWorld():"
_func2 = "def print_customer_name():"



def submit_task(submit_uri, payload):
  """
  payload is a dictionary and may include:
    device
    data
    other attributes required by the inference 
  """
  #print(f"Submitting task on device {device}")
  #payload = {"data":text, "device":device}
  #payload = {"data":text, "device":device}
  predict_task_uri = api_uri + submit_uri
  task = requests.post(predict_task_uri, json=payload)
  #print(f"Submitted task: {task.json()['task_id']}")
  task_id = task.json()['task_id']

  return task_id

def retrieve_task_results(retrieve_uri, taskid):
  """
  """

  predict_result_uri = api_uri + retrieve_uri + taskid
  response = requests.get(predict_result_uri)
  if response.status_code == 200:
    result = response.json()
    status = result['status']
    reply_text = result['result']
  else:
    reply_text = "No luck."
    status = "Failed"
  return status, reply_text


def submit_interactive(submit_uri, retrieve_uri, payload, poll_interval=1, max_attempts=60):
  """
  

  payload is a tuple and may include
    device
    data
    other attributes required by the inference 
  """
  start = time.time()
  print(f"Submitting: {submit_uri}")
  taskid = submit_task(submit_uri, payload)
  attempts = 0
  result = None
  print(f"Retrieving: {retrieve_uri}")
  while attempts < max_attempts:
    attempts += 1
    status, result = retrieve_task_results(retrieve_uri, taskid)
    if status=='Success':
      elapsed = f"Inference time: {(time.time()-start):.4} secs."
      return status, result, elapsed
    time.sleep(poll_interval)
  return "Failed", "Response timeout", ""



def translate(data, device='cpu'):
  """
  
  """
  payload = {'data':data, 'device':device}
  return submit_interactive(translate_uri, translate_results_uri, payload)

def summarize(data, device='cpu'):
  """
  
  """
  payload = {'data':data, 'device':device}
  return submit_interactive(summarize_uri, summarize_results_uri, payload)

def generate(data, filling_method, device='gpu'):
  """
  """
  payload = {'data':data, 'device':device, 'filling_method':filling_method}
  return submit_interactive(generate_uri, generate_results_uri, payload, poll_interval=5, max_attempts=60)


#summarize = partial(submit_interactve, '/andrea/predict', '/andrea/result/')
#generate = partial(submit_interactive, '/protago_generate/predict', '/protago_generate/result/')

def change_textbox(choice):
    if choice == "Example 1":
        return gr.Textbox.update(value=_text1)
    else:
        return gr.Textbox.update(visible=False)

def change_function(choice):
    if choice == "Function 1":
        return gr.Textbox.update(value=_func1)
    if choice == "Function 2":
        return gr.Textbox.update(value=_func2)    
    else:
        return gr.Textbox.update(visible=False)


with demo:
    gr.Markdown("<h1>NetMind.AI Demo.</h1>")
    with gr.Tabs():
        with gr.TabItem("Machine Translation (En -> Zh)"):
            with gr.Row():
                with gr.Column():
                  tr_device = gr.Radio(('CPU', 'GPU'), label='Device')
                  tr_examples = gr.Dropdown(choices=['Example 1'], label="Choose an example or paste your text")
                  translate_input = gr.Textbox(lines=20, interactive=True)
                #gr.example
                with gr.Column():
                  translate_output = [gr.Textbox(label='Status'), gr.Textbox(label='Translation', lines=20), gr.HTML()]
            translate_button = gr.Button("Translate")

        with gr.TabItem("Summarization"):
          with gr.Column():
            gr.Markdown(f"<h3>Model Description</h3>{summarize_description}")
            with gr.Row():
                with gr.Column():
                  sum_device = gr.Radio(('CPU', 'GPU'), label='Device')
                  sum_examples = gr.Dropdown(choices=['Example 1'], label="Choose an example or paste your text")
                  summarize_input = gr.Textbox(lines=20, interactive=True)
                with gr.Column():
                  summarize_output = [gr.Textbox(label='Status'), gr.Textbox(label='Summary', lines=5), gr.HTML()]
            summarize_button = gr.Button("Summarize")

        with gr.TabItem("Code Generation"):
          with gr.Column():
            gr.Markdown(f"<h3>Model Description</h3>{generate_description}")
            with gr.Row():
                with gr.Column():
                  gen_device = gr.Radio(('CPU', 'GPU'), label='Device')
                  gen_examples = gr.Dropdown(choices=['Function 1', 'Function 2'], label="Choose an example or paste your text")
                  filling_method = gr.Radio(choices=['Two Lines', 'Function'], label="Filling Method")
                  code_input = gr.Textbox(lines=20, interactive=True)
                with gr.Column():
                  generate_output = [gr.Textbox(label='Status'), gr.Textbox(label='Generated Code', lines=20), gr.HTML()]
            generate_button = gr.Button("Generate Code")

    tr_examples.change(fn=change_textbox, inputs=tr_examples, outputs=translate_input)
    sum_examples.change(fn=change_textbox, inputs=sum_examples, outputs=summarize_input)
    gen_examples.change(fn=change_function, inputs=gen_examples, outputs=code_input)

    translate_button.click(translate, inputs=[translate_input, tr_device], outputs=translate_output)
    summarize_button.click(summarize, inputs=[summarize_input, sum_device], outputs=summarize_output)
    generate_button.click(generate, inputs=[code_input, filling_method, gen_device], outputs=generate_output)
 
 
#if __name__=='main':
demo.launch(share=True)






#gr.Interface(
#    fn=submit_interactive,
#    title="Text Summarizer by NetMind",
#    inputs=[gr.Radio(choices=['CPU', 'GPU'], label='Run on:', value='CPU'), 
#            gr.Textbox(lines=20, label="Text")],
#    #inputs=gr.Textbox(lines=20, label="Text"),
#    outputs=[gr.Textbox(label="Status"), gr.Textbox(label="Summary"), gr.HTML()]
#    #live=True
#).launch(share=True)

