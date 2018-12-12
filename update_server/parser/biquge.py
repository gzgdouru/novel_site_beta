import asyncio
import time

from scrapy.selector import Selector
from tornado import curl_httpclient
from peewee import fn

from core import get_logger, get_database_manager
from models import Proxys

logger = get_logger()
objects = get_database_manager()
http_client = curl_httpclient.CurlAsyncHTTPClient()


async def async_get_html(url, delay_time=0, headers=None):
    await asyncio.sleep(delay_time)
    proxy = await objects.execute(Proxys.select().where(Proxys.score > 0).order_by(fn.Rand()).limit(1))
    if proxy:
        response = await http_client.fetch(url, headers=headers, proxy_host=proxy.ip, proxy_port=proxy.port)
    else:
        response = await http_client.fetch(url, headers=headers)
    return response.body.decode("gbk")


def get_html(session, url, delay_time=0, headers=None):
    time.sleep(delay_time)
    proxy = Proxys.select().where(Proxys.score > 0).order_by(fn.Rand()).limit(1)
    if proxy:
        proxy_ip = "http://{0}:{1}".format(proxy.ip, proxy.port)
        response = session.get(url, headers=headers, proxies={"https": proxy_ip})
    else:
        response = session.get(url, headers=headers)
    response.encoding = "gbk"
    return response.text


def parse_chapter(html, novel_name):
    try:
        selector = Selector(text=html)
        name = selector.css(".bookname h1::text").extract_first().strip()
        return name
    except Exception as e:
        logger.error("(biquge)解析小说[{0}]章节失败, 原因:{1}".format(novel_name, e))


def parse_novel(html, novel_name):
    try:
        selector = Selector(text=html)
        urls = selector.css("#list dl dd a::attr(href)").extract()
        yield from urls
    except Exception as e:
        logger.error("解析小说[{0}]信息失败, 原因:{1}".format(novel_name, e))
    return []
