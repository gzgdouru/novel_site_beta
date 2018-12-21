import re, string, random, json
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.db import transaction
import requests

from users.models import MobileVerify
from novel_site import settings

User = get_user_model()


def phone_nums_verify(mobile):
    matcher = re.match(settings.MOBILE_VERIFY_REGX, mobile)
    return matcher


def send_again_verify(mobile):
    record = MobileVerify.objects.filter(mobile=mobile).order_by("-add_time").first()
    if record:
        diff_time = datetime.now() - record.add_time
        if diff_time.total_seconds() < 60: return False
    return True


def mobile_verify(mobile, verify_type="register"):
    data = {}

    if not mobile:
        data["status"] = "fail"
        data["msg"] = "手机号码不能为空"
    elif not phone_nums_verify(mobile):
        data["status"] = "fail"
        data["msg"] = "无效的手机号"
    elif verify_type != "forget" and User.objects.filter(mobile=mobile).exists():
        data["status"] = "fail"
        data["msg"] = "该手机已注册"
    elif verify_type == "forget" and not User.objects.filter(mobile=mobile).exists():
        data["status"] = "fail"
        data["msg"] = "手机用户不存在"
    elif not send_again_verify(mobile):
        data["status"] = "fail"
        data["msg"] = "该号码使用过于频繁, 请稍后再试"
    else:
        data["status"] = "success"
        data["msg"] = "验证码已发送, 请查收"
    return data


def generate_code(length=6):
    nums = [random.choice(string.digits) for i in range(length)]
    code = "".join(nums)
    return code


def send_mobile_code(mobile, verify_type="register"):
    code = generate_code()
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
        raise RuntimeError("send sms error:{0}".format(res.get("msg")))
    MobileVerify(mobile=mobile, code=code, verify_type=verify_type).save()


if __name__ == "__main__":
    print(generate_code())
