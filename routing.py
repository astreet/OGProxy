import flask
from flask.logging import getLogger
import re
import sys
from logging import StreamHandler 

logger = getLogger('routing')
logger.addHandler(StreamHandler())
scrapers = {}

def scrapes(route):
    logger.error('Registering route: ' + route)
    def wrap(f):
        scrapers[route] = f
        return f
    return wrap

def handle_scrape(uri):
    for key in scrapers.iterkeys():
        if re.search(key, uri):
            return scrapers[key](uri)
    flask.abort(404)
