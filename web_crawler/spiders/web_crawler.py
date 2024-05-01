from typing import Iterable
import scrapy
from bs4 import BeautifulSoup
import os


class WebCrawlerSpider(scrapy.Spider):
    name = "web_crawler"

    def __init__(self, *args, **kwargs):
        self.seed_file_name = kwargs.get("SEED_FILE_NAME", "")
        self.num_pages = kwargs.get("NUM_PAGES", 0)
        self.hops_away = kwargs.get("HOPS_AWAY", 0)
        self.output_dir_name = kwargs.get("OUTPUT_DIR_NAME", "scraped_html_pages")

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

    def parse(self, response):
        soup = BeautifulSoup(response.text, "html.parser")

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
