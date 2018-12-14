import requests
from scrapy.selector import Selector


def biquge(chapter_url):
    response = requests.get(url=chapter_url, timeout=30)
    response.encoding = "gbk"
    selector = Selector(text=response.text)
    chapter_content = selector.css("#content").extract_first()
    return chapter_content


def dingdian(chapter_url):
    response = requests.get(url=chapter_url, timeout=30)
    response.encoding = "gbk"
    selector = Selector(text=response.text)
    chapter_content = selector.css("#content").extract_first()
    return chapter_content
