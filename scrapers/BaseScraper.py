from flask import abort
from flask.logging import getLogger
import httplib
from urlparse import urlparse

from logging import StreamHandler 

logger = getLogger('scraping')
logger.addHandler(StreamHandler())

class ScraperError(Exception):
    pass

class BaseOGScraper(object):

    def scrape(self, uri):
        parsed_uri = urlparse(uri)
        conn = httplib.HTTPConnection(parsed_uri.netloc)
        conn.request('GET', parsed_uri.path)
        response = conn.getresponse()

        if response.status != 200:
            conn.close()
            error = '%s returned %d (%s)!' % (uri, response.status, response.reason)
            logger.error(error)
            raise ScraperError(error)

        dom = response.read()
        conn.close()

        return self.scrapeDOM(dom)
    
    def scrapeDOM(self, dom):
        raise NotImplementedError('scrapeDOM must be implemented in base scraper classes')

