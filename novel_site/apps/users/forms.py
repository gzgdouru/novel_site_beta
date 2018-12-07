from django import forms
from django.contrib.auth import get_user_model
from captcha.fields import CaptchaField
from django.core.exceptions import ValidationError

from .models import UserProfile
from utils.mobileVerify import phone_nums_verify

User = get_user_model()


class LoginForm(forms.Form):
    username = forms.CharField(max_length=32, required=True)
    password = forms.CharField(max_length=32, required=True)
    captcha = CaptchaField()


class EmailRegisterForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(min_length=6, required=True)


class EmailForm(forms.Form):
    email = forms.EmailField(required=True)


class EmailResetForm(forms.Form):
    email = forms.EmailField(required=True)
    password = forms.CharField(min_length=6, required=True)
    confirm_password = forms.CharField(min_length=6, required=True)


class MobileRegisterForm(forms.Form):
    mobile = forms.CharField(min_length=11, max_length=11, required=True)
    code = forms.CharField(min_length=6, max_length=6, required=True)
    password = forms.CharField(min_length=6, required=True)

    def clean_mobile(self):
        #判断手机号码是否有效
        mobile = self.cleaned_data.get("mobile")
        if not phone_nums_verify(mobile):
            raise ValidationError("无效的手机号码")
        return mobile

    def clean(self):
        clean_data = super(MobileRegisterForm, self).clean()
        return clean_data

class MobileForgetForm(forms.Form):
    mobile = forms.CharField(min_length=11, max_length=11, required=True)
    code = forms.CharField(min_length=6, max_length=6, required=True)
    password = forms.CharField(min_length=6, required=True)
    confirm_password = forms.CharField(min_length=6, required=True)


class UserInfoForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["nickname", "birthday", "gender"]


class ModifyEmailForm(forms.Form):
    email = forms.EmailField(required=True)
    code = forms.CharField(min_length=6, max_length=6)


class ModifyMobileForm(forms.Form):
    mobile = forms.CharField(min_length=11, max_length=11, required=True)
    code = forms.CharField(min_length=6, max_length=6, required=True)


class ModifyPasswordForm(forms.Form):
    password = forms.CharField(min_length=6, required=True)
    confirm_password = forms.CharField(min_length=6, required=True)


class ModifyAvatarForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ["image"]