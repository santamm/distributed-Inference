import requests
from time import sleep

INPUT_TEXT = """
Earlier this week, the Conservative party raised money by auctioning off the chance for a supporter to have supper with Boris Johnson, Theresa May and David Cameron.
David CAMERON: (Silence)
Boris JOHNSON: (Silence)
Theresa MAY: (Silence)
CAMERON: Um ...
JOHNSON: Er ...
MAY: (Silence)
DONOR: This is fun ...
CAMERON: Yes ...
MAY: Is it?
JOHNSON: Shall we order some more wine?
MAY: Just try not to spill it this time.
CAMERON: So what inspired you to pay £120k for dinner?
DONOR: I was actually the underbidder. The woman who pledged the most said she’d pay almost anything not to have dinner with you. But since I’m here, I’d quite fancy a place in the Lords.
JOHNSON: Consider it done. Now when do I get my cut?
DONOR: Sorry?
JOHNSON: The £60k for talking to you lot...
CAMERON: I think you’ll find it was a donation to the Conservative party.
JOHNSON: Oh. I’d never have offered if I’d known.
DONOR: But can I still have a peerage?
JOHNSON: Let’s talk later. In private.
CAMERON: (Silence)
JOHNSON: (Silence)
MAY: (Silence)
CAMERON: Tiverton is nice this time of year.
JOHNSON: Why are you bringing up Tiverton?
CAMERON: No reason... Sam and I just happened to be driving through the area on the way to stay with Hugo and Sasha Swire. Do you know the Swires?
MAY: No.
CAMERON: Hugo was a junior minister in the Foreign Office when you were home secretary ...
MAY: (Silence)
DONOR: So ... how do you all think Brexit is going?
CAMERON: (Silence)
MAY: (Silence)
JOHNSON: Marvellously. Never better. The UK is booming. Bozza Builds Back Better.
CAMERON: As in the economy is taking a 4% hit to GDP during a cost of living crisis.
JOHNSON: Stop talking Britain down, Dave. Jacob Rees-Mogg is getting rid of a European law that would force the UK to have the same phone chargers as other EU countries. So now we’ll have to buy a different one whenever we go abroad. That’s what I mean when I say I’m “getting Brexit done”.
CAMERON: Admit it, Boris. Being prime minister is a lot harder work than you expected ...
JOHNSON: It’s certainly very badly paid. I’ve never been so broke in my life. I used to get £275k per year for churning out any old bobbins for the Telegraph. Now I actually have to do a full day’s work. And I only earn about £150k.
CAMERON: Though you do have Lord Brownlow to pick up the tab for soft furnishings and other living expenses. By the way, well done for getting rid of Lord Geidt. He did rather hamper your style ...
JOHNSON: Well, there’s no point in having an ethics adviser if you don’t have any ethics ... Anyway, tell me. How much do you both pull in as former prime ministers?
CAMERON: Well, most of the time life is fairly dull. I just sit in my shepherd’s hut waiting for the phone to ring. But it seldom does. No one really wants to hear what I’ve got to say about anything any more ...
DONOR: I know what you mean ...
CAMERON: Still, I did get £800k for my really boring memoir. You should get a lot more if you publish your diaries about how you stabbed me in the back ...
JOHNSON: You’re not still bitter about that are you? It’s your own fault. If you hadn’t been so lazy and slapdash you’d never have lost the referendum. And besides, I betray everyone. That’s what I do. Just ask Marina and all the other women ...
MAY: I’m earning a fortune.
JOHNSON: WTF?
CAMERON: WTF?
MAY: I’m inundated with offers to give speeches ...
JOHNSON: People pay you to speak?
MAY: Yes. Well over £100k for little more than 30 minutes ...
JOHNSON: I’m amazed.
MAY: Yes, people are still interested in the Malthouse compromise ...
CAMERON: I suppose it was no more idiotic than the Northern Ireland protocol. After all Boris went to all the trouble of negotiating a Brexit deal only to have to renege on his own treaty and is now having to renegotiate from scratch. Good luck with that.
JOHNSON: (Silence)
CAMERON: (Silence)
MAY: (Silence)
DONOR: So ...
CAMERON: So ...
MAY: Geoffrey Boycott.
CAMERON: What about him?
MAY: He was a great cricketer. I once saw him make 17 between lunch and tea in a Test against Pakistan at Lords.
CAMERON: And?
MAY: And nothing. That was it. Geoffrey Boycott.
DONOR: OK ... Then how do you think you’ll all be remembered?
CAMERON: I hope history will be kind. It’s not my fault I took my eye off the ball. Don’t forget I was prime minister for a lot longer than Theresa. And almost certainly Boris as well. Plus I did get a better degree at Oxford than Boris ...
JOHNSON: That’s because you were a girly swot. I will definitely go down as one of the all time greats. The first prime minister who picked up a criminal record. If only Sue Gray and the Met had managed to find out what we really got up toin No 10! The prime minister who stoked division and failed to level up the country. The man who put a smile on refugee faces with his world-leading Rwanda plan ...
MAY: Well I want it on record that I was a lot more popular than Boris. I won my no-confidence vote by a higher percentage of votes than he did.
JOHNSON: But I am going to hang on ...
MAY: Not if I have anything to do with it.
CAMERON: Now, now.
JOHNSON: (Silence)
MAY: (Silence)
CAMERON: (Silence)
"""


test_body = {"data":INPUT_TEXT}

def dummy_task(data, poll_interval=1, max_attempts=5):
    # submit request
    base_uri = r'http://127.0.0.1:8000'
    predict_task_uri = base_uri + '/andrea/predict'
    task = requests.post(predict_task_uri, json=data)
    print(f"Submitted task: {task.json()['task_id']}")
    task_id = task.json()['task_id']


    predict_result_uri = base_uri + '/andrea/result/' + task_id
    attempts = 0
    result = None
    while attempts < max_attempts:
        attempts += 1
        print(f"Retrieving results for {predict_result_uri}... ", end='')
        result_response = requests.get(predict_result_uri)
        #print(result_response)
        if result_response.status_code == 200:
            print("reply retrieved: ")
            result = result_response.json()
            break
        print("no luck.")
        sleep(poll_interval)
    return result


if __name__ == '__main__':
    prediction = dummy_task(test_body, poll_interval=5)
    print(prediction)