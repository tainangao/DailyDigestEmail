"""
content
    - jokes
    - memes
    - inspirational quotes
        (from anime?)
        different language?
    - vocabulary
    - stats question & answer
    - weather forecast
    - reddit trending posts
"""
import csv
import json
import random
import logging
import requests
from decouple import config

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# TODO: write README

def get_quote(quites_file: str = 'data/quotes_JBP.csv') -> dict:
    """
    generate a random quote
    :param quites_file:
    :return:
    """
    try:
        with open(quites_file) as csvfile:
            quotes = [{'author': line[0], 'quote': line[1]}
                      for line in csv.reader(csvfile, delimiter=',')]
    except Exception as e:
        logger.error(e)
        quotes = [{'author': "Jordan B Peterson", 'quote': "When you have something to say, silence is a lie."}]

    return random.choice(quotes)


# https://towardsdatascience.com/how-to-use-the-reddit-api-in-python-5e05ddfd1e5c
# https://praw.readthedocs.io/en/latest/getting_started/quick_start.html
def get_reddit_post(subreddit: str = 'AskReddit') -> dict:  # TODO: other subreddit?
    """
    retrieve a subreddit post
    :param subreddit:
    :return:
    """
    pus = config('REDDIT_PUS')
    secret = config('REDDIT_SECRET')
    auth = requests.auth.HTTPBasicAuth(pus, secret)

    # here we pass our login method (password), username, and password
    data = {'grant_type': 'password',
            'username': config('REDDIT_USERNAME'),
            'password': config('REDDIT_PASSWORD')}

    # setup our header info, which gives reddit a brief description of our app
    headers = {'User-Agent': 'DailyDigestEmail'}
    try:
        # send our request for an OAuth token
        res = requests.post('https://www.reddit.com/api/v1/access_token',
                            auth=auth, data=data, headers=headers)

        # convert response to JSON and pull access_token value
        TOKEN = res.json()['access_token']

        # add authorization to our headers dictionary
        headers = {**headers, **{'Authorization': f"bearer {TOKEN}"}}

        # while the token is valid (~2 hours) we just add headers=headers to our requests
        requests.get('https://oauth.reddit.com/api/v1/me', headers=headers)
        res = requests.get(f"https://oauth.reddit.com/r/{subreddit}/rising",  # TODO: different sorting: hot, new?
                           headers=headers, params={'limit': 1})
        data = res.json()['data']['children'][0]['data']
        logger.debug(data)
        url = data['url']
        logger.info(f"url: {url}")
        title = data['title']
        logger.info(f"url: {title}")
        return {'title': title, 'url': url}

    except Exception as e:
        logger.critical(e)
        return {'title': 'What’s the most unprofessional thing a doctor has ever said to you?',
                'url': 'https://www.reddit.com/r/AskReddit/comments/ufb3yr/whats_the_most_unprofessional_thing_a_doctor_has/'}


def get_word(word: str) -> dict:
    """
    retrieve definitions and related phrases of a word
    :param word:
    :return:
    """
    key_collegiate = config('KEY_COLLEGIATE')
    url = f'https://dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={key_collegiate}'
    try:
        res = requests.request("GET", url)
        data = res.json()
        logger.debug(data)
        logger.info('{} has {} definitions.'.format(word, len(data)))

        d = {}  # keys in dict need to be unique, so it auto-filters out duplicated word types
        for i in data:
            d[i['fl']] = {'phrase': i['hwi']['hw'],
                          'definition': i['shortdef']}
        logger.info('return result of get_word(): {}'.format(d))
        return d

    except Exception as e:
        logger.critical(e)
        logger.info('Returning the fallback word...')
        with open('data/fallback_word.json') as f:
            d = json.load(f)
        logger.info('Return result of get_word(): {}'.format(d))
        return d


def get_random_word() -> dict:
    """
    return a details of a random word from data/words.txt
    :return:
    """
    with open('data/words.txt') as f:
        words = f.readlines()
        while True:
            try:
                word = random.choice(words)
                return get_word(word)
            except Exception as e:
                logger.error(e)


if __name__ == '__main__':
    logger.info('   - Testing quote generation...')
    quote = get_quote()
    logger.info("{} - {}".format(quote['quote'], quote['author']))

    # logger.info('   - Testing reddit post retrieval...')
    # quote = get_reddit_post()
    # logger.info(quote)

    logger.info('   - Testing word details retrieval...')
    get_random_word()
