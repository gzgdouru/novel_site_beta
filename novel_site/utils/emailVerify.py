import string
import random

from django.core.mail import send_mail
from django.db import transaction

from novel_site.settings import EMAIL_HOST_USER
from users.models import EmailVerify
from novel_site.settings import CUSTOM_DNS


def generate_code(length=16):
    nums = "{0}{1}".format(string.digits, string.ascii_letters)
    code = [random.choice(nums) for i in range(length)]
    return "".join(code)


def generate_digits_code(length=6):
    code = [random.choice(string.digits) for i in range(length)]
    return "".join(code)


@transaction.atomic
def send_email_code(email, send_type="register"):
    # 保存数据到数据库
    code = generate_digits_code(length=6) if send_type == "modify" else generate_code(length=64)
    while EmailVerify.objects.filter(code=code, send_type=send_type, is_valid=True).exists():
        code = generate_digits_code(length=6) if send_type == "modify" else generate_code(length=64)
    EmailVerify(email=email, code=code, send_type=send_type).save()

    # 发送邮件
    if send_type == "register":
        subject = "用户账号激活邮件"
        content = "请点击以下链接激活你的账号:{0}/active/{1}".format(CUSTOM_DNS, code)
    elif send_type == "forget":
        subject = "用户密码重置邮件"
        content = "请点击以下链接重置你的账号密码:{0}/email_reset_password/{1}".format(CUSTOM_DNS, code)
    elif send_type == "modify":
        subject = "更改用户邮箱邮件"
        content = "您的邮箱验证码为:{0}".format(code)
    else:
        raise RuntimeError("无效的send_type:{0}".format(send_type))

    send_mail(subject, content, EMAIL_HOST_USER, [email])

if __name__ == "__main__":
    pass
