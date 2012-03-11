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

logger = app.logger

@app.route('/', methods=['GET'])
def index():
    uri = request.args.get('u', None)
    if not uri:
        abort(401)

    return handle_scrape(uri)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
