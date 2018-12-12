from django.shortcuts import render, redirect, HttpResponse, get_object_or_404
from django.views.generic import View
from django.shortcuts import reverse
from django.contrib.auth.views import logout, login
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.db import transaction
from datetime import datetime, timedelta, date
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.csrf import csrf_exempt

from users.models import UserProfile, EmailVerify, MobileVerify
from operation.models import UserFavorite, UserMessage, UserSuggest
from novel.models import Novel
from .forms import LoginForm, EmailRegisterForm, EmailResetForm, MobileRegisterForm, MobileForgetForm, \
    UserInfoForm, EmailForm, ModifyEmailForm, ModifyMobileForm, ModifyPasswordForm, ModifyAvatarForm
from utils.emailVerify import send_email_code, send_online_email_code
from utils.mobileVerify import mobile_verify, send_mobile_code
from utils.captchaTools import get_new_captcha
from novel_site.settings import CUSTOM_USER_LOGIN_URL, logger

User = get_user_model()


class MyAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            user = User.objects.get(Q(username=username) | Q(email=username) | Q(mobile=username))
            if user.check_password(password):
                return user
            else:
                return None
        except:
            return None


# Create your views here.


class LoginView(View):
    '''
    登入
    '''

    def get(self, request):
        next_page = request.GET.get("next", reverse("index"))
        return render(request, "users/login.html", context={
            "next": next_page,
            "captcha": get_new_captcha(),
        })

    def post(self, request):
        next_page = request.POST.get("next", "/")
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = request.POST.get("username")
            password = request.POST.get("password")
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return redirect(next_page)
                else:
                    messages.add_message(request, messages.ERROR, "该用户尚未激活!")
            else:
                messages.add_message(request, messages.ERROR, "用户名或密码错误!")
        else:
            pass
            # errors = login_form.errors.as_json()
            # print(errors)

        return render(request, "users/login.html", context={
            "login_form": login_form,
            "next": next_page,
            "captcha": get_new_captcha(),
        })


class LogoutView(LoginRequiredMixin, View):
    '''
    登出
    '''
    login_url = CUSTOM_USER_LOGIN_URL

    def get(self, request):
        nextUrl = request.GET.get("next", reverse("index"))
        logout(request)
        return redirect(nextUrl)


class EmailRegisterView(View):
    '''
    邮箱用户注册
    '''

    def get(self, request):
        return render(request, "users/email-register.html", context={})

    def post(self, request):
        register_form = EmailRegisterForm(request.POST)
        if register_form.is_valid():
            email = request.POST.get("email")
            password = request.POST.get("password")

            # 检查用户是否已经注册了
            if not User.objects.filter(email=email).exists():
                with transaction.atomic():
                    user = User()
                    user.username = email
                    user.email = email
                    user.password = make_password(password)
                    user.is_active = False
                    user.save()

                err = send_online_email_code(email)
                if err:
                    logger.error("发送激活邮件给用户[{0}]失败, 原因:{1}".format(email, err))
                    User.objects.filter(email=email).delete()
                    return HttpResponse("用户激活邮件发送失败, 请稍后再试.")
                logger.error("发送激活邮件给用户[{0}]成功.".format(email))
                return HttpResponse("用户激活邮件已发送， 请前往邮箱激活后登陆.")
            else:
                messages.add_message(request, messages.ERROR, "该邮箱已经注册！")
        else:
            pass

        return render(request, "users/email-register.html", context={
            "register_form": register_form,
        })


class AccountActiveView(View):
    '''
    邮箱用户账号激活
    '''

    def get(self, request, active_code):
        record = EmailVerify.objects.filter(code=active_code, is_valid=True).order_by("-add_time").first()
        if record:
            user = User.objects.get(email=record.email)
            user.is_active = True
            user.save()

            record.is_valid = False
            record.save()

            return redirect(reverse("login"))
        else:
            return HttpResponse("无效链接或者链接已失效!")


