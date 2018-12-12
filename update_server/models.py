from datetime import datetime

import peewee

from core import get_database


class Author(peewee.Model):
    name = peewee.CharField(max_length=32, verbose_name="名称", unique=True)
    intro = peewee.TextField(verbose_name="简介", default="")
    image_path = peewee.CharField(max_length=200, verbose_name="图片路径", default="default_author.jpg", null=True)
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


class UserProfile(peewee.Model):
    password = peewee.CharField(max_length=128, verbose_name="密码")
    last_login = peewee.DateTimeField(verbose_name="最后登录时间", null=True)
    is_superuser = peewee.IntegerField(verbose_name="是否超级用户")
    username = peewee.CharField(max_length=150, verbose_name="用户名")
    first_name = peewee.CharField(max_length=30)
    last_name = peewee.CharField(max_length=30)
    email = peewee.CharField(max_length=254, verbose_name="邮件地址")
    is_staff = peewee.IntegerField(verbose_name="是否员工")
    is_active = peewee.IntegerField(verbose_name="是否已激活")
    date_joined = peewee.DateTimeField(verbose_name="加入时间")
    nickname = peewee.CharField(max_length=32, verbose_name="昵称")
    birthday = peewee.DateField(verbose_name="生日", null=True)
    gender = peewee.CharField(max_length=32, verbose_name="性别")
    mobile = peewee.CharField(max_length=11, verbose_name="手机号码")
    image = peewee.CharField(max_length=255, verbose_name="用户头像")
    add_time = peewee.DateTimeField(verbose_name="添加时间")
    update_time = peewee.DateTimeField(verbose_name="更新时间")

    class Meta:
        database = get_database()
        db_table = "tb_user_profile"


class UserMessage(peewee.Model):
    message = peewee.TextField(verbose_name="消息")
    is_read = peewee.BooleanField(default=False, verbose_name="是否已读")
    add_time = peewee.DateTimeField(default=datetime.now, verbose_name="添加时间")
    user_id = peewee.IntegerField(verbose_name="用户id")

    class Meta:
        database = get_database()
        db_table = "tb_user_message"


class Proxys(peewee.Model):
    ip = peewee.CharField(max_length=16)
    port = peewee.IntegerField()
    types = peewee.IntegerField()
    protocol = peewee.IntegerField()
    country = peewee.CharField(max_length=100)
    area = peewee.CharField(max_length=100)
    updatetime = peewee.DateTimeField(null=True)
    speed = peewee.DecimalField(max_digits=5, decimal_places=2)
    score = peewee.IntegerField()

    class Meta:
        database = get_database()
        table_name = 'proxys'
