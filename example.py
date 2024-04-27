import time
from queueDS import enqueue_item, dequeue_item
from utils import make_request, logging
from models import db_session, NoResultFound, Item, Keyword
import logging
from linkedin_jobs_scraper import LinkedinScraper
from linkedin_jobs_scraper.events import Events, EventData, EventMetrics
from linkedin_jobs_scraper.query import Query, QueryOptions, QueryFilters
from linkedin_jobs_scraper.filters import RelevanceFilters, TimeFilters, TypeFilters, ExperienceLevelFilters, \
    OnSiteOrRemoteFilters
from queueDS import enqueue_item, dequeue_item
from utils import make_request, logging
from models import BaseJobPosting, db_session

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    "Accept-Language": "en-us",
    "Accept-Encoding": "gzip, deflate",
}

KEYWORD_QUEUE = "keywords"

# Fired once for each successfully processed job
def on_data(data: EventData):
    print('[ON_DATA]', data.title, data.company, data.company_link, data.date, data.link, data.insights,
          len(data.description))
    job = BaseJobPosting()
    job.title = data.title
    job.company = data.company
    job.company_link = data.company_link
    job.date = data.date
    job.link = data.link
    job.insights = data.insights
    job.description = data.description
    job.save()


def on_metrics(metrics: EventMetrics):
    print('[ON_METRICS]', str(metrics))


def on_error(error):
    print('[ON_ERROR]', error)


def on_end():
    print('[ON_END]')

def swap(keyword):

    logging.basicConfig(level=logging.INFO)
    logging.info(u"Searching for keyword: {}".format(keyword))

    scraper = LinkedinScraper(
    chrome_executable_path=None,  # Custom Chrome executable path (e.g. /foo/bar/bin/chromedriver)
    chrome_binary_location=None,  # Custom path to Chrome/Chromium binary (e.g. /foo/bar/chrome-mac/Chromium.app/Contents/MacOS/Chromium)
    chrome_options=None,  # Custom Chrome options here
    headless=True,  # Overrides headless mode only if chrome_options is None
    max_workers=1,  # How many threads will be spawned to run queries concurrently (one Chrome driver for each thread)
    slow_mo=0.5,  # Slow down the scraper to avoid 'Too many requests 429' errors (in seconds)
    page_load_timeout=40  # Page load timeout (in seconds)    
    )

# Add event listeners
    scraper.on(Events.DATA, on_data)
    scraper.on(Events.ERROR, on_error)
    scraper.on(Events.END, on_end)

    queries = [
        Query(
            options=QueryOptions(
                limit=27  # Limit the number of jobs to scrape.            
            )
        ),
        Query(
            query='Engineer',
            options=QueryOptions(
                locations=['United States', 'Europe'],
                apply_link=True,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
                skip_promoted_jobs=True,  # Skip promoted jobs. Default to False.
                page_offset=2,  # How many pages to skip
                limit=5,
                filters=QueryFilters(
                    company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',  # Filter by companies.                
                    relevance=RelevanceFilters.RECENT,
                    time=TimeFilters.MONTH,
                    type=[TypeFilters.FULL_TIME, TypeFilters.INTERNSHIP],
                    on_site_or_remote=[OnSiteOrRemoteFilters.REMOTE],
                    experience=[ExperienceLevelFilters.MID_SENIOR]
                )
            )
        ),
    ]
    scraper.run(queries)

def search(keyword):

    logging.info(u"Searching for keyword: {}".format(keyword))

    try:
        kw = db_session.query(Keyword).filter_by(keyword=keyword).one()
    except NoResultFound:
        kw = Keyword(keyword=keyword).save()

    page = make_request("https://scrapethissite.com/pages/forms/?q={}".format(keyword), headers=HEADERS)

    for row in page.find_all("tr", "team"):
        i = Item()
        i.year = row.find("td", "name").text.strip()
        i.wins = row.find("td", "wins").text.strip()
        i.losses = row.find("td", "losses").text.strip()
        i.save()

        print(i.to_dict())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--keyword", help="Manually specify a one-off keyword to search for.", type=str)
    parser.add_argument("-j", "--job", help="Manually specify a one-off keyword to search for.", type=str)
    parser.add_argument("-f", "--file", help="File path to a newline-deliniated list of keywords. ex: 'input/keywords.csv'", type=str)
    parser.add_argument("-w", "--worker", help="Create a worker that takes keywords off the queue", action='store_true')
    args = parser.parse_args()

    if args.keyword:
        search(args.keyword)

    if args.job:
        swap(args.keyword)

    elif args.file:
        with open(args.file, "r") as f:
            for line in f:
                enqueue_item(KEYWORD_QUEUE, line.strip())

    elif args.worker:
        while True:
            keyword = dequeue_item(KEYWORD_QUEUE)

            if not keyword:
                logging.info("Nothing left in queue")
                time.sleep(60)
                continue

            try:
                search(keyword)
            except Exception as e:
                logging.info("Encountered exception, placing keyword back into the queue: {}".format(keyword))
                enqueue_item(KEYWORD_QUEUE, keyword)
                raise e


