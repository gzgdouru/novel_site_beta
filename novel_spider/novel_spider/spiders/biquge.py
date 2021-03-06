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
from novel_spider.utils.biquge_utils import get_author_by_biquge, get_category_by_biquge, get_chapter_index_by_biquge
from novel_spider.utils.public_utils import novel_is_exists


class BiqugeSpider(CrawlSpider):
    name = 'biquge'
    allowed_domains = ['www.biquyun.com', 'biquyun.com']
    start_urls = ['http://www.biquyun.com/']

    custom_settings = {
        "DOWNLOAD_DELAY": 0.5,
        "USE_PROXY": False,
        "IGNORE_NOVEL": set({}),
        "RETAIN_NOVEL": set({}),
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

        category = response.xpath("//div[@class='con_top']/a[2]/text()").extract_first()
        if not category:
            categories = response.css(".con_top::text").extract()
            category = get_category_by_biquge("".join(categories))
        category = category or "其他小说"
        item_loader.add_value("category", category)

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

        index = get_chapter_index_by_biquge(response.url)
        item_loader.add_value("index", index)

        item_loader.add_css("name", ".bookname h1::text")
        item_loader.add_value("novel_name", novel)
        item_loader.add_value("author_name", author)
        item = item_loader.load_item()
        return item
