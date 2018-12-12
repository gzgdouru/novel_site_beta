"""novel_site URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.static import serve
from rest_framework.documentation import include_docs_urls

from novel.views import IndexView
from novel_site.settings import MEDIA_ROOT
from users.views import LoginView, LogoutView, EmailRegisterView, MobileRegisterView, AccountActiveView, \
    EmailForgetView, MobileForgetView, EmailResetView, MoblieVerifyView, RefreshCaptchaView

import xadmin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^xadmin/', xadmin.site.urls),

    url(r'^$', IndexView.as_view(), name="index"),
    url(r'^login/$', LoginView.as_view(), name="login"),
    url(r'^logout/$', LogoutView.as_view(), name="logout"),
    url(r'^register/email/$', EmailRegisterView.as_view(), name="email_register"),
    url(r'^register/mobile/$', MobileRegisterView.as_view(), name="mobile_register"),
    url(r'^active/(?P<active_code>.*)/$', AccountActiveView.as_view(), name="account_active"),
    url(r'^email_forget_password/$', EmailForgetView.as_view(), name="email_forget"),
    url(r'^email_reset_password/(?P<active_code>.*)/$', EmailResetView.as_view(), name="email_reset"),
    url(r'^mobile_verify/$', MoblieVerifyView.as_view(), name="mobile_verify"),
    url(r'^mobile_forget_password/$', MobileForgetView.as_view(), name="mobile_forget"),

    url(r'^novel/', include("novel.urls")),
    url(r'^authors/', include("authors.urls")),
    url(r'^users/', include("users.urls")),
    url(r'^operation/', include("operation.urls")),
    url(r'^api/v1/', include("api.urls")),
    url(r'docs/', include_docs_urls(title="小说api")),


    #刷新验证码
    url(r'^refresh_captcha/$', RefreshCaptchaView.as_view(), name="refresh_captcha"),

    #第三方登陆
    url('', include('social_django.urls', namespace='social')),

    #验证码
    url(r'^captcha/', include('captcha.urls')),

    # 配置上传文件的访问处理函数
    url(r'^media/(?P<path>.*)$', serve, {"document_root": MEDIA_ROOT}),
]
