# -*- coding: utf-8 -*-

import base64
import os
import os.path
import simplejson as json
import urllib

from flask import abort, Flask, request, redirect, render_template
from flaskext.cache import Cache

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object('conf.Config')
cache = Cache(app)

import fetchers
from fetchers import BaseFetcher
fetchers.app = app
fetchers.cache = cache

from fetchers.reddit.api import *

@app.errorhandler(BaseFetcher.FetcherError)
def handle_scrape_error(error):
    return 'Error fetching: ' + error.message, 500

@app.route('/reddit/post/<post_id>', methods=['GET'])
def post(post_id):
    return RedditPostFetcher(post_id).fetch()

@app.route('/reddit/user/<username>', methods=['GET'])
def user(username):
    return RedditUserFetcher(username).fetch()

@app.route('/reddit/subreddit/<subreddit>', methods=['GET'])
def subreddit(subreddit):
    return RedditSubredditFetcher(subreddit).fetch()

@app.route('/reddit/comment/<post_id>/<comment_id>', methods=['GET'])
def comment(post_id, comment_id):
    return RedditCommentFetcher(post_id, comment_id).fetch()

@app.route('/'):
	redirect('/static/index.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
