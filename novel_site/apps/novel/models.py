from django.db import models

from authors.models import Author


class NovelCategory(models.Model):
    name = models.CharField(max_length=32, verbose_name="分类名称", unique=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "小说分类"
        verbose_name_plural = verbose_name
        db_table = "tb_novel_category"

    def __str__(self):
        return self.name


class Novel(models.Model):
    novel_name = models.CharField(max_length=32, verbose_name="小说名称")
    site_name = models.CharField(max_length=32, verbose_name="小说网站")
    spider_name = models.CharField(max_length=64, verbose_name="爬虫名称", default="")
    url = models.CharField(unique=True, max_length=255, verbose_name="小说链接")
    category = models.ForeignKey(NovelCategory, models.CASCADE, verbose_name="小说分类")
    image_url = models.CharField(max_length=200, verbose_name="小说图片", null=True, blank=True)
    image_path = models.ImageField(upload_to='', max_length=200, verbose_name="图片路径", default="default_novel.jpg", null=True, blank=True)
    author = models.ForeignKey(Author, models.CASCADE, verbose_name="小说作者")
    intro = models.TextField(verbose_name="小说简介", default="")
    read_nums = models.PositiveIntegerField(default=0, verbose_name="阅读数")
    fav_nums = models.PositiveIntegerField(default=0, verbose_name="收藏数")
    enable = models.BooleanField(verbose_name="是否显示", default=True)
    is_end = models.BooleanField(verbose_name="是否已完结", default=False)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "小说"
        verbose_name_plural = verbose_name
        db_table = 'tb_novel'
        index_together = ("novel_name", "author")

    def __str__(self):
        return self.novel_name


class NovelChapter(models.Model):
    novel = models.ForeignKey('Novel', models.CASCADE, verbose_name="小说")
    chapter_url = models.URLField(unique=True, max_length=255, verbose_name="章节链接")
    chapter_index = models.PositiveIntegerField(verbose_name="章节顺序", default=0)
    chapter_name = models.CharField(max_length=255, verbose_name="章节名称")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "小说章节表"
        verbose_name_plural = verbose_name
        db_table = 'tb_novel_chapter'
