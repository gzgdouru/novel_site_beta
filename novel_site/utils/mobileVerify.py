import re, string, random, json
from datetime import datetime, timedelta
from django.contrib.auth import get_user_model
from django.db import transaction
import requests

from users.models import MobileVerify

User = get_user_model()


def phone_nums_verify(mobile):
    REGX = r"^((13[0-9])|(14[5,7])|(15[0-3,5-9])|(17[0,3,5-8])|(18[0-9])|166|198|199|(147))\d{8}$"
    matcher = re.match(REGX, mobile)
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
    url = r'https://api.mysubmail.com/message/xsend'
    code = generate_code()
    params = {
        "code" : code,
        "time" : 10,
    }

    data = {
        "appid": "27038",
        "to": mobile,
        "project": "Qtnph1",
        "vars": json.dumps(params),
        "signature": "c7ed55eb026edf67c87183a28948872a",
    }

    response = requests.post(url, data=data)
    res = json.loads(response.text)
    if res.get("status") == "error":
        raise RuntimeError("send sms error:{0}".format(res.get("msg")))
    MobileVerify(mobile=mobile, code=code, verify_type=verify_type).save()


if __name__ == "__main__":
   print(generate_code())
