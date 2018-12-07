from collections import namedtuple

from captcha.models import CaptchaStore
from captcha.views import captcha_image_url

def get_new_captcha():
    Captcha = namedtuple("Captcha", ["hashKey", "imgUrl"])
    key = CaptchaStore.generate_key()
    img_url = captcha_image_url(key)
    return Captcha(hashKey=key, imgUrl=img_url)