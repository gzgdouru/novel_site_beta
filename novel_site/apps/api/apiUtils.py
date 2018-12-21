import string
import random
import json
import requests

from django.contrib.auth import get_user_model

from users.models import EmailVerify, MobileVerify
from novel_site import settings

User = get_user_model()


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
    data = {
        "appid": settings.ONLINE_EMAIL_APPID,
        "to": email,
        "signature": settings.ONLINE_EMAIL_APPKEY,
        "project": "B8yc31"
    }

    # 生成验证码
    code = generate_digits_code()

    # 发送邮件
    if send_type == "register":
        subject = "用户账号注册邮件"
    elif send_type == "forget":
        subject = "用户密码重置邮件"
    elif send_type == "modify":
        subject = "用户邮箱变更邮件"
    else:
        return "无效的send_type:{0}".format(send_type)

    data["subject"] = subject
    data["vars"] = json.dumps({"code": code})
    response = requests.post(settings.ONLINE_EMAIL_URL, data=data)
    res = json.loads(response.text)
    if res.get("status") == "error":
        return res.get("msg")
    else:
        EmailVerify(email=email, code=code, send_type=send_type).save()


def send_mobile_code(mobile, verify_type="register"):
    code = generate_digits_code()
    params = {
        "code": code,
        "time": 10,
    }

    data = {
        "appid": settings.SMS_APPID,
        "to": mobile,
        "project": "Qtnph1",
        "vars": json.dumps(params),
        "signature": settings.SMS_APPKEY,
    }

    response = requests.post(settings.SMS_URL, data=data)
    res = json.loads(response.text)
    if res.get("status") == "error":
        return res.get("msg")
    MobileVerify(mobile=mobile, code=code, verify_type=verify_type).save()


if __name__ == "__main__":
    pass
