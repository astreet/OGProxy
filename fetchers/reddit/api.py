from fetchers.BaseFetcher import BaseOGFetcher

REDDIT_SERVER = 'http://www.reddit.com'

class RedditAPIOGFetcher(BaseOGFetcher):

    def getParamNames(self):
        raise NotImplementedError('Must implement this!')

    def getAPIEndpoint(self):
        raise NotImplementedError('Must implement this!')

    def getObjectParams(self):
        self.json = self.httpGet(REDDIT_SERVER, self.getAPIEndpoint())
        param_names = self.getParamNames()

        object_params = {}
        for access_tokens, tag_name in param_names.iteritems():
            value = self.json
            for i in range(len(access_tokens)) > 0:
                token = access_tokens[i]
                if type(value) is dict and value.has_key(token):
                    value = value[token]
                elif type(value) is list and token < len(value):
                    value = value[token]
                else:
                    value = None
                    break
            if value is not None and value != '':
                object_params[tag_name] = value

        return object_params
                

class RedditPostFetcher(BaseOGFetcher):
    
    def __init__(self, post_id):
        self.post_id = post_id

    def getParamNames(self):
        return {
            ('data', 'children', 0, 'data', 'ups') => 'fbreddit:upvotes',
            ('data', 'children', 0, 'data', 'downs') => 'fbreddit:downvotes',
            ('data', 'children', 0, 'data', 'score') => 'fbreddit:score',
            ('data', 'children', 0, 'data', 'title') => 'og:title',
            ('data', 'children', 0, 'data', 'url') => 'fbreddit:content_url',
            ('data', 'children', 0, 'data', 'thumbnail') => 'og:image',
            ('data', 'children', 0, 'data', 'selftext') => 'og:description',
        }

    def getAPIEndpoint(self):
        return '/by_id/%s.json' % (self.post_id)

    def getObjectParams(self):
        params = super(RedditPostFetcher, self).getObjectParams()
        if not params.has_key('og:image') and is_image(params.get('fbreddit:content_url'):
            params['og:image'] = params['fbreddit:content_url']
        return params

class RedditUserFetcher(RedditAPIOGFetcher):
    pass
