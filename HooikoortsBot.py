#!/usr/bin/env python
__doc__ = "The HooikoortsBot retrieves tweets that contain the term 'hay fever' and provides natural remedies when the sentiment of the tweet is negative."
__author__ = "David Lopez Mejia, Sietse Huisman, Gert-Jan de Graaf" 
__credits__ = ["David Lopez Mejia", "Sietse Huisman", "Gert-Jan de Graaf"]
__license__ = "CC BY-NC 4.0" 
__version__ = "0.0.1" 
__maintainer__ = "David Lopez Mejia" 
__email__ = "d.i.lopezmejia@student.vu.nl" 
__status__ = "Production"

import tweepy, json, sys, random
#reload(sys)
#sys.setdefaultencoding("utf-8")
from urllib2 import Request, urlopen, URLError
from keys import keys
from collections import Counter


# Create a keys.py file with your Twitter API credentials
CONSUMER_KEY = keys['consumer_key']
CONSUMER_SECRET = keys['consumer_secret']
ACCESS_TOKEN = keys['access_token']
ACCESS_TOKEN_SECRET = keys['access_token_secret']
 
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
 
# Main query for the Twitter search 
twt = api.search(q="hay fever")     
 
# List of specific symptoms we want to check for in the retrieved Tweets.
# The bot will not tweet at someone if it does not detect at least one of
# these keywords.
symptoms1 = ['rhinorrhea',
             'nasal',
             'runny nose',
             'itching',
             'itch',
             'itchy',
             'sneezing',
             'congestion',
             'congested',
             'clogged',
             'obstruction',
             'obstructed',
             'conjunctival swelling',
             'swollen',
             'swelling',
             'itchy eyes',
             'swollen eyes',
             'teary eyes',
             'erythema',
             'eyelid swelling',
             'swollen eyelids',
             'lower eyelid venous stasis',
             'rings under the eyes',
             'allergic shiners',
             'swollen nasal turbinates',
             'swollen nose',
             'middle ear effusion',
             'clogged ears',
             'dry throat'
        ]
'''
# Add symptoms that would yield to different remedies
symptoms2 = ['hello',
    'Hello world!',
    'Hello World!!!',
    'Hello world!!!',
    'Hello, world!',
    'Hello, World!',
     'This is a very unique tweet.']
'''

#get keywords given a certain tweet from the Alchemy API
def getKeywords(tweet):
    tweet = tweet.encode('utf-8')
    keywords = []
    api_key = '8158bcf4501268b1166d06c98ac16796553f6b9b'
    url_text = tweet.replace(' ', '%20')
    request_text = 'http://access.alchemyapi.com/calls/text/TextGetRankedKeywords?apikey=' + api_key + '&text=' +url_text+ '&outputMode=json'
    request = Request(request_text)
    
    #make request, if succesful return keywords, else return error
    try:
         response = urlopen(request)
         try:
             json2 = json.loads(response.read())
         except:
             json2 = []
         if 'keywords' in json2:         
             keywords_with_relevance = json2['keywords']
             for key in keywords_with_relevance:
                 keywords.append(key['text'])
             return keywords
         else:
             return []
    except URLError, e:
         print 'No kittez. Got an error code:', e
         return []


# Get the sentiment of the tweets from Alchemy API
def getSentiment(tweet):
    tweet = tweet.encode('utf-8')
    keywords = []
    api_key = '8158bcf4501268b1166d06c98ac16796553f6b9b'
    url_text = tweet.replace(' ', '%20')
    request_text = 'http://access.alchemyapi.com/calls/text/TextGetTextSentiment?apikey=' + api_key + '&text=' +url_text+ '&outputMode=json'
    request = Request(request_text)
    
    #make request, if succesful return keywords, else return error
    try:
         response = urlopen(request)
         try:
             json2 = json.loads(response.read())
         except:
             json2 = []

         #print json2
         if 'docSentiment' in json2:         
             return json2['docSentiment']['type']
             
         else:
             return ''
    except URLError, e:
         print 'No kittez. Got an error code:', e
         return []
        


keywords = []

# Use the natural remedies published in
# http://www.goodtoknow.co.uk/wellbeing/galleries/28104/natural-hay-fever-remedies
treatments = ['eating more honey? Bee pollen desensitizes your body to other pollens!',
              'eating more vitamin C? It is a known natural antihistamine! Eat an orange!',
              'some hot peppers? They contain capsaicin, which opens your nasal passages!',
              'eating carrots, sweet potatoes, or spinach? They all contain antioxidants that help against swelling!',
              'drinking chamomile tea? It acts as an anti-inflammatory agent thanks to its anti-oxidants and flavonoids!',
              'increasing your intake of garlic? It can really boost your immune system, also being a decongestant!',
              'eating more onions? They are a good source of quercetin, a natural antihistamine and anti-inflammatory!'
    ]

with open('symptomsJSON.json', 'r') as f:
    symptom_counters = json.load(f)

with open('sentimentsJSON.json', 'r') as g:
    sentiment_counters = json.load(g)

# Get the IDs of all the tweets that have been analyzed in the past
tweetIDs = open("tweetIDs.txt", "r")	
stored_tweetIDs = tweetIDs.read().split(',')
new_tweetIDs = []

# Run the bot
for s in twt:
    # Check if the current tweet was already analyzed
    if str(s.id) not in stored_tweetIDs:
        keywords = getKeywords(s.text)
        # print keywords
        sentiment = getSentiment(s.text)
        if sentiment != 'positive' and sentiment != 'neutral' and sentiment != 'negative' and sentiment != '':
            sentiment = ''
        #print sentiment
        #print sentiment_counters
        sentiment_counters[sentiment] += 1
        #check on first symptoms
        for symptom in symptoms1:
            for keyword in keywords:
                if symptom.lower() == keyword.lower():
                    symptom_counters[symptom] += 1
                    sn = s.user.screen_name
                    print sn
                    m = "@%s Have you tried " % (sn) + random.choice(treatments) 
                    try:
                        if sentiment == 'negative':
                            s = api.update_status(status=m, in_reply_to_status_id=s.id)
                            '''
                                                    # Debugging and getting info on sent tweets
                            print 'Sentiment: ' + sentiment
                            print 'tweeting to: ' + sn
                            print m
                            '''
                    except:
                        continue
        new_tweetIDs.append(s.id)

        
# Save the number of incidences of each symptom in this run            
with open('symptomsJSON.json', 'w') as f:
    f.write(json.dumps(symptom_counters))

# Save the number of tweets with a certain sentiment in this run
with open('sentimentsJSON.json', 'w') as g:
    g.write(json.dumps(sentiment_counters))


#Save the tweet IDs to prevent from sending repeated tweets to people
with open("tweetIDs.txt", "a") as ids:
    ids.write(','.join(map(str, new_tweetIDs)))
