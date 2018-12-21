from datetime import datetime, timedelta
import re

from django.db.models import Q
from rest_framework import serializers
from rest_framework.validators import UniqueValidator, UniqueTogetherValidator

from novel.models import Novel, NovelCategory, NovelChapter
from authors.models import Author
from users.models import UserProfile, EmailVerify, MobileVerify
from operation.models import UserFavorite, UserMessage, UserSuggest
from .validators import mobileValidator, NotNullTogetherValidator, EqualValidator
from novel_site.settings import MOBILE_VERIFY_REGX


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NovelCategory
        fields = ("id", "name")


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "name")


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = NovelChapter
        exclude = ["add_time"]
        # fields = ("id", "novel", "chapter_url", "chapter_index", "chapter_name")


class NovelSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    author = AuthorSerializer()

    class Meta:
        model = Novel
        fields = (
            "id", "novel_name", "site_name", "image_path", "intro", "read_nums", "fav_nums", "enable", "is_end",
            "category",
            "author")


class UserInfoSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(label="邮箱", help_text="邮箱地址", allow_blank=True, required=False,
                                   validators=[UniqueValidator(queryset=UserProfile.objects.all(), message="邮箱已存在")])
    mobile = serializers.CharField(label="手机", help_text="11位手机号码", min_length=11, max_length=11, allow_blank=True,
                                   required=False,
                                   validators=[UniqueValidator(queryset=UserProfile.objects.all(), message="手机号码已存在"),
                                               mobileValidator])

    class Meta:
        model = UserProfile
        fields = ("username", "email", "nickname", "birthday", "gender", "mobile", "image")
        validators = [NotNullTogetherValidator(fields=("email", "mobile"), message="邮件和手机号码必须填写其中一个")]


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(min_length=6, max_length=64, required=True, write_only=True, label="密码",
                                     help_text="必填. 6-64个字符", style={"input_type": "password"})
    email = serializers.EmailField(label="邮箱", help_text="邮箱地址", allow_blank=True, required=False,
                                   validators=[UniqueValidator(queryset=UserProfile.objects.all(), message="邮箱已存在")])
    mobile = serializers.CharField(label="手机", help_text="11位手机号码", min_length=11, max_length=11, allow_blank=True,
                                   required=False,
                                   validators=[UniqueValidator(queryset=UserProfile.objects.all(), message="手机号码已存在"),
                                               mobileValidator])

    class Meta:
        model = UserProfile
        fields = ("username", "password", "email", "mobile")
        validators = [NotNullTogetherValidator(fields=("email", "mobile"), message="邮件和手机号码必须填写其中一个")]


class EmailCodeSendSerializer(serializers.Serializer):
    send_type = serializers.ChoiceField(required=True, label="邮件类型",
                                        help_text="邮件类型(用户注册:register 密码重置:forget 更改邮箱:modify)",
                                        choices=(('register', '用户注册'), ('forget', '密码重置'), ('modify', '更改邮箱')))
    email = serializers.EmailField(required=True, label="邮箱", help_text="邮箱地址")

    def validate_email(self, email):
        email_type = self.initial_data["send_type"]
        if email_type in ("register", "modify") and UserProfile.objects.filter(email=email).exists():
            raise serializers.ValidationError("邮箱已存在")

        if email_type == "forget" and not UserProfile.objects.filter(email=email).exists():
            raise serializers.ValidationError("邮箱不存在")

        one_minute_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if EmailVerify.objects.filter(email=email, add_time__gt=one_minute_ago, send_type=email_type).exists():
            raise serializers.ValidationError("距离上一次发送未超过60s")

        return email

    def validate_send_type(self, send_type):
        if send_type not in ("register", "forget", "modify"):
            raise serializers.ValidationError("无效的邮件类型")

        return send_type


class EmailCodeVerifySerializer(serializers.Serializer):
    code = serializers.CharField(label="验证码", help_text="6位数字验证码", min_length=6, max_length=6, required=True,
                                 write_only=True)
    email = serializers.EmailField(required=True, label="邮箱", help_text="邮箱地址")
    send_type = serializers.ChoiceField(required=True, label="邮件类型",
                                        help_text="邮件类型(用户注册:register 密码重置:forget 更改邮箱:modify)",
                                        choices=(('register', '用户注册'), ('forget', '密码重置'), ('modify', '更改邮箱')))

    def validate_code(self, code):
        email = self.initial_data["email"]
        send_type = self.initial_data["send_type"]
        record = EmailVerify.objects.filter(email=email, code=code, send_type=send_type, is_valid=True).order_by(
            "-add_time").first()

        if not record:
            raise serializers.ValidationError("验证码错误")

        five_minutes_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
        if record.add_time < five_minutes_ago:
            raise serializers.ValidationError("验证码已过期")

        if record.code != code:
            raise serializers.ValidationError("验证码错误")

        return code


