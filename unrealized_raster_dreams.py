from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import API
from tweepy import Stream
import sys
import vincenty
import os
import json
import ATD


def get_it_started():
    '''
    I think this is an artifact of the projects original vision of being a raster based
    collection system with each cell having its own twitter listener and filling up real
    time. Sadly that vision cannot be realized without expensive firehose streaming capability.
    :return:
    '''

    record_path = os.path.join(os.getcwd(), 'point.csv')
    record_file = open(record_path, 'r')
    record_file.readline()

    while True:
        full_line = record_file.readline()
        if not full_line:
            break
        line = full_line.split(',')
        new_file = open(str(line[0])+'.txt','w')
        new_file.close()
    record_file.close()

        
# All the super-secret OAuth twitter API...stuff.
access_token = 'your token here'
access_token_secret = "remember, it's a secret"
consumer_key = 'dont let anyone know'
consumer_secret = 'and dont accidentally include it in a fork'


def parse_point_file(point_num):
    '''
    This is another function used in the original pipedream vision of the
    project. Apparantly there were a lot of files involved. I believe that someday
    it will be realized so it will be re-commented at that time.
    :param point_num: Raster grid location file
    :return: Decimal degree latitude and longitude
    '''
    file_name = str(point_num) + '.txt'
    file_path = os.path.join(os.getcwd(), file_name)
    point_file = open(file_path, 'r')
    lat, lon = point_file.readline().strip().split(',')
    return lat, lon

# Create the listener class when I get the tweety running.
# Nesting the main data handler call in here so it slows the API calls
# down to the point where tiwtter won't shut me down. (Enhance your calm error)
class StdOutListener(StreamListener):

    def __init__(self, num):
        point_num = num
        self.point_num = point_num
        print 'made listener!'
        return

    # Procs when legitimate json tweet data is plugged into the listener
    def on_data(self, data):

        # Read the tweet as a json object. Oh yes very nice. Call the things w/ [].
        tweet = json.loads(data)
        content = tweet['text']
        content.encode('utf-8')
        chars = content.len()

        parsed_content = content.split(' ')
        # This is my favorite block. Since the natural language processor wont recognize urls or hastags
        # I replace them all with a proper noun (it is very forgiving of proper noun placement).
        # Now every one of those proper nouns are 'Steve'. Egotistical? Yes. Hilarious? Most definitely.
        for place, word in enumerate(parsed_content):
            if '#' or 'http://' in word:
                parse_point_file[place] = 'Steve'

        parsed_content = parsed_content.join(' ')

        # print 'found a tweet'
        ATD.setDefaultKey('twitter_parsing-'+str(self.num))
        data = ATD.stats(parsed_content)

        edit_file = open(str(self.num)+'.txt', 'a')
        edit_file.write(str(chars), str(data.join(', ')))
        edit_file.close()

        return True

    def on_error(self, status):
        print status


class ListenRunner():

    def __init__(self): # , num, lat, lon):
        #self.num = num
        #self.lat = lat
        #self.lon = lon
        print('did listen runner')


    def create_bounding_box(self, lat, lon):
        # This is a bounding box to be created around the point considering WGS-84 spheroid. Uses
        # my vincenty solution stuff also on the githubs. I can't rememeber if this is the one that works
        # or not...
        ne_corner = vincenty.direct_solution(lat, lon, 11379.78, 45)
        sw_corner = vincenty.direct_solution(lat, lon, 11379.78, 45+180)
        sw_corner_lat, sw_corner_lon = sw_corner[0], sw_corner[1]
        ne_corner_lat, ne_corner_lon = ne_corner[0], ne_corner[1]
        print 'made a box'
        return round(sw_corner_lon,5), round(sw_corner_lat,5), round(ne_corner_lon,5), round(ne_corner_lat,5)

    def start_things(self, num, lat, lon):

        # IN-STAN-TI-ATE (that is a dalek creating my listener class)
        listener = StdOutListener(num)

        # Thank you tweepy for taking care of the OAuth headers so easily.
        authentication = OAuthHandler(consumer_key, consumer_secret)
        authentication.set_access_token(access_token, access_token_secret)


        # The concepts of data procesing are not matured in this version of the script. If things change and I am able
        # to get the firehose type data streaming that I want then I will make sure it's updated. The idea was to collect
        # the data with the search API in a five mile radius around a point centered within the 100 mile squared
        # bounding box. The API does some weird reverse geocoding in some situations and some changes need to be
        # made for integrity in this script.
        api = API(authentication)
        search_string = str(lat) + ',' + str(lon) + ',' + '5mi'
        my_tweets = api.search(geocode=search_string)
        print 'searching in '+search_string
        print len(my_tweets)
        for tweet in my_tweets:
            content = tweet.text
            content.encode('utf-8')
            chars = content.len()

            parsed_content = content.split(' ')
            for place, word in enumerate(parsed_content):
                if '#' or 'http://' in word:
                    parse_point_file[place] = 'Steve'

            parsed_content = parsed_content.join(' ')

            ATD.setDefaultKey('twitter_parsing-'+str(num))
            data = ATD.stats(parsed_content)

            _file = os.path.join(os.getcwd(), 'raster_space//'+str(num)+'.txt')
            edit_file = open(_file, 'a')
            edit_file.write(str(chars)+ str(data.join(', ')))
            edit_file.close()

