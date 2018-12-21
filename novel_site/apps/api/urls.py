from django.conf.urls import url, include
from rest_framework.routers import DefaultRouter

from . import views, viewsets

app_name = "api"
router = DefaultRouter()
router.register("novel", viewsets.NovelViewset, base_name="novel")
router.register("category", viewsets.CategoryViewset, base_name="category")
router.register("author", viewsets.AuthorViewset, base_name="author")
router.register("chapter", viewsets.ChapterViewset, base_name="chapter")
router.register("user", viewsets.UserViewset, base_name="user")
router.register("favorite", viewsets.UserFavViewset, base_name="favorite")
router.register("message", viewsets.UserMessageViewset, base_name="message")
router.register("suggest", viewsets.UserSuggestViewset, base_name="suggest")

urlpatterns = [
    url(r'', include(router.urls)),
    url(r'^email-send/$', views.EmailCodeSendView.as_view(), name="email-send"),
    url(r'^email-verify/$', views.EmailCodeVerifyView.as_view(), name="email-verify"),
    url(r'^mobile-send/$', views.MobileCodeSendView.as_view(), name="mobile-send"),
    url(r'^mobile-verify/$', views.MobileVerifyView.as_view(), name="mobile-verify"),
    url(r'^password-modify/$', views.PasswordModifyView.as_view(), name="password-modify"),
]
