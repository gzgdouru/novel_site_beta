# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import logging
from urllib import parse
import os

from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request
from scrapy.exceptions import DropItem

from novel_spider.items import ChapterItem
from novel_spider.models import Novel


class SiteCrawlerPipeline(object):
    def process_item(self, item, spider):
        return item


class OutPutPipeline(object):
    def process_item(self, item, spider):
        logger = logging.getLogger(spider.name)
        logger.info(item)
        return item


class SaveItemPipeline(object):
    def process_item(self, item, spider):
        if hasattr(item, "save_item"):
            err_msg = item.save_item()
            if err_msg:
                spider.logger.error(err_msg)
            else:
                spider.logger.info("保存{0}成功.".format(item))
        return item


class NovelImagePipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if "image_url" in item:
            item["image_url"] = [parse.urljoin(item["url"], image_url) for image_url in item["image_url"]]
            return [Request(x) for x in item.get(self.images_urls_field, [])]

    def file_path(self, request, response=None, info=None):
        path = super(NovelImagePipeline, self).file_path(request, response, info)
        return path.replace("full/", "")

    def item_completed(self, results, item, info):
        for ok, value in results:
            if ok:
                item["image_path"] = value["path"]
            else:
                info.spider.logger.error("下载图片({0})失败!".format(item["image_url"]))
        return item


class LogComplatePipeline(object):
    def __init__(self, crawler):
        self.crawler = crawler

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        spider.logger.info("process url:{0} finish.".format(item["url"]))
        return item


class RestrictionPipeline(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self.ignore_novel = crawler.settings.get("IGNORE_NOVEL")
        self.retain_novel = crawler.settings.get("RETAIN_NOVEL")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_item(self, item, spider):
        novel_name = item.get("novel_name")
        if novel_name:
            if self.ignore_novel and novel_name in self.ignore_novel:
                raise DropItem("过滤[{0}], 原因:满足小说忽略规则.".format(item))

            if self.retain_novel and novel_name not in self.retain_novel:
                raise DropItem("过滤[{0}], 原因:不满足小说保留规则.".format(item))

        return item
