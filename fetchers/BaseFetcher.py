from flask import abort, render_template
from flask.logging import getLogger
import httplib

from logging import StreamHandler 

logger = getLogger('fetching')
logger.addHandler(StreamHandler())

class FetcherError(Exception):
    pass

class BaseOGFetcher(object):

    def fetch(self):
        object_params = self.getObjectParams()
        return render_template('og.html', object_params=object_params)
    
    def getObjectParams(self):
        raise NotImplementedError('getObjectParams must be implemented in base scraper classes')

