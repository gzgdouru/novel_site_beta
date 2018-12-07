from django.conf.urls import url

from .views import AddFavoriteView, UpdateNoticeView, ContactUsView

app_name = "operation"

urlpatterns = [
    url(r'^add_fav/$', AddFavoriteView.as_view(), name="add_fav"),
    url(r'^update_notice/$', UpdateNoticeView.as_view(), name="update_notice"),
    url(r'^contact/$', ContactUsView.as_view(), name="contact"),
]