from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime, timedelta


VerifyCodeChoices = (
    ("register", "注册"),
    ("forget", "忘记密码"),
)

# Create your models here.


class UserProfile(AbstractUser):
    nickname = models.CharField(max_length=32, default="", verbose_name="昵称")
    birthday = models.DateField(null=True, blank=True, verbose_name="生日")
    gender = models.CharField(max_length=32, choices=(("male", "男"), ("female", "女")), default="male",
                              verbose_name="性别")
    mobile = models.CharField(max_length=11, default="", verbose_name="手机号码")
    image = models.ImageField(max_length=255, upload_to="user/avatar/", verbose_name="头像", default="default_author.jpg")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="修改时间")

    class Meta:
        verbose_name = "用户信息表"
        verbose_name_plural = verbose_name
        db_table = "tb_user_profile"

    def __str__(self):
        return self.username

    def unread_msg_nums(self):
        from operation.models import UserMessage
        nums = UserMessage.objects.filter(user=self.id, is_read=False).count()
        return nums


class EmailVerify(models.Model):
    email = models.EmailField(verbose_name="邮箱")
    code = models.CharField(max_length=255, verbose_name="验证码")
    is_valid = models.BooleanField(default=True, verbose_name="是否有效")
    send_type = models.CharField(max_length=32, choices=VerifyCodeChoices, default="register", verbose_name="验证码类型")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "邮件验证码"
        verbose_name_plural = verbose_name
        db_table = "tb_email_verify"


class MobileVerify(models.Model):
    mobile = models.CharField(max_length=11, verbose_name="手机")
    code = models.CharField(max_length=32, verbose_name="验证码")
    valid_time = models.PositiveIntegerField(default=10, verbose_name="有效时长(分钟)")
    is_valid = models.BooleanField(default=True, verbose_name="是否有效")
    verify_type = models.CharField(max_length=32, choices=VerifyCodeChoices, verbose_name="验证码类型", default="register")
    add_time = models.DateTimeField(auto_now_add=True, verbose_name="添加时间")

    def __str__(self):
        return self.mobile

    class Meta:
        verbose_name = "手机验证码"
        verbose_name_plural = verbose_name
        db_table = "tb_mobile_verify"
