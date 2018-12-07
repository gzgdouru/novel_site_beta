import asyncio
from urllib import parse
import time
from datetime import datetime, timedelta

from tornado import httpclient
from scrapy.selector import Selector

from core import get_database_manager, get_logger
from models import UserFavorite, Novel, Chapter
from utils import get_index_by_chapter
import settings

objects = get_database_manager()
logger = get_logger()
http_client = httpclient.AsyncHTTPClient()
semaphore = asyncio.Semaphore(settings.CONCURRENT_REQUESTS)


async def get_html(url, encoding="utf-8"):
    await asyncio.sleep(settings.DOWNLOAD_DELAY)
    response = await http_client.fetch(url)
    return response.body.decode(encoding)


async def parse_chapter(url):
    try:
        html = await get_html(url, encoding="gbk")
        selector = Selector(text=html)
        index = get_index_by_chapter(url)
        name = selector.css(".bookname h1::text").extract_first().strip()
        return name, index
    except Exception as e:
        logger.error("parse_chapter({0})失败, 原因:{1}".format(url, e))


async def parse_novel(url):
    try:
        html = await get_html(url, encoding="gbk")
        response = await http_client.fetch(url)
        selector = Selector(text=html)
        urls = selector.css("#list dl dd a::attr(href)").extract()
        return urls
    except Exception as e:
        logger.error("parse_novel({0}) 失败, 原因:{1}".format(url, e))
    return []


async def novel_update(novel):
    async with semaphore:
        send_notice = False
        logger.info("更新小说[{0}]开始...".format(novel.novel_name))
        start_time = time.time()
        chapters = await objects.execute(Chapter.select(Chapter.chapter_url).where(Chapter.novel_id == novel.id))
        filter_urls = set([chapter.chapter_url for chapter in chapters])
        urls = await parse_novel(novel.url)
        for url in urls:
            url = parse.urljoin(novel.url, url)
            if url in filter_urls:
                continue
            send_notice = True
            chapter_info = await parse_chapter(url)
            if not chapter_info:
                continue
            try:
                await objects.create(Chapter, chapter_url=url, chapter_name=chapter_info[0],
                                     chapter_index=chapter_info[1], novel_id=novel.id)
                logger.info("保存[{0}:{1}]到数据库成功.".format(novel.novel_name, chapter_info[0]))
            except Exception as e:
                logger.error("保存[{0}:{1}]到数据库失败, 原因:{2}".format(novel.novel_name, chapter_info[0], e))
        logger.info("更新小说[{0}]结束, 耗时:{1}".format(novel.novel_name, time.time() - start_time))

        if send_notice:
            logger.info("发送小说[{0}]更新通知给用户.".format(novel.novel_name))
        else:
            logger.info("小说[{0}]无更新.".format(novel.novel_name))


async def main():
    while True:
        novels = await objects.execute(Novel.select())
        tasks = [asyncio.ensure_future(novel_update(novel)) for novel in novels]
        for task in asyncio.as_completed(tasks):
            await task

        next_time = datetime.now() + timedelta(seconds=settings.UPDATE_INTERVAL)
        logger.info("休眠{0}秒, 下次将于{1}更新.".format(settings.UPDATE_INTERVAL, next_time.strftime("%Y-%m-%d %H:%M:%S")))
        await asyncio.sleep(settings.UPDATE_INTERVAL)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
