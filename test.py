import time
from celery_tasks.tasks import andrea_summarize_predict, protago_translate, protago_generate
#from PIL import Image
#i#mport torchvision.transforms as T
import base64


#INPUT_TEXT = "I have been waiting for a fast.ai course my whole life"
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


#IMG = "scarlett.jpeg"

# Celery tasks do not accept images so we need to convert them into tensors

#img = Image.open(IMG)

#with open(IMG, "rb") as image:
#    transform = T.Compose([T.PILToTensor()])
#    pilimage = Image.open(image)
#    tensor = transform(pilimage)


#taskid = shinkaiGAN_generate.apply_async(tensor, serializer='pickle')

ARTICLE2="""
write a function that sorts the elements in a list
"""

taskid = andrea_summarize_predict.delay(ARTICLE)

print(f"Submitted task: {taskid}")
# wait a bit
time.sleep(10)
# check if ready 
if taskid.ready():
  print("Result is ready:")
  print(taskid.get(timeout=1))
else:
  print("Result is not ready)")



