from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import time
import ATD
import os
import json

# Set up a recording file this will hold the raw metrics.
record_path = os.path.join(os.getcwd(), 'record_file.txt')
record_file = open(record_path, 'a+')

# All the super secret OAuth twitter API...stuff.
access_token = 'your token here'
access_token_secret = "remember, it's a secret"
consumer_key = 'dont let anyone know'
consumer_secret = 'and dont accidentally include it in a fork'

# Here is the listener class and all the data handling for the ATD stuff.
class StdOutListener(StreamListener):

    def __init__(self):
        return

    def sentence_processing(self, content):
        '''
        A slightly altered proper noun replacement block. Removes most poorly encoded, program breaking idiosyncracies
        from tweets. Also replaces hashtags, @'s, and uri's with the proper noun "Steve" (they would otherwise be
        incorrectly marked as errors by the natural language processor). Hilarious results ensue.
        :param content: A string of text from the json tweet.
        :return: A cleaned up version string of the tweet ready for error checking.
        '''

        parsed_content = content.split(' ')
        for place, word in enumerate(parsed_content):
            if r'\x' in str(word):
                parsed_content[place] = ''

            if '#' in str(word):
                parsed_content[place] = 'Steve'

            if 'http://' in str(word):
                parsed_content[place] = 'Steve'

            if '@' in str(word):
                parsed_content[place] = 'Steve'

        parsed_content = ' '.join(parsed_content)

        return parsed_content

    def atd_processing(self, sentence):
        '''
        Takes the cleaned tweet string and pushes through the After the Deadline (ATD) API.
        Which was created by Miguel Ventura under the MIT license. He da real MVP.
        :param sentence: Cleaned tweet string
        :return: Yet another string of the raw language metrics.
        '''
        got_ATD_response = False
        data = []

        # I don't want to overdo it on the ATD sever calls so this block throttles things a little bit.
        # This constrains the rate of data collection and, arguably, compromises some of the scientific
        # integrity of the data. It also keeps things throttled for Twitter APIs sake. It is the curse of
        # big[ish] data. It pains me to have to do this at all.
        while not got_ATD_response:
            try:
                ATD.setDefaultKey('twitter_parsing-' + str(time.time()))
                data = ATD.stats(sentence)
                got_ATD_response = True
            except:
                print 'ATD servers are being dumb. Give them time to calm down then try again.'
                time.wait(10)
                pass

        # Puts the metric result data into a fancy list then combines it into a string for file output.
        metric_list = []
        for metric in data:
            metric_list.append(str(metric))

        metric_data = ','.join(metric_list)

        return metric_data

    # Procs when legitimate json tweet data is plugged into the listener
    def on_data(self, data):
        # Read the tweet as a json object. Oh yes very nice. Call the things w/ square brackets.
        tweet = json.loads(data)
        # This makes sure we only get geocoded tweets. This type of dataflow, while suboptimal, is necessary
        # because the free twitter API hates fun and happiness.
        if tweet['coordinates']:
            coords = tweet['coordinates']['coordinates']
            print coords
            ttext= tweet['text'].encode('utf-8')
            sentence = self.sentence_processing(ttext)
            print sentence
            metric_data = self.atd_processing(sentence)
            full_line = (str(coords[0])+','+str(coords[1])+','+metric_data+'\n')
            record_file.write(full_line)
            record_file.flush()
            time.sleep(1)
        return True

    def on_error(self, status):
        print status

# IN-STAN-TI-ATE.
listener = StdOutListener()

# Thank you tweepy for taking care of the OAuth headers so easily.
authentication = OAuthHandler(consumer_key, consumer_secret)
authentication.set_access_token(access_token, access_token_secret)

# Open up the streaming with my OAuth header and the listener class...listening.
stream = Stream(authentication, listener)
# This is where I filter my stream to relevant, contiguous US bboxed stuff. The bounding box can be changed to whatever,
# but this broad view was to get data just outside of the borders for continuity's sake. Also queries only english
# language tweets which, as it turns out, is important for english language processing.
while True:
    try:
       stream.filter(languages=['en'], locations=[-126.00, 26.00, -65.00, 50.00])
       print 'listened'
    except:
        pass

