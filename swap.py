import logging
from linkedin_jobs_scraper.events.events import EventData, EventMetrics, Events
from linkedin_jobs_scraper.filters.filters import ExperienceLevelFilters, OnSiteOrRemoteFilters, RelevanceFilters, SourceType, TimeFilters, TypeFilters
from linkedin_jobs_scraper.linkedin_scraper import LinkedinScraper
from linkedin_jobs_scraper.query.query import Query, QueryFilters, QueryOptions
from utils import logging
from models import BaseJobPosting
import random

count = 0
# Fired once for each successfully processed job
def on_data(data: EventData):
    global count
    count+=1
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
    job.description_length = len(data.description)
    job.save()


def on_metrics(metrics: EventMetrics):
    print('[ON_METRICS]', str(metrics))


def on_error(error):
    print('[ON_ERROR]', error)


def on_end():
    global count
    print('[ON_END] Scraping Complete.',count,'data points scraped successfully.')

def startLinkedInScrap(): 
    source = SourceType.LINKEDIN
    logging.basicConfig(level=logging.INFO)
    logging.info(u"Searching for keyword: {}".format(source))

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
            query='Developer',
            options=QueryOptions(
                locations=['India'],
                apply_link=True,  # Try to extract apply link (easy applies are skipped). If set to True, scraping is slower because an additional page must be navigated. Default to False.
                skip_promoted_jobs=True,  # Skip promoted jobs. Default to False.
                page_offset=2,  # How many pages to skip
                limit=5,
                filters=QueryFilters(
                    company_jobs_url='https://www.linkedin.com/jobs/search/?f_C=1441%2C17876832%2C791962%2C2374003%2C18950635%2C16140%2C10440912&geoId=92000000',  # Filter by companies.                
                    relevance=RelevanceFilters.RECENT,
                    time=TimeFilters.MONTH,
                    type=random.choice(TypeFilters),
                    on_site_or_remote=random.choice(OnSiteOrRemoteFilters),
                    experience=random.choice(ExperienceLevelFilters)
                )
            )
        ),
    ]
    scraper.run(queries)


if __name__ == '__main__':
    
    startLinkedInScrap()



