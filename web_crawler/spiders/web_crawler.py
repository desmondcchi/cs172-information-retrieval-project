from typing import Iterable
import scrapy
from bs4 import BeautifulSoup
import os


class WebCrawlerSpider(scrapy.Spider):
    name = "web_crawler"

    def __init__(self, *args, **kwargs):
        self.seed_file_name = str(kwargs.get("SEED_FILE_NAME", ""))
        self.num_pages = int(kwargs.get("NUM_PAGES", 0))
        self.hops_away = int(kwargs.get("HOPS_AWAY", 0))
        self.output_dir_name = str(kwargs.get("OUTPUT_DIR_NAME", "scraped_html_pages"))
        self.html_pages_count = 0
        self.visited_urls = set()

    def start_requests(self) -> Iterable[scrapy.Request]:
        seed_urls_file = open(
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), f"../../{self.seed_file_name}")
            ),
            "r",
        )

        self.start_urls = [line.strip() for line in seed_urls_file if line.strip()]
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response) -> Iterable[scrapy.Request]:
        if self.html_pages_count >= self.num_pages:
            return

        soup = BeautifulSoup(response.text, "html.parser")

        # Write HTML page into a folder.
        title = soup.find("title").text.strip()
        file_name = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), f"../../{self.output_dir_name}/{title}.html"
            )
        )

        if not os.path.exists(os.path.dirname(file_name)):
            os.makedirs(os.path.dirname(file_name))

        file = open(file_name, "wb")
        file.write(response.body)
        file.close()
        self.html_pages_count += 1
        self.visited_urls.add(response.url)

        if self.html_pages_count >= self.num_pages:
            return

        # Get all links on current HTML page.
        all_links = soup.find_all("a")
        extracted_links = []
        for link in all_links:
            href = link.get("href")
            if href.startswith("http"):
                extracted_links.append(href)

        # Follow (continue crawling) all extracted links.
        for url in extracted_links:
            yield scrapy.Request(url=url, callback=self.parse)
