from routing import scrapes

@scrapes('^https?://(reddit\.com|[^/]*\.reddit\.com)/.*')
def scrape_reddit(uri):
    return '<html>I would have scraped reddit!</html>'
