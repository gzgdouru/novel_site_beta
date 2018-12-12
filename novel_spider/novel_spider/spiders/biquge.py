# -*- coding: utf-8 -*-
from urllib import parse
import logging

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
# from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scrapy.http import Request

from novel_spider.items import NovelItem, ChapterItem
from novel_spider.utils.biquge_utils import get_author_by_biquge, novel_is_exists


class BiqugeSpider(CrawlSpider):
    name = 'biquge'
    allowed_domains = ['www.biquge.com.tw', 'biquge.com.tw']
    start_urls = ['http://www.biquge.com.tw/']

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "ITEM_PIPELINES": {
            # 'novel_spider.pipelines.OutPutPipeline': 1,
            'novel_spider.pipelines.NovelImagePipeline': 2,
            'novel_spider.pipelines.SaveItemPipeline': 4,
            'novel_spider.pipelines.LogComplatePipeline': 120,
        },
        "IMAGES_STORE": "/home/ouru/novel_site_beta/novel_site/media",
        "IMAGES_URLS_FIELD": "image_url",
        "USE_PROXY": True,
    }

    rules = (
        Rule(LinkExtractor(allow=r'\d+_\d+/$'), callback='parse_novel', follow=True),
        # Rule(LinkExtractor(allow=r'.*?/\d+.html'), callback='parse_chapter', follow=True,
        #      process_request="custom_process_request"),
    )

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(BiqugeSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_close, signal=signals.spider_closed)
        return spider

    def __init__(self, *args, **kwargs):
        super(BiqugeSpider, self).__init__(*args, **kwargs)

    def spider_close(self):
        self.logger.info("{0} finish.".format(self.name))

    def parse_novel(self, response):
        author_widget = response.xpath("//div[@id='info']/p[1]/text()").extract()
        author = "".join([get_author_by_biquge(author) for author in author_widget])
        novel = response.css("#info h1::text").extract_first().strip()

        # 已存在的小说不做处理
        if novel_is_exists(novel_name=novel, author_name=author):
            self.logger.info("过滤已存在的小说[{0}]".format(novel))
            return None

        item_loader = ItemLoader(item=NovelItem(), response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_css("image_url", "#fmimg img::attr(src)")
        item_loader.add_css("site_name", ".header_logo a::text")
        item_loader.add_value("novel_name", novel)
        item_loader.add_value("spider_name", self.name)
        item_loader.add_value("author", author)
        item_loader.add_css("category", ".con_top::text")
        item_loader.add_css("intro", "#intro")
        item = item_loader.load_item()
        yield item

        urls = response.css("#list dl dd a::attr(href)").extract()
        for url in urls:
            url = parse.urljoin(response.url, url)
            yield Request(url=url, dont_filter=True, meta={"novel": novel, "author": author},
                          callback=self.parse_chapter)

    def parse_chapter(self, response):
        author = response.meta.get("author", "")
        novel = response.meta.get("novel", "")

        item_loader = ItemLoader(item=ChapterItem(), response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_value("index", response.url)
        item_loader.add_css("name", ".bookname h1::text")
        item_loader.add_value("novel_name", novel)
        item_loader.add_value("author_name", author)
        item = item_loader.load_item()
        return item
