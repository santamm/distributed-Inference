import time
from hf_model.tasks import predict

for i in range(10):
  time.sleep(0.01)
  predict.delay("I have been waiting for a fast.ai course my whole life")
  # wait a bit
# check if ready 
#if result.ready():
#  print("Result is ready:")
#  print(result.get(timeout=1))
#else:
#  print("Result is not ready)")