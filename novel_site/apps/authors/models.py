from django.db import models
from datetime import datetime


# Create your models here.


class Author(models.Model):
    name = models.CharField(max_length=32, verbose_name="名称", unique=True, help_text="作者名称")
    intro = models.TextField(verbose_name="简介", default="")
    image_path = models.ImageField(upload_to="", max_length=200, verbose_name="图片路径", default="default_author.jpg", null=True, blank=True)
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    class Meta:
        verbose_name = "小说作者"
        verbose_name_plural = verbose_name
        db_table = "tb_novel_author"

    def __str__(self):
        return self.name
