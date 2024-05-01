from typing import Iterable
import scrapy
from bs4 import BeautifulSoup
import os


class WebCrawlerSpider(scrapy.Spider):
    name = "web_crawler"
    # allowed_domains = ["example.com"]
    seed_urls = ["https://www.github.com/desmondcchi"]

    def __init__(self, *args, **kwargs):
        # super(WebCrawlerSpider, self).__init__(*args, **kwargs)
        self.output_dir_name = kwargs.get("OUTPUT_DIR_NAME", "scraped_html_data")

    def start_requests(self) -> Iterable[scrapy.Request]:
        for url in self.seed_urls:
            yield scrapy.Request(url=url, callback=self.parse)

        # return super().start_requests()

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
