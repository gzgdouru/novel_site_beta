import json
import threading
from urllib import parse

from tornado import httpclient

import settings
from core import get_logger

logger = get_logger()
http_client = httpclient.AsyncHTTPClient()


async def send_update_sms(mobile, novel_name):
    url = settings.SMS_URL
    params = {"novel": novel_name}

    data = {
        "appid": settings.SMS_APPID,
        "to": mobile,
        "project": "tz4Nm1",
        "vars": json.dumps(params),
        "signature": settings.SMS_APPKEY,
    }

    response = await http_client.fetch(url, method="POST", body=parse.urlencode(data))
    res = json.loads(response.body)
    if res.get("status") != "error":
        logger.info("发送小说[{0}]更新短信给用户[{1}]成功".format(novel_name, mobile))
    else:
        logger.error("发送小说[{0}]更新短信给用户[{1}]失败, 原因:{2}".format(novel_name, mobile, res.get("msg")))


async def send_update_online_email(subject, receiver, novel_name):
    url = settings.ONLINE_EMAIL_URL
    params = {"novel_name": novel_name}

    data = {
        "appid": settings.ONLINE_EMAIL_APPID,
        "to": receiver,
        "subject": subject,
        "project": "3pTLi2",
        "vars": json.dumps(params),
        "signature": settings.ONLINE_EMAIL_APPKEY,
    }
    response = await http_client.fetch(url, method="POST", body=parse.urlencode(data))
    res = json.loads(response.body)
    if res.get("status") != "error":
        logger.info("发送小说[{0}]更新邮件给用户[{1}]成功".format(novel_name, receiver))
    else:
        logger.error("发送小说[{0}]更新邮件给用户[{1}]失败, 原因:{2}".format(novel_name, receiver, res.get("msg")))


if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.create_task(send_update_online_email("小说更新通知", "18719091650@163.com", "全职法师"))
    loop.run_forever()
