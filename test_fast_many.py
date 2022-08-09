import requests
import time

base_uri = r'http://127.0.0.1:8000'
#base_uri = 'https://40d9220970b5.ngrok.io'

ARTICLE = """ New York (CNN)When Liana Barrientos was 23 years old, she got married in Westchester County, New York.
A year later, she got married again in Westchester County, but to a different man and without divorcing her first husband.
Only 18 days after that marriage, she got hitched yet again. Then, Barrientos declared "I do" five more times, sometimes only within two weeks of each other.
In 2010, she married once more, this time in the Bronx. In an application for a marriage license, she stated it was her "first and only" marriage.
Barrientos, now 39, is facing two criminal counts of "offering a false instrument for filing in the first degree," referring to her false statements on the
2010 marriage license application, according to court documents.
Prosecutors said the marriages were part of an immigration scam.
On Friday, she pleaded not guilty at State Supreme Court in the Bronx, according to her attorney, Christopher Wright, who declined to comment further.
After leaving court, Barrientos was arrested and charged with theft of service and criminal trespass for allegedly sneaking into the New York subway through an emergency exit, said Detective
Annette Markowski, a police spokeswoman. In total, Barrientos has been married 10 times, with nine of her marriages occurring between 1999 and 2002.
All occurred either in Westchester County, Long Island, New Jersey or the Bronx. She is believed to still be married to four men, and at one time, she was married to eight men at once, prosecutors say.
Prosecutors said the immigration scam involved some of her husbands, who filed for permanent residence status shortly after the marriages.
Any divorces happened only after such filings were approved. It was unclear whether any of the men will be prosecuted.
The case was referred to the Bronx District Attorney\'s Office by Immigration and Customs Enforcement and the Department of Homeland Security\'s
Investigation Division. Seven of the men are from so-called "red-flagged" countries, including Egypt, Turkey, Georgia, Pakistan and Mali.
Her eighth husband, Rashid Rajput, was deported in 2006 to his native Pakistan after an investigation by the Joint Terrorism Task Force.
If convicted, Barrientos faces up to four years in prison.  Her next court appearance is scheduled for May 18.
"""

test_body = {"data":ARTICLE}


def submit_testbed(data):
  """"
  
  """
  predict_task_uri = base_uri + '/summarize/predict'
  task = requests.post(predict_task_uri, json=data)
  print(f"Submitted task: {task.json()['task_id']}")
  time.sleep(30)

  
  for i in range(10):
    time.sleep(0.1)
    task = requests.post(predict_task_uri, json=data)
    print(f"Submitted task: {task.json()['task_id']}")





def dummy_task(data, poll_interval=1, max_attempts=5):
    # submit request
    
    predict_task_uri = base_uri + '/summarize/predict'
    task = requests.post(predict_task_uri, json=data)
    print(f"Submitted task: {task.json()['task_id']}")
    task_id = task.json()['task_id']


    predict_result_uri = base_uri + '/summarize/result/' + task_id
    attempts = 0
    result = None
    while attempts < max_attempts:
        attempts += 1
        print(f"Retrieving results for {predict_result_uri}... ", end='')
        result_response = requests.get(predict_result_uri)
        print(result_response)
        if result_response.status_code == 200:
            print("reply retrieved: ")
            result = result_response.json()
            break
        print("no luck.")
        sleep(poll_interval)
    return result


if __name__ == '__main__':
    submit_testbed(test_body)