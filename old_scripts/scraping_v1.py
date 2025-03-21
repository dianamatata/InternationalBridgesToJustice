import scrapy
from scrapy.utils.project import get_project_settings
import logging
settings = get_project_settings()

import scrapy
from scrapy.utils.project import get_project_settings
import logging


class MostRevisionsSpider(scrapy.Spider):
    name = 'extract_defensewiki'
    start_urls = ['https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=20&offset=0']
    start_urls = ['https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=100&offset=0']
    start_urls = ['https://defensewiki.ibj.org/index.php?title=Special:MostRevisions&limit=2000&offset=0'] # Showing below up to 1,251 results in range #1 to #1,251.


    def parse(self, response):
        # Step 1: Extract all the links from the list
        links = response.css('ol.special li a::attr(href)').extract()

        # List to store valid links
        valid_links = []

        # Step 2: Visit each page by following the links
        for link in links:
            # Filter out links that contain '&action=history'
            if '&action=history' not in link:
                # Construct the full URL for the page
                full_url = response.urljoin(link)
                self.logger.debug(f'Found link: {full_url}')
                valid_links.append(full_url)  # Add valid link to the list

        self.logger.info(f"\033[91mTotal valid links found: {len(valid_links)}\033[0m")  # Red color

        # Step 3: Yield requests for each valid link
        for valid_link in valid_links[:100]:  # You can remove slicing to yield all links
            self.logger.info(f"\033[91mFetching: {valid_link}\033[0m")  # Red color
            yield scrapy.Request(valid_link, callback=self.parse_page, dont_filter=True)

    def parse_page(self, response):
        # self.logger.info(f"\033[91mProcessing page: {response.url}\033[0m")  # Red color

        # Save the HTML of the page to a file
        page_name = response.url.split('title=')[1].split('&')[0]  # Extract page name from URL
        filename = f'/Users/dianaavalos/PycharmProjects/InternationalBridgesToJustice/html_pages/defensewiki.ibj.org/page_{page_name}.html'

        with open(filename, 'wb') as f:
            f.write(response.body)  # Write the HTML content to the file
        self.logger.info(f"\033[91mSaved page {response.url} to {filename}\033[0m")  # Red color

# call in bash
# python -m scrapy crawl extract_defensewiki --loglevel=DEBUG -s CONCURRENT_REQUESTS=5

# scrapy crawl extract_defensewiki -s CONCURRENT_REQUESTS=5

# scrapy crawl extract_defensewiki --set=DEFAULT_SETTINGS_MODULE=defensewiki.settings
# scrapy crawl extract_defensewiki --set=LOG_LEVEL=DEBUG

