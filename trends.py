"""Visualizing Twitter Sentiment Across America"""

import string
from data import word_sentiments, load_tweets, get_data
from geo import us_states, geo_distance, make_position, longitude, latitude
from maps import draw_state, draw_name, draw_dot, wait
from ucb import main, trace, interact, log_current_line
from idict import *


# Phase 1: The feelings in tweets

def make_tweet(text, time, lat, lon):
    """Return a tweet, represented as an immutable dictionary.    

    text -- A string; the text of the tweet, all in lowercase
    time -- A datetime object; the time that the tweet was posted
    lat -- A number; the latitude of the tweet's location
    lon -- A number; the longitude of the tweet's location
    """
    return make_idict(('text', text), ('time', time), ('latitude', lat), ('longitude', lon))

def tweet_words(tweet):
    """Return a tuple of words in the tweet.
    
    Arguments:
    tweet -- a tweet abstract data type.
    
    Return 1 value:
     - The list of words in the tweet.
    """
    "*** YOUR CODE HERE ***"
    text = idict_select(tweet, 'text')
    text = extract_words(text)
    return text
    

def tweet_location(tweet):
    """Return a position (see geo.py) that represents the tweet's location."""
    "*** YOUR CODE HERE ***"
    lat = idict_select(tweet, 'latitude')
    lon = idict_select(tweet, 'longitude')
    return make_position(lat, lon)

def tweet_string(tweet):
    """Return a string representing the tweet."""
    return '"{0}" @ {1}'.format(idict_select(tweet, 'text'), tweet_location(tweet))

def extract_words(text):
    """Return a tuple of the words in a tweet, not including punctuation.

    >>> extract_words('anything else.....not my job')
    ('anything', 'else', 'not', 'my', 'job')
    >>> extract_words('i love my job. #winning')
    ('i', 'love', 'my', 'job', 'winning')
    >>> extract_words('make justin # 1 by tweeting #vma #justinbieber :)')
    ('make', 'justin', 'by', 'tweeting', 'vma', 'justinbieber')
    >>> extract_words("paperclips! they're so awesome, cool, & useful!")
    ('paperclips', 'they', 're', 'so', 'awesome', 'cool', 'useful')
    """
    "*** YOUR CODE HERE ***"
    global string
    for char in text:
        if char in string.punctuation:
            text = text.replace(char, " ")
        if char in string.digits:
            text = text.replace(char, " ")
    return tuple(text.split())

def get_word_sentiment(word):
    """Return a number between -1 and +1 representing the degree of positive or
    negative feeling in the given word. 

    Return None if the word is not in the sentiment dictionary.
    (0 represents a neutral feeling, not an unknown feeling.)
    
    >>> get_word_sentiment('good')
    0.875
    >>> get_word_sentiment('bad')
    -0.625
    >>> get_word_sentiment('winning')
    0.5
    >>> get_word_sentiment('Berkeley')  # Returns None
    """
    return get_data(word)

def analyze_tweet_sentiment(tweet):
    """ Return a number between -1 and +1 representing the degree of positive or
    negative sentiment in the given tweet, averaging over all the words in the
    tweet that have a sentiment score. 

    If there are words that don't have a sentiment score, leave them 
    out of the calculation. 

    If no words in the tweet have a sentiment score, return None.
    (do not return 0, which represents neutral sentiment).

    >>> positive = make_tweet('i love my job. #winning', None, 0, 0)
    >>> round(analyze_tweet_sentiment(positive), 5)
    0.29167
    >>> negative = make_tweet("Thinking, 'I hate my job'", None, 0, 0)
    >>> analyze_tweet_sentiment(negative)
    -0.25
    >>> no_sentiment = make_tweet("Go bears!", None, 0, 0)
    >>> analyze_tweet_sentiment(no_sentiment)
    """
    average = None
    "*** YOUR CODE HERE ***"
    words = tweet_words(tweet)
    summed = 0
    count = 0
    for word in words:
        if (get_word_sentiment(word) != None):
            summed += get_word_sentiment(word)
            count+=1

    if(count==0):
        return None
    average = summed/count
    
    return average

def print_sentiment(text='Are you virtuous or verminous?'):
    """Print the words in text, annotated by their sentiment scores.

    For example, to print each word of a sentence with its sentiment:

    # python3 trends.py 'favorite family layman'
    """
    words = extract_words(text.lower())
    assert words, 'No words extracted from "' + text + '"'
    layout = '{0:>' + str(len(max(words, key=len))) + '}: {1}'
    for word in extract_words(text.lower()):
        print(layout.format(word, get_word_sentiment(word)))
        

# Phase 2: The geometry of maps

