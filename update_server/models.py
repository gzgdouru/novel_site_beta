from datetime import datetime

import peewee

from core import get_database


class Author(peewee.Model):
    name = peewee.CharField(max_length=32, verbose_name="名称", unique=True)
    intro = peewee.TextField(verbose_name="简介", default="")
    image_path = peewee.CharField( max_length=200, verbose_name="图片路径", default="default_author.jpg", null=True)
    add_time = peewee.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        database = get_database()
        table_name = "tb_novel_author"


class Category(peewee.Model):
    name = peewee.CharField(max_length=32, verbose_name="分类名称", unique=True)
    add_time = peewee.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        database = get_database()
        table_name = "tb_novel_category"


class Novel(peewee.Model):
    novel_name = peewee.CharField(max_length=32, verbose_name="小说名称")
    site_name = peewee.CharField(max_length=32, verbose_name="小说网站")
    spider_name = peewee.CharField(max_length=64, verbose_name="爬虫名称", default="")
    url = peewee.CharField(unique=True, max_length=255, verbose_name="小说链接")
    category = peewee.ForeignKeyField(Category, on_delete="CASCADE", verbose_name="小说分类")
    image_url = peewee.CharField(max_length=200, verbose_name="小说图片", null=True)
    image_path = peewee.CharField(max_length=255, verbose_name="图片路径", default="default_novel.jpg", null=True)
    author = peewee.ForeignKeyField(Author, on_delete="CASCADE", verbose_name="小说作者")
    intro = peewee.TextField(verbose_name="小说简介", default="")
    read_nums = peewee.IntegerField(default=0, verbose_name="阅读数")
    fav_nums = peewee.IntegerField(default=0, verbose_name="收藏数")
    enable = peewee.BooleanField(verbose_name="是否显示", default=True)
    is_end = peewee.BooleanField(verbose_name="是否已完结", default=False)
    add_time = peewee.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        database = get_database()
        db_table = 'tb_novel'


class Chapter(peewee.Model):
    novel = peewee.ForeignKeyField(Novel, on_delete="CASCADE", verbose_name="小说")
    chapter_url = peewee.CharField(unique=True, max_length=255, verbose_name="章节链接")
    chapter_index = peewee.IntegerField(verbose_name="章节顺序", default=0)
    chapter_name = peewee.CharField(max_length=255, verbose_name="章节名称")
    add_time = peewee.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        database = get_database()
        table_name = 'tb_novel_chapter'


class UserFavorite(peewee.Model):
    user_id = peewee.IntegerField(verbose_name="用户id")
    novel_id = peewee.IntegerField(verbose_name="小说id")
    notice_enable = peewee.BooleanField(default=False, verbose_name="更新通知开关")
    add_time = peewee.DateTimeField(default=datetime.now, verbose_name="添加时间")
    update_time = peewee.DateTimeField(datetime.now, verbose_name="更新时间")

    class Meta:
        database = get_database()
        db_table = "tb_user_fav"
