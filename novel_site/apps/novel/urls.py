from django.conf.urls import url
from django.views.decorators.cache import cache_page
from .views import CategoryListView, CategoryDetailView, NovelListView, NovelDetaiView, \
    ChapterListView, ChapterDetailView, NovelDownloadView

app_name = "novel"

urlpatterns = [
    url(r'^$', NovelListView.as_view(), name="novel_list"),
    url(r'^(?P<novel_id>\d+)/$', NovelDetaiView.as_view(), name="novel_detail"),
    url(r'^chapter/list/(?P<novel_id>\d+)/$', ChapterListView.as_view(), name="chapter_list"),
    url(r'^chapter/detail/(?P<chapter_id>\d+)/$',ChapterDetailView.as_view(), name="chapter_detail"),
    url(r'^category/$', CategoryListView.as_view(), name="category_list"),
    url(r'^category/(?P<category_id>\d+)/$', CategoryDetailView.as_view(), name="category_detail"),
    url(r'^download/(?P<novel_id>\d+)/$', NovelDownloadView.as_view(), name="novel_download"),
]