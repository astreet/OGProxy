import fetchers
from fetchers.BaseFetcher import BaseOGFetcher, http_get
import flask
from flask.logging import getLogger
import httplib
from logging import StreamHandler
import re
import simplejson as json
from urlparse import urlparse

REDDIT_SERVER = 'www.reddit.com'
REDDIT_URI = 'http://' + REDDIT_SERVER
PROXY_URI = 'http://ogproxy.herokuapp.com'

logger = getLogger('reddit-api')
logger.addHandler(StreamHandler())

@fetchers.cache.memoize(timeout=1800)
def cached_http_get(server, path):
    return http_get(server, path)

def is_image(uri):
    return uri and uri.endswith(('jpg', 'png', 'gif', 'bmp'))

def is_imgur_single(uri):
    if not uri:
        return False

    parsed = urlparse(uri)
    if not (parsed.netloc == 'imgur.com' or parsed.netloc.endswith('.imgur.com')):
        return False

    return re.match('^/[^/]+$', parsed.path)

def extract_image(s):
    match = re.search('https?://[^/]+/.*\.(jpg|png|gif|bmp)', s)
    if not match:
        return None
    return match.group(0)

class RedditAPIOGFetcher(BaseOGFetcher):

    def getOGType(self):
        raise NotImplementedError('Must implement this!')

    def getDefaultImage(self):
        raise NotImplementedError('Must implement this!')

    def getParamNames(self):
        raise NotImplementedError('Must implement this!')

    def getAPIEndpoint(self):
        raise NotImplementedError('Must implement this!')

    def getObjectParams(self):
        self.json = json.loads(cached_http_get(REDDIT_SERVER, self.getAPIEndpoint()))
        param_names = self.getParamNames()

        object_params = {}
        for tag_name, access_tokens in param_names.iteritems():
            transform_function = (lambda v: v)
            if type(access_tokens[0]) is tuple:
                access_tokens, transform_function = access_tokens
            
            value = self.json
            for i in range(len(access_tokens)):
                token = access_tokens[i]
                if type(value) is dict and value.has_key(token):
                    value = value[token]
                elif type(value) is list and token < len(value):
                    value = value[token]
                else:
                    value = None
                    break
            if value is not None and value != '':
                object_params[tag_name] = transform_function(value)

        if not object_params.has_key('og:image') or not is_image(object_params['og:image']):
            object_params['og:image'] = self.getDefaultImage()

        object_params['og:type'] = self.getOGType()

        return object_params
                

class RedditPostFetcher(RedditAPIOGFetcher):

    def __init__(self, post_id):
        self.post_id = post_id

    def getOGType(self):
        return 'fbreddit:post'

    def getDefaultImage(self):
        return 'http://2.bp.blogspot.com/-otxHec_ptYA/Txi3lYGCceI/AAAAAAAAAOg/xrSjvqUpjas/s1600/reddit-alien-blackout.png'

    def getParamNames(self):
        return {
            'fbreddit:upvotes': ('data', 'children', 0, 'data', 'ups'),
            'fbreddit:downvotes': ('data', 'children', 0, 'data', 'downs'),
            'fbreddit:score': ('data', 'children', 0, 'data', 'score'),
            'og:title': ('data', 'children', 0, 'data', 'title'),
            'fbreddit:content_url': ('data', 'children', 0, 'data', 'url'),
            'fbreddit:link': (
                ('data', 'children', 0, 'data', 'permalink'),
                lambda pl: REDDIT_URI + pl
            ),
            'og:image': ('data', 'children', 0, 'data', 'thumbnail'),
            'og:description': ('data', 'children', 0, 'data', 'selftext'),
            'og:url': (
                ('data', 'children', 0, 'data', 'name'),
                lambda p: PROXY_URI + flask.url_for('post', post_id=p)
            ),
            'fbreddit:author': (
                ('data', 'children', 0, 'data', 'author'),
                lambda u: PROXY_URI + flask.url_for('user', username=u),
            ),
            'fbreddit:subreddit': (
                ('data', 'children', 0, 'data', 'subreddit'),
                lambda s: PROXY_URI + flask.url_for('subreddit', subreddit=s),
            ),
        }

    def getAPIEndpoint(self):
        return '/by_id/%s.json' % (self.post_id)

    def getObjectParams(self):
        params = super(RedditPostFetcher, self).getObjectParams()
        if params['og:image'] == self.getDefaultImage():
            content_url = params.get('fbreddit:content_url')
            if is_image(content_url):
                params['og:image'] = content_url 
            elif is_imgur_single(content_url):
                params['og:image'] = content_url + '.png'
                
        return params

