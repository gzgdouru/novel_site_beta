import aioredis
import asyncio
import time
from datetime import datetime, timedelta
import pickle

from playhouse.shortcuts import model_to_dict

from models import Novel, UserFavorite
from core import get_database_manager, get_logger, get_redis_url
import settings

objects = get_database_manager()
logger = get_logger()


async def fav_main(redis_pool):
    while True:
        logger.info("process fav_novel start...")
        total = 0
        start_time = time.time()

        favs = await objects.execute(UserFavorite.select(UserFavorite.novel_id).group_by(UserFavorite.novel_id))
        novel_ids = [fav.novel_id for fav in favs]
        novels = await objects.execute(Novel.select().where(Novel.id.in_(novel_ids)))
        for novel in novels:
            async with redis_pool.get() as redis:
                value = pickle.dumps(novel, protocol=-1)
                await redis.execute("lpush", "fav_novels", value)
                total += 1

        next_time = datetime.now() + timedelta(seconds=settings.FAV_UPDATE_INTERVAL)
        logger.info("process fav_novel finish, 共处理数据:{0}条, 耗时:{1}, 下次运行时间:{2}".format(
            total, time.time() - start_time, next_time.strftime("%Y-%m-%d %H:%M:%S")))

        await asyncio.sleep(settings.FAV_UPDATE_INTERVAL)


async def novel_main(redis_pool):
    while True:
        logger.info("process novel start...")
        total = 0
        start_time = time.time()

        favs = await objects.execute(UserFavorite.select(UserFavorite.novel_id).group_by(UserFavorite.novel_id))
        novel_ids = [fav.novel_id for fav in favs]
        novels = await objects.execute(Novel.select().where(Novel.id.not_in(novel_ids)))
        for novel in novels:
            async with redis_pool.get() as redis:
                value = pickle.dumps(novel, protocol=-1)
                await redis.execute("lpush", "novels", value)
                total += 1

        next_time = datetime.now() + timedelta(seconds=settings.NOVEL_UPDATE_INTERVAL)
        logger.info("process novel finish, 共处理数据:{0}条, 耗时:{1}, 下次运行时间:{2}".format(
            total, time.time() - start_time, next_time.strftime("%Y-%m-%d %H:%M:%S")))

        await asyncio.sleep(settings.NOVEL_UPDATE_INTERVAL)


async def main():
    redis_pool = await aioredis.create_pool(get_redis_url())
    asyncio.ensure_future(fav_main(redis_pool))
    asyncio.ensure_future(novel_main(redis_pool))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
