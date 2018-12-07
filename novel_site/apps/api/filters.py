import django_filters

from novel.models import Novel


class NovelFilter(django_filters.rest_framework.FilterSet):
    novel = django_filters.rest_framework.CharFilter(field_name="novel_name", lookup_expr="icontains")
    category_name = django_filters.rest_framework.CharFilter(field_name="category__name", lookup_expr="icontains")
    author_name = django_filters.rest_framework.CharFilter(field_name="author__name", lookup_expr="icontains")
    category_id = django_filters.rest_framework.NumberFilter(field_name="category_id")
    author_id = django_filters.rest_framework.NumberFilter(field_name="author_id")

    class Meta:
        model = Novel
        fields = ("novel", "category_name", "author_name", "category_id", "author_id")
