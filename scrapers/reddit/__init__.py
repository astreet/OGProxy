from routing import scrapes

from PostScraper import PostScraper

REDDIT_BASE_URI = '^https?://(www\.)?reddit\.com'

@scrapes(REDDIT_BASE_URI + '/r/[^/]+/comments/[^/]+/[^/]+/?$')
def scrape_post(uri):
    return PostScraper().scrape(uri)

@scrapes(REDDIT_BASE_URI + '/user/[^/]+/?$')
def scrape_user(uri):
    return UserScraper().scrape(uri)

@scrapes(REDDIT_BASE_URI + '/r/[^/]+/?$')
def scrape_user(uri):
    return SubredditScraper().scrape(uri)
