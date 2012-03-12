# -*- coding: utf-8 -*-

import base64
import os
import os.path
import simplejson as json
import urllib
import pylibmc

from flask import abort, Flask, request, redirect, render_template
from flaskext.cache import Cache

from fetchers import BaseFetcher
from fetchers.reddit.api import *

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object('conf.Config')
cache = Cache(app)

@app.errorhandler(BaseFetcher.FetcherError)
def handle_scrape_error(error):
    return 'Error fetching: ' + error.message, 500

@app.route('/reddit/post/<post_id>', methods=['GET'])
@cache.memoize(timeout=1800)
def post(post_id):
    return RedditPostFetcher(post_id).fetch()

@app.route('/reddit/user/<username>', methods=['GET'])
@cache.memoize(timeout=10800)
def user(username):
    return RedditUserFetcher(username).fetch()

@app.route('/reddit/subreddit/<subreddit>', methods=['GET'])
@cache.memoize(timeout=86400)
def subreddit(subreddit):
    return RedditSubredditFetcher(subreddit).fetch()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
