from django.conf.urls import url

from . import views

app_name = "api_v1"

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name="index"),
    url(r'^novel/$', views.NovelListView.as_view(), name="novel_list"),
    url(r'^novel/(?P<pk>\d+)/$', views.NovelDetailView.as_view(), name="novel_detail"),

    url(r'^category/(?P<category_id>\d+)/novel/$', views.CategoryAllNovelView.as_view(), name="category_all_novel"),
    url(r'^author/(?P<author_id>\d+)/novel/$', views.AuthorAllNovelView.as_view(), name="author_all_novel"),

    url(r'^category/$', views.CategoryListView.as_view(), name="category_list"),
    url(r'^category/(?P<pk>\d+)/$', views.CategoryDetailView.as_view(), name="category_detail"),

    url(r'^author/$', views.AuthorListView.as_view(), name="author_list"),
    url(r'^author/(?P<pk>\d+)/$', views.AuthorDetailView.as_view(), name="author_detail"),

    url(r'^chapter/(?P<novel_id>\d+)/$', views.ChapterListView.as_view(), name="chapter_list"),
    url(r'^chapter/(?P<pk>\d+)/$', views.ChapterDetailView.as_view(), name="chapter_detail"),
]
