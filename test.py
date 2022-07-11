import time
from hf_model.tasks import predict

result = predict.delay("I have been waiting for a fast.ai course my whole life")
# wait a bit
time.sleep(10)
# check if ready 
if result.ready():
  print("Result is ready:")
  print(result.get(timeout=1))
else:
  print("Result is not ready)")