class MobileRegisterView(View):
    '''
    手机用户注册
    '''

    def get(self, request):
        return render(request, "users/mobile-register.html", context={})

    def post(self, request):
        register_form = MobileRegisterForm(request.POST)
        if register_form.is_valid():
            mobile = request.POST.get("mobile")
            code = request.POST.get("code")
            password = request.POST.get("password")
            record = MobileVerify.objects.filter(mobile=mobile, code=code, is_valid=True).order_by("-add_time").first()
            if record:
                diff_time = datetime.now() - record.add_time
                if diff_time.seconds < 10 * 60:
                    UserProfile(username=mobile, mobile=mobile, password=make_password(password), is_active=True).save()
                    record.is_valid = False
                    record.save()
                    return redirect(reverse("login"))
                else:
                    messages.add_message(request, messages.ERROR, "验证码已失效, 请重新获取")
            else:
                messages.add_message(request, messages.ERROR, "验证码错误")
        else:
            pass

        return render(request, "users/mobile-register.html", context={
            "register_form": register_form,
        })


class MoblieVerifyView(View):
    '''
    获取手机验证码
    '''

    def post(self, request):
        mobile = request.POST.get("mobile")
        verify_type = request.POST.get("verify_type", "register")
        data = mobile_verify(mobile, verify_type)
        if data.get("status") == "success":
            send_mobile_code(mobile, verify_type)
        return JsonResponse(data)


class EmailForgetView(View):
    '''
    忘记密码 - 邮箱用户
    '''

    def get(self, request):
        return render(request, "users/email-forget-password.html", context={})

    def post(self, request):
        forget_form = EmailForm(request.POST)
        if forget_form.is_valid():
            email = request.POST.get("email")
            if UserProfile.objects.filter(email=email).exists():
                err = send_online_email_code(email, "forget")
                if err:
                    logger.error("发送密码重置邮件给用户[{0}]失败, 原因:{1}".format(email, err))
                    return HttpResponse("邮件发送失败, 请稍后重试.")
                return HttpResponse("邮件已发送, 请前往邮箱重置您的密码.")
            else:
                messages.add_message(request, messages.ERROR, "该邮箱用户不存在!")
        else:
            pass

        return render(request, "users/email-forget-password.html", context={
            "forget_form": forget_form,
        })


class EmailResetView(View):
    '''
    邮箱用户重置密码
    '''

    def get(self, request, active_code):
        record = EmailVerify.objects.filter(code=active_code, is_valid=True, send_type="forget").order_by(
            "-add_time").first()
        if record:
            email = record.email
            return render(request, "users/email-password-reset.html", context={
                "email": email,
                "code": active_code,
            })
        else:
            return HttpResponse("无效链接或者链接已失效!")

    def post(self, request, active_code):
        active_code = request.POST.get("code")
        reset_form = EmailResetForm(request.POST)
        if reset_form.is_valid():
            email = request.POST.get("email")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            if password == confirm_password:
                UserProfile.objects.filter(email=email).update(password=make_password(password))
                EmailVerify.objects.filter(email=email, code=active_code, send_type="forget").update(is_valid=False)
                return redirect(reverse("login"))
            else:
                messages.add_message(request, messages.ERROR, "密码不一致!")
        else:
            pass

        return render(request, "users/email-password-reset.html", context={
            "email": request.POST.get("email"),
            "reset_form": reset_form,
            "code": active_code,
        })


class MobileForgetView(View):
    '''
    忘记密码 - 手机用户
    '''

    def get(self, request):
        return render(request, "users/mobile-forget-password.html", context={})

    def post(self, request):
        forget_form = MobileForgetForm(request.POST)
        if forget_form.is_valid():
            mobile = request.POST.get("mobile")
            code = request.POST.get("code")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            record = MobileVerify.objects.filter(mobile=mobile, code=code, verify_type="forget",
                                                 is_valid=True).order_by("-add_time").first()
            if record:
                diff_time = datetime.now() - record.add_time
                if diff_time.total_seconds() <= record.valid_time * 60:
                    if password == confirm_password:
                        user = UserProfile.objects.filter(mobile=mobile).update(
                            password=make_password(confirm_password))
                        record.is_valid = False
                        record.save()
                        return redirect(reverse("login"))
                    else:
                        messages.add_message(request, messages.ERROR, "密码不一致")
                else:
                    messages.add_message(request, messages.ERROR, "验证码已过期, 请重新获取")
            else:
                messages.add_message(request, messages.ERROR, "验证码错误")
        else:
            pass

        return render(request, "users/mobile-forget-password.html", context={
            "forget_form": forget_form,
        })


