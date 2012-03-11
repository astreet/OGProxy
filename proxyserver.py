# -*- coding: utf-8 -*-

import base64
import os
import os.path
import simplejson as json
import urllib

import requests

from flask import abort, Flask, request, redirect, render_template

from routing import *
from scrapers import *

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object('conf.Config')

@app.errorhandler(BaseScraper.ScraperError)
def handle_scrape_error(error):
    return 'Error scraping: ' + error.message, 500

@app.route('/reddit/post/<post_id>', methods=['GET'])
def post(username):
    return RedditPostFetcher(post_id).fetch()

@app.route('/reddit/user/<username>', methods=['GET'])
def user(username):
    return RedditUserFetcher(username).fetch()

@app.route('/reddit/subreddit/<subreddit_name>', methods=['GET'])
def user(username):
    return RedditSubredditFetcher(subreddit_name).fetch()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
