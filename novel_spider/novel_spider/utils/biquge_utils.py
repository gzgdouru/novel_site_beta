import re
import hashlib

from novel_spider.models import Novel, Author, Chapter


def get_md5(value):
    m = hashlib.md5()
    m.update(str(value).encode("utf-8"))
    return m.hexdigest()


def get_category_by_biquge(value):
    match_obj = re.match(r'.*?>(.*)?>.*', value)
    if match_obj:
        return match_obj.group(1).strip()
    else:
        return ""


def get_author_by_biquge(value):
    match_obj = re.match(r'^作.*?者：(\w+)', value)
    if match_obj:
        return match_obj.group(1)
    else:
        return ""


def get_chapter_index_by_biquge(value):
    match_obj = re.match(r'.*?/(\d+).html', value)
    if match_obj:
        return int(match_obj.group(1))
    return 0


def novel_is_exists(novel_name, author_name):
    author = Author.select().where(Author.name == author_name)
    if not author:
        return False

    if Novel.select().where((Novel.novel_name == novel_name) & (Novel.author == author)).exists():
        return True
    else:
        return False


def chapter_is_exists(chapter_url):
    return Chapter.select().where(Chapter.chapter_url == chapter_url).exists()