def find_centroid(polygon):
    """Find the centroid of a polygon.

    http://en.wikipedia.org/wiki/Centroid#Centroid_of_polygon
    
    polygon -- A tuple of positions, in which the first and last are the same

    Returns: 3 numbers; centroid latitude, centroid longitude, and polygon area

    Hint: If a polygon has 0 area, return its first position as its centroid

    >>> p1, p2, p3 = make_position(1, 2), make_position(3, 4), make_position(5, 0)
    >>> triangle = (p1, p2, p3, p1)  # First vertex is also the last vertex
    >>> find_centroid(triangle)
    (3.0, 2.0, 6.0)
    >>> find_centroid((p1, p3, p2, p1))
    (3.0, 2.0, 6.0)
    >>> find_centroid((p1, p2, p1))
    (1, 2, 0)
    """
    "*** YOUR CODE HERE ***"

    def Area(polygon):
        l = len(polygon)-1
        temp = 0
        area =0
        while(temp<l):
            area+= (latitude(polygon[temp]) *longitude(polygon[temp+1])-latitude(polygon[temp+1])*longitude(polygon[temp]))
            temp +=1
        area = area/2
        return (area)
    area = Area(polygon)

    l = len(polygon)-1
    temp = 0
    Cx, Cy = 0, 0

    while (temp <l):
        Cx += (latitude(polygon[temp])+latitude(polygon[temp+1]))*(latitude(polygon[temp]) *longitude(polygon[temp+1])-latitude(polygon[temp+1])*longitude(polygon[temp]))
        Cy += (longitude(polygon[temp])+longitude(polygon[temp+1]))*(latitude(polygon[temp]) *longitude(polygon[temp+1])-latitude(polygon[temp+1])*longitude(polygon[temp]))
        temp +=1

    if (area)==0:
        return latitude(polygon[0]), longitude(polygon[0]), 0

    Cx = Cx/(6*area)
    Cy = Cy/ (6*area)
    return Cx, Cy, abs(area)
    
            

def find_center(shapes):
    """Compute the geographic center of a state, averaged over its shapes.

    The center is the average position of centroids of the polygons in shapes,
    weighted by the area of those polygons.
    
    Arguments:
    # shapes -- a list of polygons
    shapes -- a tuple of polyons

    >>> ca = find_center(idict_select(us_states, 'CA'))  # California
    >>> round(latitude(ca), 5)
    37.25389
    >>> round(longitude(ca), 5)
    -119.61439

    >>> hi = find_center(idict_select(us_states, 'HI'))  # Hawaii
    >>> round(latitude(hi), 5)
    20.1489
    >>> round(longitude(hi), 5)
    -156.21763
    """
    "*** YOUR CODE HERE ***"

    Xsum, Ysum, totalArea = 0, 0, 0

    for polygon in shapes:
        X,Y, area = find_centroid(polygon)
        Xsum, Ysum, totalArea = Xsum+X*area, Ysum+Y*area, totalArea+area
    Xsum = Xsum/totalArea
    Ysum = Ysum/totalArea
    return make_position(Xsum,Ysum)
        

def draw_centered_map(center_state='TX', n=10):
    """Draw the n states closest to center_state.
    
    For example, to draw the 20 states closest to California (including California),
    enter in the terminal: 

    # python3 trends.py CA 20
    """
    us_centers = make_idict()
    for i, s in idict_items(us_states):
        us_centers = idict_insert(us_centers, i, find_center(s))
    center = idict_select(us_centers, center_state.upper())
    dist_from_center = lambda name: geo_distance(center, idict_select(us_centers, name)) 
    for name in sorted(idict_keys(us_states), key=dist_from_center)[:int(n)]:
        draw_state(idict_select(us_states, name))
        draw_name(name, idict_select(us_centers, name))
    draw_dot(center, 1, 10)  # Mark the center state with a red dot
    wait()


# Phase 3: The mood of the nation

def find_closest_state(tweet, state_centers):
    """Return the name of the state closest to the given tweet's location.
    
    Use the geo_distance function (already provided) to calculate distance 
    in miles between two latitude-longitude positions.

    Arguments:
    tweet -- a tweet abstract data type
    state_centers -- a immutable dictionary from state names to positions

    >>> us_centers = make_idict()
    >>> for n, s in idict_items(us_states):
    ...     us_centers = idict_insert(us_centers, n, find_center(s)) 
    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> find_closest_state(sf, us_centers)
    'CA'
    >>> find_closest_state(ny, us_centers)
    'NJ'
    """
    "*** YOUR CODE HERE ***"

    loc=tweet_location(tweet)

    keys = idict_keys(state_centers)
    minDist = 1000000
    for key in keys:
        centerloc=idict_select(state_centers,key)
        if(geo_distance(loc, centerloc)<minDist):
            minDist= geo_distance(loc, centerloc)
            closest = key

    return closest
    


