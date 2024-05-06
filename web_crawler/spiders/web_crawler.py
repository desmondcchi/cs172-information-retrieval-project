from typing import Iterable
import scrapy
from bs4 import BeautifulSoup
import os
from concurrent.futures import ThreadPoolExecutor

class WebCrawlerSpider(scrapy.Spider):
    name = "web_crawler"
    start_urls = []
    allowed_domains = []

    def __init__(self, *args, **kwargs):
        self.seed_file_name = str(kwargs.get("SEED_FILE_NAME", ""))
        self.allowed_domains_file_name = str(
            kwargs.get("ALLOWED_DOMAINS_FILE_NAME", "")
        )
        self.max_num_pages = int(kwargs.get("MAX_NUM_PAGES", 0))
        self.max_hops_away = int(kwargs.get("MAX_HOPS_AWAY", 0))
        self.html_pages_count = 0
        self.executor = ThreadPoolExecutor(max_workers=5)  # adjust max_workers as needed

    def start_requests(self) -> Iterable[scrapy.Request]:
        seed_urls_file = open(
            os.path.abspath(
                os.path.join(os.path.dirname(__file__), f"../../{self.seed_file_name}")
            ),
            "r",
        )

        allowed_domains_file = open(
            os.path.abspath(
                os.path.join(
                    os.path.dirname(__file__), f"../../{self.allowed_domains_file_name}"
                )
            ),
            "r",
        )

        WebCrawlerSpider.start_urls = [line.strip() for line in seed_urls_file if line.strip()]
        WebCrawlerSpider.allowed_domains = [
            line.strip() for line in allowed_domains_file if line.strip()
        ]
        for url in WebCrawlerSpider.start_urls:
            yield scrapy.Request(
                url=url, callback=self.parse, cb_kwargs={"curr_hops_away": 0}
            )

    def parse(self, response, curr_hops_away) -> Iterable[scrapy.Request]:
        if (
            self.html_pages_count >= self.max_num_pages
            or curr_hops_away > self.max_hops_away
        ):
            return

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.find("title").text.strip()
        main_content = soup.find("main").get_text(strip=True)
        header_content = soup.find("header").get_text(strip=True)
        footer_content = soup.find("footer").get_text(strip=True)

        # Save data into json.
        yield {
            "title": title,
            "url": response.url,
            "main_content": main_content,
            "header_content": header_content,
            "footer_content": footer_content,
        }

        # Write page content into a folder.
        # file_name = os.path.abspath(
        #     os.path.join(
        #         os.path.dirname(__file__), f"../../{self.output_dir_name}/{title}.html"
        #     )
        # )

        # if not os.path.exists(os.path.dirname(file_name)):
        #     os.makedirs(os.path.dirname(file_name))

        # file = open(file_name, "wb")
        # file.write(response.body)
        # file.close()
        
        self.html_pages_count += 1

        # Get all links on current HTML page.
        all_links = soup.find_all("a")
        extracted_links = []
        for link in all_links:
            href = link.get("href")
            if href.startswith("http"):
                extracted_links.append(href)

        # Submit tasks to ThreadPoolExecutor
        futures = []
        for url in extracted_links:
            futures.append(
                self.executor.submit(self.fetch_url, url, curr_hops_away)
            )

        # Wait for all tasks to complete
        for future in futures:
            for request in future.result():
                yield request

    def fetch_url(self, url, curr_hops_away):
        response = scrapy.Request(url=url)
        return self.parse(response, curr_hops_away)