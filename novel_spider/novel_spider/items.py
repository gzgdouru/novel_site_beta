# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst, MapCompose, Join, Identity
from scrapy_djangoitem import DjangoItem

from novel_spider.utils.biquge_utils import get_category_by_biquge, get_author_by_biquge, get_chapter_index_by_biquge, \
    novel_is_exists, chapter_is_exists
from novel_spider.models import Novel, Category, Chapter, Author


class SiteCrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class NovelItem(scrapy.Item):
    site_name = scrapy.Field(output_processor=TakeFirst())
    novel_name = scrapy.Field(output_processor=TakeFirst())
    spider_name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    image_url = scrapy.Field()
    image_path = scrapy.Field()
    author = scrapy.Field(output_processor=TakeFirst())
    category = scrapy.Field(input_processor=MapCompose(get_category_by_biquge), output_processor=Join(""))
    intro = scrapy.Field(output_processor=TakeFirst())

    def save_item(self):
        author = Author.select().where(Author.name == self.get("author")).first()
        if author:
            if Novel.select().where((Novel.novel_name == self.get("novel_name")) & (Novel.author == author)).exists():
                return "小说[{0}]已存在".format(self.get("novel_name"))
        else:
            author = Author()
            author.name = self.get("author")
            author.save()

        novel = Novel()
        novel.site_name = self.get("site_name")
        novel.novel_name = self.get("novel_name")
        novel.spider_name = self.get("spider_name")
        novel.url = self.get("url")

        category = Category.select().where(Category.name == self.get("category")).first()
        if not category:
            category = Category(name=self.get("category"))
            category.save()
        novel.category = category

        novel.image_url = ",".join(self.get("image_url"))
        novel.image_path = self.get("image_path", "")
        novel.author = author

        novel.intro = self.get("intro")
        novel.save()

    def __str__(self):
        return "[{0}]".format(self.get("novel_name"))


class ChapterItem(scrapy.Item):
    novel_name = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    index = scrapy.Field(input_processor=MapCompose(get_chapter_index_by_biquge), output_processor=TakeFirst())
    name = scrapy.Field(output_processor=TakeFirst())
    author_name = scrapy.Field(output_processor=TakeFirst())

    def save_item(self):
        author = Author.select().where(Author.name == self.get("author_name")).first()
        if not author:
            return "保存章节[{0}]失败, 原因:小说作者{1}不存在!".format(self.get("name"), self.get("author_name"))

        novel = Novel.select().where((Novel.novel_name == self.get("novel_name")) & (Novel.author == author)).first()
        if not novel:
            return "保存章节[{0}]失败, 原因:小说{1}不存在!".format(self.get("name"), self.get("novel_name"))

        chapter = Chapter()
        chapter.novel = novel
        chapter.chapter_url = self.get("url")
        chapter.chapter_index = self.get("index")
        chapter.chapter_name = self.get("name")
        chapter.save()

    def __str__(self):
        return "[{0}:{1}]".format(self.get("novel_name"), self.get("name"))
