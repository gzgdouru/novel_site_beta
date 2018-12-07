from django.conf.urls import url

from .views import UserInfoView, EmailVerifyView, ModifyEmailView, ModifyMobileView, ModifyPasswordView, \
    UserFavoriteView, UserMessageView, ModifyAvatarView, UserSuggestView, EmptyMessageView, EmptySuggestView

app_name = "users"

urlpatterns = [
    url(r'^info/$', UserInfoView.as_view(), name="info"),
    url(r'^email/code/$', EmailVerifyView.as_view(), name="email_code"),
    url(r'^email/modify/$', ModifyEmailView.as_view(), name="email_modify"),
    url(r'^mobile/modify/$', ModifyMobileView.as_view(), name="mobile_modify"),
    url(r'^mobile/password/$', ModifyPasswordView.as_view(), name="password_modify"),
    url(r'^favorite/$', UserFavoriteView.as_view(), name="favorite"),
    url(r'^message/$', UserMessageView.as_view(), name="message"),
    url(r'^modify_avatar/$', ModifyAvatarView.as_view(), name="modify_avatar"),
    url(r'^suggest/$', UserSuggestView.as_view(), name="user_suggest"),
    url(r'^empty/message/$', EmptyMessageView.as_view(), name="empty_message"),
    url(r'^empty/suggest/$', EmptySuggestView.as_view(), name="empty_suggest"),
]