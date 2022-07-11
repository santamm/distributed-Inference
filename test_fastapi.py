import requests
from time import sleep


test_body = {"data":"I have been waiting for netmind.ai my whole life"}

def dummy_task(data, poll_interval=1, max_attempts=5):
    # submit request
    base_uri = r'http://127.0.0.1:8000'
    predict_task_uri = base_uri + '/summarize/predict'
    task = requests.post(predict_task_uri, json=data)
    print(task.json())
    task_id = task.json()['task_id']


    predict_result_uri = base_uri + '/summarize/result/' + task_id
    attempts = 0
    result = None
    while attempts < max_attempts:
        attempts += 1
        print(f"Retrieving results for {predict_result_uri}")
        result_response = requests.get(predict_result_uri)
        #print(result_response)
        if result_response.status_code == 200:
            result = result_response.json()
            break
        sleep(poll_interval)
    return result


if __name__ == '__main__':
    prediction = dummy_task(test_body)
    print(prediction)