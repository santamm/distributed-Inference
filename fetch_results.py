import redis
import optparse


#r = redis.Redis(host='6.tcp.ngrok.io', port=12937, db=0)

r = redis.Redis(host='127.0.0.1', port=6379, db=0)

def fech_task_result(taskid):
  """
  
  """
 
  result = r.get(taskid)
  if result:
    print(f"Result for task {taskid}: {result}")
  else:
    print("No result")


def fetch_all():
  for key in r.scan_iter():
    print(key, r.get(key))


if __name__ == '__main__':
  """
  Fetch results from Redis Server
  """
 
  #argv = sys.argv[1:] 
  #kwargs = {kw[0]:kw[1] for kw in [ar.split('=') for ar in argv if ar.find('=')>0]}
  #args = [arg for arg in argv if arg.find('=')<0]
  parser = optparse.OptionParser()
  parser.add_option('--task', '-t', action="store", dest='taskid')
  parser.add_option('--all', '-a', action="store_true", default=False, dest='all', help="Show all tasks")
  (options, args) = parser.parse_args()

  #a_device_var=kwargs.get('device',False)
  #print(args)
  #print(options)

  if options.taskid:
    result = fech_task_result("celery-task-meta-"+options.taskid)
  elif options.all:
    fetch_all()


