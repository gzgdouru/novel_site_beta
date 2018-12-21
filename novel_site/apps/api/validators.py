import re

from rest_framework import serializers

from novel_site.settings import MOBILE_VERIFY_REGX


def mobileValidator(mobile):
    if not re.match(MOBILE_VERIFY_REGX, mobile):
        raise serializers.ValidationError("非法的手机号码")


class NotNullTogetherValidator(object):
    def __init__(self, fields, message):
        self.fields = fields
        self.message = message

    def __call__(self, attr):
        for field in self.fields:
            if attr.get(field):
                return
        raise serializers.ValidationError(self.message)


class EqualValidator(object):
    def __init__(self, fields, message):
        self.fields = fields
        self.message = message

    def __call__(self, attr):
        values = set([attr[field] for field in self.fields])
        if len(values) > 1:
            raise serializers.ValidationError(self.message)