class RedditUserFetcher(RedditAPIOGFetcher):

    def __init__(self, username):
        self.username = username

    def getOGType(self):
        return 'fbreddit:user'

    def getDefaultImage(self):
        return 'http://redditstatic.s3.amazonaws.com/sobrave.png'

    def getParamNames(self):
        return {
            'fbreddit:link_karma': ('data', 'link_karma'),
            'fbreddit:comment_karma': ('data', 'comment_karma'),
            'fbreddit:birthday': (
                ('data', 'created_utc'),
                lambda ts: int(ts)
            ),
            'og:title': ('data', 'name'),
            'og:url': (
                ('data', 'name'),
                lambda u: PROXY_URI + flask.url_for('user', username=u),
            ),
            'fbreddit:link': (
                ('data', 'name'),
                lambda u: REDDIT_URI + '/user/' + u
            ),
        }

    def getAPIEndpoint(self):
        return '/user/%s/about.json' % (self.username)

class RedditSubredditFetcher(RedditAPIOGFetcher):

    def __init__(self, subreddit):
        self.subreddit = subreddit 

    def getOGType(self):
        return 'fbreddit:subreddit'

    def getDefaultImage(self):
        return 'http://sp.reddit.com/160x160A.jpg'

    def getParamNames(self):
        return {
            'og:description': ('data', 'description'),
            'og:image': ('data', 'header_img'),
            'og:title': (
                ('data', 'display_name'),
                lambda name: '/r/' + name,
            ),
            'og:url': (
                ('data', 'display_name'),
                lambda s: PROXY_URI + flask.url_for('subreddit', subreddit=s),
            ),
            'fbreddit:link': (
                ('data', 'url'),
                lambda url: REDDIT_URI + url
            ),
            'fbreddit:subscribers': ('data', 'subscribers'),
        }

    def getAPIEndpoint(self):
        return '/r/%s/about.json' % (self.subreddit)

class RedditCommentFetcher(RedditAPIOGFetcher):

    def __init__(self, post_id, comment_id):
        self.post_id = post_id
        self.cid = comment_id

    def getOGType(self):
        return 'fbreddit:comment'

    def getDefaultImage(self):
        return 'http://i.imgur.com/tH8Q5.png'

    def getParamNames(self):
        return {
            'fbreddit:upvotes': (1, 'data', 'children', 0, 'data', 'ups'),
            'fbreddit:downvotes': (1, 'data', 'children', 0, 'data', 'downs'),
            'og:title': (
                (1, 'data', 'children', 0, 'data', 'body'),
                lambda t: t if len(t) < 50 else t[:47] + '...'
            ),
            'fbreddit:link': (
                (),
                lambda _: REDDIT_URI + '/comments/%s/466f7865732052756c65/%s' % (self.post_id, self.cid)
            ),
            'og:image': (
                (1, 'data', 'children', 0, 'data', 'body'),
                lambda b: extract_image(b)
            ),
            'og:description': (1, 'data', 'children', 0, 'data', 'body'),
            'og:url': (
                (),
                lambda _: PROXY_URI + flask.url_for('comment', post_id=self.post_id, comment_id=self.cid)
            ),
            'fbreddit:author': (
                (1, 'data', 'children', 0, 'data', 'author'),
                lambda u: PROXY_URI + flask.url_for('user', username=u),
            ),
            'fbreddit:post': (
                (),
                lambda _: PROXY_URI + flask.url_for('post', post_id=('t3_' + self.post_id)),
            ),
        }

    def getAPIEndpoint(self):
        return '/comments/%s/466f7865732052756c65/%s.json?limit=1' % (self.post_id, self.cid)

    def getObjectParams(self):
        params = super(RedditCommentFetcher, self).getObjectParams()
        params['fbreddit:score'] = params['fbreddit:upvotes'] - params['fbreddit:downvotes']
        return params