class UserInfoView(LoginRequiredMixin, View):
    '''
    用户个人信息中心
    '''
    login_url = CUSTOM_USER_LOGIN_URL

    def get(self, request):
        return render(request, "users/user-info.html", context={})

    def post(self, request):
        userinfo_form = UserInfoForm(request.POST, instance=request.user)
        if userinfo_form.is_valid():
            userinfo_form.save()
            # UserProfile.objects.filter(username=request.user.username).update(birthday=userinfo_form.cleaned_data["birthday"])
            messages.add_message(request, messages.SUCCESS, "保存成功")
            return render(request, "users/user-info.html", context={})
        else:
            for key, value in userinfo_form.errors.items():
                messages.add_message(request, messages.ERROR, "{0}:{1}".format(key, value))
        return render(request, "users/user-info.html", context={
            "userinfo_form": userinfo_form,
        })


class EmailVerifyView(View):
    '''
    获取邮箱验证码
    '''

    def post(self, request):
        data = {}
        verify_form = EmailForm(request.POST)
        if verify_form.is_valid():
            email = request.POST.get("email")
            if not UserProfile.objects.filter(email=email).exists():
                send_email_code(email=email, send_type="modify")
                data["status"] = "success"
                data["msg"] = "验证码已发送"
            else:
                data["status"] = "fail"
                data["msg"] = "该邮箱已注册"
        else:
            errors = ["{0}:{1}".format(key, value) for key, value in verify_form.errors.items()]
            data["status"] = "fail"
            data["msg"] = "\n".join(errors)
        return JsonResponse(data)


class ModifyEmailView(LoginRequiredMixin, View):
    '''用户邮箱修改'''
    login_url = CUSTOM_USER_LOGIN_URL

    def post(self, request):
        data = {}
        modify_form = ModifyEmailForm(request.POST)
        if modify_form.is_valid():
            email = request.POST.get("email")
            code = request.POST.get("code")
            record = EmailVerify.objects.filter(email=email, code=code, send_type="modify", is_valid=True).order_by(
                "-add_time").first()
            if record:
                UserProfile.objects.filter(username=request.user.username, email=request.user.email).update(email=email,
                                                                                                            username=email)
                record.is_valid = False
                record.save()
                data["status"] = "success"
                data["msg"] = "修改成功"
            else:
                data["status"] = "fail"
                data["msg"] = "无效的验证码"
        else:
            errors = ["{0}:{1}".format(key, value) for key, value in modify_form.errors.items()]
            data["status"] = "fail"
            data["msg"] = "\n".join(errors)
        return JsonResponse(data)


class ModifyMobileView(LoginRequiredMixin, View):
    '''修改手机号码'''
    login_url = CUSTOM_USER_LOGIN_URL

    def post(self, request):
        data = {}
        modify_form = ModifyMobileForm(request.POST)
        if modify_form.is_valid():
            mobile = request.POST.get("mobile")
            code = request.POST.get("code")
            record = MobileVerify.objects.filter(mobile=mobile, code=code, verify_type="modify",
                                                 is_valid=True).order_by("-add_time").first()
            if record:
                diff_time = datetime.now() - record.add_time
                if diff_time.total_seconds() <= record.valid_time * 60:
                    UserProfile.objects.filter(username=request.user.username, mobile=request.user.mobile).update(
                        mobile=mobile, username=mobile)
                    record.is_valid = False
                    record.save()
                    data["status"] = "success"
                    data["msg"] = "修改成功"
                else:
                    data["status"] = "fail"
                    data["msg"] = "验证码已失效, 请重新获取"
            else:
                data["status"] = "fail"
                data["msg"] = "无效的验证码"
        else:
            errors = ["{0}:{1}".format(key, value) for key, value in modify_form.errors.items()]
            data["status"] = "fail"
            data["msg"] = "\n".join(errors)
        return JsonResponse(data)


