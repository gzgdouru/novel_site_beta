from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime

from novel.models import Novel

User = get_user_model()
# Create your models here.


class UserFavorite(models.Model):
    user = models.ForeignKey(User, models.CASCADE, verbose_name="用户")
    novel = models.ForeignKey(Novel, models.CASCADE, verbose_name="小说")
    notice_enable = models.BooleanField(default=False, verbose_name="更新通知开关")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "用户收藏表"
        verbose_name_plural = verbose_name
        db_table = "tb_user_fav"

    def __str__(self):
        return self.user.username


class UserMessage(models.Model):
    user = models.ForeignKey(User, models.CASCADE, verbose_name="用户")
    message = models.TextField(verbose_name="用户消息")
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用户消息表"
        verbose_name_plural = verbose_name
        db_table = "tb_user_message"

    def __str__(self):
        return self.user.username


class UserSuggest(models.Model):
    user = models.ForeignKey(User, models.CASCADE, verbose_name="用户")
    subject = models.CharField(max_length=64, default="", verbose_name="标题")
    suggest = models.TextField(verbose_name="建议")
    has_deal = models.BooleanField(default=False, verbose_name="是否已处理")
    add_time = models.DateTimeField(default=datetime.now, verbose_name="添加时间")

    class Meta:
        verbose_name = "用户意见表"
        verbose_name_plural = verbose_name
        db_table = "tb_user_suggest"

    def __str__(self):
        return self.user.username