class MobileCodeSendSerializer(serializers.Serializer):
    verify_type = serializers.ChoiceField(required=True, label="动作",
                                          help_text="动作(用户注册:register 密码重置:forget 手机变更:modify)",
                                          choices=(('register', '用户注册'), ('forget', '密码重置'), ('modify', '手机变更')))
    mobile = serializers.CharField(required=True, label="手机", help_text="11位手机号码", min_length=11, max_length=11)

    def validate_verity_type(self, verity_type):
        if verity_type not in ("register", "forget", "modify"):
            raise serializers.ValidationError("无效的动作")
        return verity_type

    def validate_mobile(self, mobile):
        if not re.match(MOBILE_VERIFY_REGX, mobile):
            raise serializers.ValidationError("非法的手机号码")

        verify_type = self.initial_data["verify_type"]
        if verify_type in ("register", "modify") and UserProfile.objects.filter(mobile=mobile).exists():
            raise serializers.ValidationError("手机号码已存在")

        if verify_type == "forget" and not UserProfile.objects.filter(mobile=mobile).exists():
            raise serializers.ValidationError("手机号码不存在")

        one_minute_ago = datetime.now() - timedelta(hours=0, minutes=1, seconds=0)
        if MobileVerify.objects.filter(mobile=mobile, add_time__gt=one_minute_ago, verify_type=verify_type).exists():
            raise serializers.ValidationError("距离上一次发送未超过60s")

        return mobile


class MobileVerifySerializer(serializers.Serializer):
    verify_type = serializers.ChoiceField(required=True, label="动作",
                                          help_text="动作(用户注册:register 密码重置:forget 手机变更:modify)",
                                          choices=(('register', '用户注册'), ('forget', '密码重置'), ('modify', '手机变更')))
    mobile = serializers.CharField(required=True, label="手机", help_text="11位手机号码", min_length=11, max_length=11)
    code = serializers.CharField(required=True, label="验证码", help_text="6位数字验证码", min_length=6, max_length=6,
                                 write_only=True)

    def validate_code(self, code):
        mobile = self.initial_data["mobile"]
        verify_type = self.initial_data["verify_type"]
        record = MobileVerify.objects.filter(mobile=mobile, code=code, verify_type=verify_type).order_by(
            "-add_time").first()

        if not record:
            raise serializers.ValidationError("验证码错误")

        ten_minutes_ago = datetime.now() - timedelta(hours=0, minutes=10, seconds=0)
        if record.add_time < ten_minutes_ago:
            raise serializers.ValidationError("验证码已过期")

        if record.code != code:
            raise serializers.ValidationError("验证码错误")

        return code


class PasswdModifySerializer(serializers.Serializer):
    username = serializers.CharField(label="用户名", help_text="用户名/邮箱/手机号码", required=True)
    password = serializers.CharField(min_length=6, max_length=64, required=True, write_only=True, label="密码",
                                     help_text="必填. 6-64个字符", style={"input_type": "password"})
    again_password = serializers.CharField(min_length=6, max_length=64, required=True, write_only=True, label="确认密码",
                                           help_text="必填. 6-64个字符", style={"input_type": "password"})

    class Meta:
        model = UserProfile
        fields = ("username", "password", "again_password")
        validators = [EqualValidator(fields=("password", "again_password"), message="密码不一致")]

    def validate_username(self, username):
        if not UserProfile.objects.filter(Q(username=username) | Q(email=username) | Q(mobile=username)).exists():
            raise serializers.ValidationError("用户不存在")
        return username


class UserFavSerializer(serializers.ModelSerializer):
    novel = NovelSerializer(read_only=True)
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = UserFavorite
        fields = ["id", "notice_enable", "novel", "add_time"]


class UserFavDetaiSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = UserFavorite
        fields = ["novel", "notice_enable", "user"]
        validators = [
            UniqueTogetherValidator(queryset=UserFavorite.objects.all(), fields=("user", "novel"), message="已经收藏")]


class UserMessageSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = UserMessage
        fields = ["id", "user", "is_read", "add_time"]


class UserSuggestSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    has_deal = serializers.BooleanField(read_only=True)
    add_time = serializers.DateTimeField(read_only=True, format="%Y-%m-%d %H:%M:%S")

    class Meta:
        model = UserSuggest
        fields = ["id", "user", "subject", "suggest", "has_deal", "add_time"]
