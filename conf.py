import os
import pylibmc

class Config(object):
    DEBUG = True 
    TESTING = False
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'DEBUG')
    FBAPI_APP_ID = os.environ.get('FACEBOOK_APP_ID')
    CACHE_TYPE = 'memcached'
    CACHE_MEMCACHED_SERVERS = pylibmc.Client(
        servers=[os.environ.get('MEMCACHE_SERVERS')],
        username=os.environ.get('MEMCACHE_USERNAME'),
        password=os.environ.get('MEMCACHE_PASSWORD'),
        binary=True
    )
