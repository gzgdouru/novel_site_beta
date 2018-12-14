from rest_framework import serializers

from novel.models import Novel, NovelCategory, NovelChapter
from authors.models import Author


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NovelCategory
        fields = ("id", "name")


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ("id", "name")


class ChapterSerializer(serializers.ModelSerializer):
    class Meta:
        model = NovelChapter
        fields = ("id", "chapter_index", "chapter_name")


class NovelSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    author = AuthorSerializer()

    class Meta:
        model = Novel
        fields = (
        "id", "novel_name", "site_name", "image_path", "intro", "read_nums", "fav_nums", "enable", "is_end", "category",
        "author")