class ModifyPasswordView(LoginRequiredMixin, View):
    '''用户修改密码'''
    login_url = CUSTOM_USER_LOGIN_URL

    def post(self, request):
        data = {}
        modify_form = ModifyPasswordForm(request.POST)
        if modify_form.is_valid():
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            if password == confirm_password:
                UserProfile.objects.filter(id=request.user.id).update(password=make_password(confirm_password))
                data["status"] = "success"
                data["msg"] = "修改成功"
            else:
                data["status"] = "fail"
                data["msg"] = "密码不一致"
        else:
            errors = ["{0}:{1}".format(key, value) for key, value in modify_form.errors.items()]
            data["status"] = "fail"
            data["msg"] = "\n".join(errors)
        return JsonResponse(data)


class RefreshCaptchaView(View):
    '''刷新验证码'''

    def get(self, request):
        response = {}
        new_captcha = get_new_captcha()
        response["status"] = 1
        response["new_cptch_key"] = new_captcha.hashKey
        response["new_cptch_image"] = new_captcha.imgUrl
        return JsonResponse(response)


class UserFavoriteView(LoginRequiredMixin, View):
    '''用户收藏'''
    login_url = CUSTOM_USER_LOGIN_URL

    def get(self, request):
        all_fav = UserFavorite.objects.filter(user=request.user)
        novels = [(Novel.objects.filter(id=fav.novel_id).first(), fav.notice_enable) for fav in all_fav]
        return render(request, "users/user-favorite.html", context={
            "novels": novels,
        })


class UserMessageView(LoginRequiredMixin, View):
    '''用户消息'''
    login_url = CUSTOM_USER_LOGIN_URL

    def get(self, request):
        all_messages = UserMessage.objects.filter(user=request.user).order_by("-add_time")

        # 把所有消息都设置成已读
        all_messages.update(is_read=True)

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_messages, 8, request=request)
        user_messages = p.page(page)

        return render(request, "users/user-message.html", context={
            "user_messages": user_messages,
        })

    def post(self, request):
        data = {}
        if request.user.is_authenticated:
            msg_id = request.POST.get("msg_id")
            msg = get_object_or_404(UserMessage, pk=msg_id)
            msg.delete()
            data["status"] = "success"
        else:
            data["status"] = "fail"
            data["msg"] = "用户未登录"
        return JsonResponse(data)


class UserSuggestView(LoginRequiredMixin, View):
    '''我的建议'''
    login_url = CUSTOM_USER_LOGIN_URL

    def get(self, request):
        all_suggests = UserSuggest.objects.filter(user=request.user).order_by("-add_time")

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_suggests, 8, request=request)
        user_suggests = p.page(page)

        return render(request, "users/user-suggest.html", context={
            "user_suggests": user_suggests,
        })

    def post(self, request):
        data = {}
        if request.user.is_authenticated:
            suggest_id = request.POST.get("suggest_id")
            suggest = get_object_or_404(UserSuggest, pk=suggest_id)
            suggest.delete()
            data["status"] = "success"
        else:
            data["status"] = "fail"
            data["msg"] = "用户未登录"
        return JsonResponse(data)


class ModifyAvatarView(View):
    '''修改头像'''

    def post(self, request):
        data = {}
        imageUploadForm = ModifyAvatarForm(request.POST, request.FILES, instance=request.user)
        if imageUploadForm.is_valid():
            imageUploadForm.save()
            data["status"] = "success"
        else:
            data["status"] = "fail"
            data["msg"] = "请上传一张有效的图片。您所上传的文件不是图片或者是已损坏的图片"
        return JsonResponse(data)

    @csrf_exempt
    def dispatch(self, *args, **kwargs):
        return super(ModifyAvatarView, self).dispatch(*args, **kwargs)


class EmptyMessageView(View):
    '''清空用户消息'''

    def post(self, request):
        data = {}
        if request.user.is_authenticated:
            UserMessage.objects.filter(user=request.user).delete()
            data["status"] = "success"
        else:
            data["status"] = "fail"
            data["msg"] = "用户未登录"
        return JsonResponse(data)


class EmptySuggestView(View):
    '''清空用户建议'''

    def post(self, request):
        data = {}
        if request.user.is_authenticated:
            UserSuggest.objects.filter(user=request.user).delete()
            data["status"] = "success"
        else:
            data["status"] = "fail"
            data["msg"] = "用户未登录"
        return JsonResponse(data)
