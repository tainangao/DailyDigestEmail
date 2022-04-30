"""
content
    - jokes
    - memes
    - inspirational quotes
        (from anime?)
        different language?
    - vocabulary
    - stats question & answer
    - forecast
    - reddit trending posts
"""
import csv
import random
import logging

logger = logging.getLogger(__name__)


def get_quote(quites_file='data/quotes_JBP.csv'):
    try:
        with open(quites_file) as csvfile:
            quotes = [{'author': line[0], 'quote': line[1]}
                      for line in csv.reader(csvfile, delimiter=',')]
    except Exception as e:
        quotes = [{'author': "Jordan B Peterson", 'quote': "When you have something to say, silence is a lie."}]

    return random.choice(quotes)


if __name__ == '__main__':
    print('Testing quote generation...')
    quote = get_quote()
    print("   - Today's Quote -   ")
    print("{} - {}".format(quote['quote'], quote['author']))
