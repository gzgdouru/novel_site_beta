import asyncio
from urllib import parse
import time
import pickle

from fake_useragent import UserAgent
import aioredis
from playhouse.shortcuts import dict_to_model

from core import get_database_manager, get_logger, get_redis_url
from models import UserFavorite, Novel, Chapter, UserProfile, UserMessage
from utils import get_index_by_chapter, send_update_online_email, send_update_sms
import settings
from parser import biquge, dingdian

objects = get_database_manager()
logger = get_logger()
async_semaphore = asyncio.Semaphore(settings.CONCURRENT_REQUESTS)

novel_parser = {
    "biquge": biquge,
    "dingdian": dingdian,
}

ua = UserAgent()
headers = {
    "User-Agent": ua.random,
}


async def update_notice(novel):
    favs = await objects.execute(
        UserFavorite.select().where((UserFavorite.novel_id == novel.id) & (UserFavorite.notice_enable > 0)))

    for fav in favs:
        user = await objects.execute(UserProfile.get_by_id(fav.user_id))
        if user.email:
            subject = "小说更新通知"
            await send_update_online_email(subject, user.email, novel.novel_name)
        elif user.mobile:
            await send_update_sms(user.mobile, novel.novel_name)
        else:
            try:
                message = "您收藏的小说({0})已经有更新了, 请前往阅读.".format(novel.novel_name)
                objects.create(UserMessage, message=message, user_id=user.id)
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
            urls = parser_obj.parse_novel(html)
            for url in urls:
                url = parse.urljoin(novel.url, url)
                if url in filter_urls:
                    continue

                try:
                    html = await parser_obj.async_get_html(url, delay_time=settings.DOWNLOAD_DELAY, headers=headers)
                    chapter_name = parser_obj.parse_chapter(html)
                except Exception as e:
                    logger.error(f"解析小说【{novel.novel_name}】章节【{url}】失败, 原因:{e}")

                chapter_index = get_index_by_chapter(url)

                try:
                    await objects.create(Chapter, chapter_url=url, chapter_name=chapter_name,
                                         chapter_index=chapter_index, novel_id=novel.id)
                    logger.info("保存[{0}:{1}]到数据库成功.".format(novel.novel_name, chapter_name))
                except Exception as e:
                    logger.error("保存[{0}:{1}:{2}]到数据库失败, 原因:{3}".format(novel.novel_name, chapter_index, url, e))
        except Exception as e:
            logger.error("更新小说[{0}]失败, 原因:{1}".format(novel.novel_name, e))
        logger.info("更新小说[{0}]结束, 耗时:{1}".format(novel.novel_name, time.time() - start_time))


async def fav_update(novel):
    async with async_semaphore:
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
            chapters = await objects.execute(Chapter.select(Chapter.chapter_url).where(Chapter.novel_id == novel.id))
            html = await parser_obj.async_get_html(novel.url, delay_time=settings.DOWNLOAD_DELAY, headers=headers)
            urls = parser_obj.parse_novel(html)
            filter_urls = set([chapter.chapter_url for chapter in chapters])
            for url in urls:
                url = parse.urljoin(novel.url, url)
                if url in filter_urls:
                    continue

                try:
                    html = await parser_obj.async_get_html(url, delay_time=settings.DOWNLOAD_DELAY, headers=headers)
                    chapter_name = parser_obj.parse_chapter(html)
                except Exception as e:
                    logger.error(f"解析小说【{novel.novel_name}】章节url【{url}】失败, 原因:{e}")
                    continue

                chapter_index = get_index_by_chapter(url)

                try:
                    objects.create(Chapter, chapter_url=url, chapter_name=chapter_name, chapter_index=chapter_index,
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


async def novel_update_main(redis_pool):
    logger.info("小说更新服务启动成功....")
    while True:
        async with redis_pool.get() as redis:
            novel = await redis.execute("brpop", "novels", "0")
            novel = pickle.loads(novel[1])
            # novel = dict_to_model(Novel, novel)
            asyncio.ensure_future(novel_update(novel))


async def fav_update_main(redis_pool):
    logger.info("用户收藏小说更新服务开启....")
    while True:
        async with redis_pool.get() as redis:
            novel = await redis.execute("brpop", "fav_novels", "0")
            novel = pickle.loads(novel[1])
            # novel = dict_to_model(Novel, novel)
            asyncio.ensure_future(fav_update(novel))


async def main():
    redis_pool = await aioredis.create_pool(get_redis_url())
    asyncio.ensure_future(fav_update_main(redis_pool))
    asyncio.ensure_future(novel_update_main(redis_pool))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