def group_tweets_by_state(tweets):
    """Return an immutable dictionary that aggregates tweets by their nearest state center.

    The keys of the returned dictionary are state names, and the values are
    tuples of tweets that appear closer to that state center than any other.
     
    tweets -- a tuple of tweet abstract data types

    >>> sf = make_tweet("Welcome to San Francisco", None, 38, -122)
    >>> ny = make_tweet("Welcome to New York", None, 41, -74)
    >>> ca_tweets = idict_select(group_tweets_by_state((sf, ny)), 'CA')
    >>> tweet_string(ca_tweets[0])
    '"Welcome to San Francisco" @ (38, -122)'
    """
    tweets_by_state, us_centers = make_idict(), make_idict()
    for n, s in idict_items(us_states):
        us_centers = idict_insert(us_centers, n, find_center(s))

    for tweet in tweets:
        key=find_closest_state(tweet, us_centers)
        if(not idict_select(tweets_by_state, key)):
            tweets_by_state=idict_insert(tweets_by_state, key, (tweet,))

        else:
            prev = idict_select(tweets_by_state, key)
            tweets_by_state=idict_insert(tweets_by_state, key, prev + (tweet,))
            
    "*** YOUR CODE HERE ***"
    return tweets_by_state

def calculate_average_sentiments(tweets_by_state):
    """Calculate the average sentiment of the states by averaging over all 
    the tweets from each state that have a sentiment value. Return the result
    as an immutable dictionary from state names to average sentiment values.
   
    If a state has no tweets with sentiment values, leave it out of the
    dictionary entirely.  Do not include a states with no tweets, or with tweets
    that have no sentiment, as 0.  0 represents neutral sentiment, not unknown
    sentiment.

    tweets_by_state -- An immutable dictionary from state names to tuples of tweets
    """

    #for states in 
    averaged_state_sentiments = make_idict()
    
    for key in idict_keys(tweets_by_state):
        tweets = idict_select(tweets_by_state, key)
        count=0
        senti= None
        for tweet in tweets:
            if(analyze_tweet_sentiment(tweet)):
                if (senti==None):
                    senti = 0
                senti = senti + analyze_tweet_sentiment(tweet)
                count+=1
        if(senti!=None):
            senti = senti/count
            averaged_state_sentiments=idict_insert(averaged_state_sentiments, key, senti)

    "*** YOUR CODE HERE ***"
    return averaged_state_sentiments

def draw_state_sentiments(state_sentiments=make_idict()):
    """Draw all U.S. states in colors corresponding to their sentiment value.
    
    Unknown state names are ignored; states without values are colored grey.
    
    state_sentiments -- An immutable dictionary from state strings to sentiment values
    """
    for name, shapes in idict_items(us_states):
        sentiment = idict_select(state_sentiments, name)
        draw_state(shapes, sentiment)
    
    for name, shapes in idict_items(us_states):
        center = find_center(shapes)
        if center is not None:
            draw_name(name, center)

def draw_map_for_term(term='my job'):
    """
    Draw the sentiment map corresponding to the tweets that match term.
    
    term -- a word or phrase to filter the tweets by.  
    
    To visualize tweets containing the word "obama":
    
    # python3 trends.py obama
    
    Some term suggestions:
    New York, Texas, sandwich, my life, justinbieber
    """
    tweets = load_tweets(make_tweet, term)
    tweets_by_state = group_tweets_by_state(tweets)
    state_sentiments = calculate_average_sentiments(tweets_by_state)
    draw_state_sentiments(state_sentiments)
    for tweet in tweets:
        draw_dot(tweet_location(tweet), analyze_tweet_sentiment(tweet))
    wait()

#################################################################
##   You don't need to look at this unless you really want to  ##
#################################################################

def setup_args():
    """Reads in the command-line argument, and chooses an appropriate
    action.

    Note: this function uses Python syntax/techniques not yet covered
          in this course. You do not need to understand how this works.
    """
    import argparse

    description = """Run your project code in a specific manner. For \
instance, to run the print_sentiment code, do: 'python3 trends.py \
--print_sentiment "favorite family lowerclassman" '. Defaults to {0} if no argument is \
given.""".format('--print_sentiment')

    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('fn_args', nargs='*')
    parser.add_argument('--print_sentiment', '-3', const=print_sentiment,
                        action='store_const', dest='fn',
                        help="Prints the sentiment of each word of a \
given sentence.")
    parser.add_argument('--draw_centered_map', '-6', const=draw_centered_map,
                        action='store_const', dest='fn',
                        help="Draws the N closest states to a given STATE.")
    parser.add_argument('--draw_map_for_term', '-9', const=draw_map_for_term,
                        action='store_const', dest='fn', 
                        help="Displays the sentiments for a given term.")

    args = parser.parse_args()
    if not args.fn:
        args.fn = print_sentiment
    if args.fn == print_sentiment:
        wds = ' '.join(args.fn_args)
        return lambda: args.fn(wds)
    elif args.fn == draw_centered_map:
        if len(args.fn_args) <= 1:
            centerstate = args.fn_args
            return lambda: args.fn(centerstate)
        else:
            centerstate, n = args.fn_args
            return lambda: args.fn(centerstate, n)
    else:
        return lambda: args.fn(args.fn_args[0])

@main
def run(*args):
    fn = setup_args()
    fn()
