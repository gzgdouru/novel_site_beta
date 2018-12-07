from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import reverse
from django.http import JsonResponse
from django.contrib import messages

from .models import UserFavorite, UserSuggest
from novel.models import Novel
from .forms import SuggestForm
from novel_site.settings import CUSTOM_USER_LOGIN_URL

# Create your views here.


class AddFavoriteView(View):
    '''添加收藏'''

    def post(self, request):
        data = {}
        if not request.user.is_authenticated:
            data["status"] = "fail"
            data["msg"] = "用户未登录"
            return JsonResponse(data)

        novel_id = request.POST.get("novel_id")
        novel = get_object_or_404(Novel, pk=novel_id)

        if UserFavorite.objects.filter(user=request.user, novel=novel).exists():
            UserFavorite.objects.filter(user=request.user, novel=novel).delete()
            data["msg"] = "remove"
            if novel.fav_nums > 0:
                novel.fav_nums -= 1
                novel.save()
        else:
            UserFavorite(user=request.user, novel=novel).save()
            data["msg"] = "add"
            novel.fav_nums += 1
            novel.save()
        data["status"] = "success"
        return JsonResponse(data)


class UpdateNoticeView(View):
    '''更新通知'''

    def post(self, request):
        data = {}
        if not request.user.is_authenticated:
            data["status"] = "fail"
            data["msg"] = "用户未登录"
            return JsonResponse(data)

        novel_id = int(request.POST.get("novel_id"))
        record = UserFavorite.objects.filter(user=request.user, novel_id=novel_id).first()
        if record.notice_enable:
            record.notice_enable = False
            data["msg"] = "off"
        else:
            record.notice_enable = True
            data["msg"] = "on"
        record.save()
        data["status"] = "success"
        return JsonResponse(data)


class ContactUsView(LoginRequiredMixin, View):
    '''联系我们'''
    login_url = CUSTOM_USER_LOGIN_URL

    def get(self, request):
        return render(request, "users/contact.html", context={})

    def post(self, request):
        suggest_form = SuggestForm(request.POST)

        if request.user.is_authenticated:
            if suggest_form.is_valid():
                suggest = suggest_form.cleaned_data.get("suggest")
                UserSuggest(user=request.user, suggest=suggest).save()
                messages.add_message(request, messages.SUCCESS, "提交成功")
                return render(request, "users/contact.html", context={})
        else:
           messages.add_message(request, messages.ERROR, "用户未登录!")
        return render(request, "users/contact.html", context={
            "suggest_form" : suggest_form,
        })





