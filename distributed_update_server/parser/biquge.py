import asyncio
import time

from scrapy.selector import Selector
from tornado import curl_httpclient
from peewee import fn

from core import get_logger, get_database_manager
from models import Proxys
from settings import USE_PROXY, ERR_PREFIX

logger = get_logger()
objects = get_database_manager()
http_client = curl_httpclient.CurlAsyncHTTPClient()


async def async_get_html(url, delay_time=0, headers=None):
    await asyncio.sleep(delay_time)
    try:
        if USE_PROXY:
            proxy = await objects.execute(Proxys.select().where(Proxys.score > 0).order_by(fn.Rand()).limit(1))
            if proxy:
                response = await http_client.fetch(url, headers=headers, proxy_host=proxy[0].ip,
                                                   proxy_port=proxy[0].port)
            else:
                response = await http_client.fetch(url, headers=headers)
        else:
            response = await http_client.fetch(url, headers=headers)
        html = response.body.decode("gbk")
    except Exception as e:
        raise RuntimeError("{0}async_get_html({1}) fail, error:{2}".format(ERR_PREFIX, url, e))
    return html


def get_html(session, url, delay_time=0, headers=None):
    time.sleep(delay_time)
    try:
        if USE_PROXY:
            proxy = Proxys.select().where(Proxys.score > 0).order_by(fn.Rand()).limit(1)
            if proxy:
                proxy_ip = "http://{0}:{1}".format(proxy[0].ip, proxy[0].port)
                response = session.get(url, headers=headers, proxies={"https": proxy_ip})
            else:
                response = session.get(url, headers=headers)
        else:
            response = session.get(url, headers=headers)
        response.encoding = "gbk"
    except Exception as e:
        raise RuntimeError("{0}get_html({1}) fail, error:{2}".format(ERR_PREFIX, url, e))
    return response.text


def parse_chapter(html):
    try:
        selector = Selector(text=html)
        name = selector.css(".bookname h1::text").extract_first().strip()
        return name
    except Exception as e:
        raise RuntimeError("{0}parse_chapter() fail, error:{1}".format(ERR_PREFIX, e))


def parse_novel(html):
    try:
        selector = Selector(text=html)
        urls = selector.css("#list dl dd a::attr(href)").extract()
        yield from urls
    except Exception as e:
        raise RuntimeError("{0}parse_novel() fail, error:{1}".format(ERR_PREFIX, e))
