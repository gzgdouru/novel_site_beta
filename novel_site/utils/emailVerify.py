import string
import random
import json
import requests

from django.core.mail import send_mail
from django.db import transaction

from novel_site.settings import EMAIL_HOST_USER
from users.models import EmailVerify
from novel_site import settings


def generate_code(length=16):
    nums = "{0}{1}".format(string.digits, string.ascii_letters)
    code = "".join([random.choice(nums) for i in range(length)])
    while EmailVerify.objects.filter(code=code, is_valid=True).exists():
        code = "".join([random.choice(nums) for i in range(length)])
    return code


def generate_digits_code(length=6):
    code = "".join([random.choice(string.digits) for i in range(length)])
    while EmailVerify.objects.filter(code=code, is_valid=True).exists():
        code = "".join([random.choice(string.digits) for i in range(length)])
    return code


def send_email_code(email, send_type="register"):
    # 保存数据到数据库
    if send_type == "modify":
        code = generate_digits_code(length=6)
    else:
        code = generate_code(length=64)
    EmailVerify(email=email, code=code, send_type=send_type).save()

    # 发送邮件
    if send_type == "register":
        subject = "用户账号激活邮件"
        content = "请点击以下链接激活你的账号:{0}/active/{1}".format(settings.CUSTOM_DNS, code)
    elif send_type == "forget":
        subject = "用户密码重置邮件"
        content = "请点击以下链接重置你的账号密码:{0}/email_reset_password/{1}".format(settings.CUSTOM_DNS, code)
    elif send_type == "modify":
        subject = "更改用户邮箱邮件"
        content = "您的邮箱验证码为:{0}".format(code)
    else:
        return "无效的send_type:{0}".format(send_type)

    return send_mail(subject, content, EMAIL_HOST_USER, [email])


def send_online_email_code(email, send_type="register"):
    data = {
        "appid": settings.ONLINE_EMAIL_APPID,
        "to": email,
        "signature": settings.ONLINE_EMAIL_APPKEY,
    }

    # 保存数据到数据库
    if send_type == "modify":
        code = generate_digits_code(length=6)
    else:
        code = generate_code(length=64)

    # 发送邮件
    if send_type == "register":
        subject = "用户账号激活邮件"
        project = "PwalT1"
    elif send_type == "forget":
        subject = "用户密码重置邮件"
        project = "AIk5G1"
    elif send_type == "modify":
        subject = "更改用户邮箱邮件"
        project = "zasOO4"
    else:
        return "无效的send_type:{0}".format(send_type)

    data["subject"] = subject
    data["project"] = project
    data["vars"] = json.dumps({"code": code})
    response = requests.post(settings.ONLINE_EMAIL_URL, data=data)
    res = json.loads(response.text)
    if res.get("status") == "error":
        return res.get("msg")
    else:
        EmailVerify(email=email, code=code, send_type=send_type).save()


if __name__ == "__main__":
    pass
