import asyncio
from urllib import parse
import time
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

from tornado import httpclient
from scrapy.selector import Selector
from fake_useragent import UserAgent
import requests

from core import get_database_manager, get_logger
from models import UserFavorite, Novel, Chapter, UserProfile, UserMessage
import utils, asyncUtils
import settings
from parser import biquge

objects = get_database_manager()
logger = get_logger()
async_semaphore = asyncio.Semaphore(settings.CONCURRENT_REQUESTS)
novel_parser = {
    "biquge": biquge,
}

ua = UserAgent()
headers = {
    "User-Agent": ua.random,
}


def update_notice(novel):
    favs = UserFavorite.select().where((UserFavorite.novel_id == novel.id) & (UserFavorite.notice_enable > 0))

    for fav in favs:
        user = UserProfile.get_by_id(fav.user_id)
        if user.email:
            subject = "小说更新通知"
            utils.send_update_online_email(subject, user.email, novel.novel_name)
        elif user.mobile:
            utils.send_update_sms(user.mobile, novel.novel_name)
        else:
            try:
                message = "您收藏的小说({0})已经有更新了, 请前往阅读.".format(novel.novel_name)
                UserMessage.create(message=message, user_id=user.id)
                logger.info("发送小说[{0}]更新消息给用户[{1}]成功".format(novel.novel_name, user.username))
            except Exception as e:
                logger.error("发送小说[{0}]更新消息给用户[{1}]失败, 原因:{2}".format(novel.novel_name, user.username, e))


async def novel_update(novel):
    async with async_semaphore:
        send_notice = False
        logger.info("更新小说[{0}]开始...".format(novel.novel_name))
        start_time = time.time()

        try:
            parser_obj = novel_parser[novel.spider_name]
        except KeyError as e:
            logger.error("不存在的解析器:{0}".format(novel.spider_name))
            logger.info("更新小说[{0}]结束, 耗时:{1}".format(novel.novel_name, time.time() - start_time))
            return

        try:
            chapters = await objects.execute(Chapter.select(Chapter.chapter_url).where(Chapter.novel_id == novel.id))
            filter_urls = set([chapter.chapter_url for chapter in chapters])
            html = await parser_obj.async_get_html(novel.url, delay_time=settings.DOWNLOAD_DELAY, headers=headers)
            urls = parser_obj.parse_novel(html, novel.novel_name)
            for url in urls:
                url = parse.urljoin(novel.url, url)
                if url in filter_urls:
                    continue
                html = await parser_obj.async_get_html(url, delay_time=settings.DOWNLOAD_DELAY, headers=headers)
                chapter_name = parser_obj.parse_chapter(html, novel.novel_name)
                chapter_index = utils.get_index_by_chapter(url)
                try:
                    await objects.create(Chapter, chapter_url=url, chapter_name=chapter_name,
                                         chapter_index=chapter_index, novel_id=novel.id)
                    logger.info("保存[{0}:{1}]到数据库成功.".format(novel.novel_name, chapter_name))
                    send_notice = True
                except Exception as e:
                    logger.error("保存[{0}:{1}:{2}]到数据库失败, 原因:{3}".format(novel.novel_name, chapter_index, url, e))
        except Exception as e:
            logger.error("更新小说[{0}]失败, 原因:{1}".format(novel.novel_name, e))
        logger.info("更新小说[{0}]结束, 耗时:{1}".format(novel.novel_name, time.time() - start_time))


def fav_update(session, novel):
    send_notice = False
    logger.info("更新用户收藏小说[{0}]开始...".format(novel.novel_name))
    start_time = time.time()

    try:
        parser_obj = novel_parser[novel.spider_name]
    except KeyError as e:
        logger.error("不存在的解析器:{0}".format(novel.spider_name))
        logger.info("更新用户收藏小说[{0}]结束, 耗时:{1}".format(novel.novel_name, time.time() - start_time))
        return

    try:
        chapters = Chapter.select(Chapter.chapter_url).where(Chapter.novel_id == novel.id)
        filter_urls = set([chapter.chapter_url for chapter in chapters])
        html = parser_obj.get_html(session, novel.url, delay_time=settings.DOWNLOAD_DELAY, headers=headers)
        urls = parser_obj.parse_novel(html, novel.novel_name)
        for url in urls:
            url = parse.urljoin(novel.url, url)
            if url in filter_urls:
                continue
            html = parser_obj.get_html(session, url, delay_time=settings.DOWNLOAD_DELAY, headers=headers)
            chapter_name = parser_obj.parse_chapter(html, novel.novel_name)
            chapter_index = utils.get_index_by_chapter(url)
            try:
                Chapter.create(chapter_url=url, chapter_name=chapter_name, chapter_index=chapter_index,
                               novel_id=novel.id)
                logger.info("保存[{0}:{1}]到数据库成功.".format(novel.novel_name, chapter_name))
                send_notice = True
            except Exception as e:
                logger.error("保存[{0}:{1}:{2}]到数据库失败, 原因:{3}".format(novel.novel_name, chapter_index, url, e))
    except Exception as e:
        logger.error("更新用户收藏小说[{0}]失败, 原因:{1}".format(novel.novel_name, e))
    logger.info("更新用户收藏小说[{0}]结束, 耗时:{1}".format(novel.novel_name, time.time() - start_time))

    try:
        if send_notice:
            update_notice(novel)
        else:
            logger.info("小说[{0}]无更新.".format(novel.novel_name))
    except Exception as e:
        logger.error("发送小说[{0}]更新同时失败, 原因:{1}".format(novel.novel_name, e))


async def novel_update_main():
    while True:
        start_time = time.time()
        logger.info("小说更新服务开启....")

        favs = await objects.execute(UserFavorite.select(UserFavorite.novel_id).group_by(UserFavorite.novel_id))
        novel_ids = [fav.novel_id for fav in favs]
        novels = await objects.execute(Novel.select().where(Novel.id.not_in(novel_ids)))
        tasks = [asyncio.ensure_future(novel_update(novel)) for novel in novels]
        for task in asyncio.as_completed(tasks):
            await task

        next_time = datetime.now() + timedelta(seconds=settings.NOVEL_UPDATE_INTERVAL)
        logger.info("小说更新服务结束, 耗时:{0}, 下次将于{1}更新.".format(time.time() - start_time,
                                                          next_time.strftime("%Y-%m-%d %H:%M:%S")))
        await asyncio.sleep(settings.NOVEL_UPDATE_INTERVAL)


async def fav_update_main():
    while True:
        with requests.Session() as session:
            start_time = time.time()
            logger.info("用户收藏小说更新服务开启....")

            favs = await objects.execute(UserFavorite.select(UserFavorite.novel_id).group_by(UserFavorite.novel_id))
            novel_ids = [fav.novel_id for fav in favs]
            novels = await objects.execute(Novel.select().where(Novel.id.in_(novel_ids)))
            loop = asyncio.get_event_loop()
            executor = ThreadPoolExecutor(settings.CONCURRENT_REQUESTS)
            tasks = [loop.run_in_executor(executor, fav_update, session, novel) for novel in novels]
            for task in asyncio.as_completed(tasks):
                await task

            next_time = datetime.now() + timedelta(seconds=settings.FAV_UPDATE_INTERVAL)
            logger.info("用户收藏小说更新服务结束, 耗时:{0}, 下次将于{1}更新.".format(time.time() - start_time,
                                                                  next_time.strftime("%Y-%m-%d %H:%M:%S")))
        await asyncio.sleep(settings.FAV_UPDATE_INTERVAL)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(novel_update_main())
    loop.create_task(fav_update_main())
    loop.run_forever()
