import re
import json

import requests

from core import get_logger, get_email_manager
import settings

logger = get_logger()
emailobj = get_email_manager()


def get_index_by_chapter(value):
    match_obj = re.match(r'.*?/(\d+).html', value)
    if match_obj:
        return int(match_obj.group(1))
    return 0


def send_update_email(subject, content, receiver, novel_name):
    err = emailobj.send_email(subject, content, receiver)
    if not err:
        logger.info("发送小说[{0}]更新邮件给用户[{1}]成功".format(novel_name, receiver))
    else:
        logger.info("发送小说[{0}]更新邮件给用户[{1}]失败, 原因:{2}".format(novel_name, receiver, err))


def send_update_online_email(subject, receiver, novel_name):
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
    response = requests.post(url, data=data)
    res = json.loads(response.text)
    if res.get("status") != "error":
        logger.info("发送小说[{0}]更新邮件给用户[{1}]成功".format(novel_name, receiver))
    else:
        logger.error("发送小说[{0}]更新邮件给用户[{1}]失败, 原因:{2}".format(novel_name, receiver, res.get("msg")))

def send_update_sms(mobile, novel_name):
    url = settings.SMS_URL
    params = {"novel": novel_name}

    data = {
        "appid": settings.SMS_APPID,
        "to": mobile,
        "project": "tz4Nm1",
        "vars": json.dumps(params),
        "signature": settings.SMS_APPKEY,
    }

    session = requests.session()
    response = session.post(url, data=data)
    res = json.loads(response.text)
    if res.get("status") != "error":
        logger.info("发送小说[{0}]更新短信给用户[{1}]成功".format(novel_name, mobile))
    else:
        logger.error("发送小说[{0}]更新短信给用户[{1}]失败, 原因:{2}".format(novel_name, mobile, res.get("msg")))
