# V1.1 with random User Agents and Proxies implemented

import scrapy
import json
import random

from scrapy.crawler import CrawlerProcess


class RandomUserAgentMiddleware:
    def __init__(self, user_agents):
        self.user_agents = user_agents

    @classmethod
    def from_crawler(cls, crawler):
        ua_list = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1'
        ]
        return cls(ua_list)

    def process_request(self, request, spider):
        ua = random.choice(self.user_agents)
        request.headers.setdefault('User-Agent', ua)
        spider.logger.debug(f"Using User-Agent: {ua}")

class ProxyMiddleware:
    def __init__(self, proxy_file):
        try:
            with open(proxy_file, 'r') as f:
                self.proxies = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            self.proxies = []

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.get('PROXY_FILE'))

    def process_request(self, request, spider):
        if self.proxies:
            proxy = random.choice(self.proxies)
            if not proxy.startswith(('http://', 'https://')):
                proxy = f"http://{proxy}"
            request.meta['proxy'] = proxy

class MultiFileOutputPipeline:
    def open_spider(self, spider):
        self.html_file = open('data_html.jsonl', 'a', encoding='utf-8')
        self.json_file = open('data_json.jsonl', 'a', encoding='utf-8')

    def close_spider(self, spider):
        self.html_file.close()
        self.json_file.close()

    def process_item(self, item, spider):
        line = json.dumps(dict(item), ensure_ascii=False) + "\n"
        if item.get('data_type') == 'html':
            self.html_file.write(line)
        else:
            self.json_file.write(line)
        return item

class ProductionSpider(scrapy.Spider):
    name = "fuzz_scraper"
    
    def __init__(self, target_url=None, wordlist_path='wordlist.txt', *args, **kwargs):
        super(ProductionSpider, self).__init__(*args, **kwargs)
        self.start_urls = [target_url] if target_url else []
        self.base_url = target_url.rstrip('/') if target_url else ""
        self.wordlist_path = wordlist_path

    async def start(self):
        for url in self.start_urls:
            yield scrapy.Request(url, callback=self.parse_html)
            
            try:
                with open(self.wordlist_path, 'r') as f:
                    for line in f:
                        path = line.strip().lstrip('/')
                        if path:
                            yield scrapy.Request(f"{self.base_url}/{path}", callback=self.detect_content_type)
            except FileNotFoundError:
                self.logger.error("Wordlist not found.")

    def detect_content_type(self, response):
        ctype = response.headers.get('Content-Type', b'').decode('utf-8').lower()
        if 'application/json' in ctype:
            return self.parse_json(response)
        return self.parse_html(response)

    def parse_html(self, response):
        yield {
            'url': response.url,
            'title': response.css('title::text').get(),
            'data_type': 'html',
            'status': response.status
        }
        for link in response.css('a::attr(href)').getall():
            yield response.follow(link, callback=self.parse_html)

    def parse_json(self, response):
        try:
            yield {
                'url': response.url,
                'payload': json.loads(response.text),
                'data_type': 'json',
                'status': response.status
            }
        except:
            pass

if __name__ == "__main__":
    process = CrawlerProcess(settings={
        'PROXY_FILE': 'proxies.txt',
        'DOWNLOADER_MIDDLEWARES': {
            '__main__.RandomUserAgentMiddleware': 400,
            '__main__.ProxyMiddleware': 410,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
        },
        'ITEM_PIPELINES': {
            '__main__.MultiFileOutputPipeline': 300,
        },
        'CONCURRENT_REQUESTS': 16,
        'DOWNLOAD_TIMEOUT': 10,
        'LOG_LEVEL': 'INFO',
    })

    process.crawl(ProductionSpider, target_url='https://books.toscrape.com/', wordlist_path='wordlist.txt')
    process.start()