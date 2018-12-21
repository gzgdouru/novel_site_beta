import django_filters

from novel.models import Novel, NovelCategory, NovelChapter
from authors.models import Author


class NovelFilter(django_filters.rest_framework.FilterSet):
    novel = django_filters.rest_framework.CharFilter(field_name="novel_name", lookup_expr="icontains", help_text="小说名称")
    category_name = django_filters.rest_framework.CharFilter(field_name="category__name", lookup_expr="icontains",
                                                             help_text="小说分类名称")
    author_name = django_filters.rest_framework.CharFilter(field_name="author__name", lookup_expr="icontains",
                                                           help_text="小说作者名称")
    category_id = django_filters.rest_framework.NumberFilter(field_name="category_id", help_text="小说分类id")
    author_id = django_filters.rest_framework.NumberFilter(field_name="author_id", help_text="小说作者id")

    class Meta:
        model = Novel
        fields = ("novel", "category_name", "author_name", "category_id", "author_id")


class AuthorFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.rest_framework.CharFilter(field_name="name", lookup_expr="icontains", help_text="作者名称")

    class Meta:
        model = Author
        fields = ("name",)


class CatrgoryFilter(django_filters.rest_framework.FilterSet):
    name = django_filters.rest_framework.CharFilter(field_name="name", lookup_expr="icontains", help_text="分类名称")

    class Meta:
        model = NovelCategory
        fields = ("name",)


class ChapterFilter(django_filters.rest_framework.FilterSet):
    novel_id = django_filters.rest_framework.NumberFilter(field_name="novel_id", help_text="小说id")

    class Meta:
        model = NovelChapter
        fields = ("novel_id",)
