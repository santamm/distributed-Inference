import gradio as gr
import requests
import time
import os

#base_uri = os.environ("NETMIND_API_URI")

# uri of the uvicorn/gunicorn ASGI web server
# base_uri = r'http://127.0.0.1:8000'

base_uri = os.environ["API_URI"]

def submit_task(device, text):
  """
  """
  #print(f"Submitting task on device {device}")
  #payload = {"data":text, "device":device}
  payload = {"data":text, "device":device}
  predict_task_uri = base_uri + '/protago_translate/predict'
  task = requests.post(predict_task_uri, json=payload)
  #print(f"Submitted task: {task.json()['task_id']}")
  task_id = task.json()['task_id']

  return task_id



def retrieve_task_results(taskid):
  """
  """

  predict_result_uri = base_uri + '/protago_translate/result/' + taskid
  response = requests.get(predict_result_uri)
  if response.status_code == 200:
    result = response.json()
    status = result['status']
    summary = result['result']
  else:
    summary = "No luck."
    status = "Failed"
  return status, summary


def submit_interactive(device, text, poll_interval=10, max_attempts=6):
  """
  
  """
  start = time.time()
  taskid = submit_task(device, text)
  attempts = 0
  result = None
  while attempts < max_attempts:
    attempts += 1
    status, result = retrieve_task_results(taskid)
    if status=='Success':
      elapsed = f"Inference time: {(time.time()-start):.4} secs."
      return status, result, elapsed
    time.sleep(poll_interval)
  return "Failed", "Response timeout", ""



gr.Interface(
    fn=submit_interactive,
    title="Text Summarizer by NetMind",
    inputs=[gr.Radio(choices=['CPU', 'GPU'], label='Run on:', value='CPU'), 
            gr.Textbox(lines=20, label="Text")],
    #inputs=gr.Textbox(lines=20, label="Text"),
    outputs=[gr.Textbox(label="Status"), gr.Textbox(label="Summary"), gr.HTML()]
    #live=True
).launch(share=True)
