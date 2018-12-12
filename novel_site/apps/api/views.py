from django.shortcuts import get_object_or_404, redirect
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework import filters
from rest_framework.reverse import reverse
import django_filters

from novel.models import Novel, NovelCategory, NovelChapter
from authors.models import Author
from .serializers import NovelSerializer, CategorySerializer, AuthorSerializer
from .serializers import ChapterSerializer
from .filters import NovelFilter, AuthorFilter, CatrgoryFilter
from utils import chapterParser


# Create your views here.
class IndexView(APIView):
    def get(self, request):
        return redirect("/docs/")


class NovelListView(generics.ListAPIView):
    '''获取小说列表'''
    queryset = Novel.objects.all()
    serializer_class = NovelSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    # filter_backends = (django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter)
    filterset_class = NovelFilter
    # filter_fields = ("novel_name", "category", "author__name")
    # search_fields = ("novel_name", "author__name")


class NovelCategoryView(generics.GenericAPIView):
    '''获取分类的所有小说'''
    serializer_class = NovelSerializer

    def get(self, request, category_id):
        self.category_id = category_id
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        category = get_object_or_404(NovelCategory, pk=self.category_id)
        return Novel.objects.filter(category=category)


class NovelAuthorView(generics.GenericAPIView):
    '''获取作者的所有小说'''
    serializer_class = NovelSerializer

    def get(self, request, author_id):
        self.author_id = author_id
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        author = get_object_or_404(Author, pk=self.author_id)
        return Novel.objects.filter(author=author)


class NovelDetailView(generics.RetrieveAPIView):
    '''获取特定的小说'''
    queryset = Novel.objects.all()
    serializer_class = NovelSerializer


class CategoryListView(generics.ListAPIView):
    '''获取小说分类列表'''
    queryset = NovelCategory.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = CatrgoryFilter
    # filter_fields = ("name",)


class CategoryDetailView(generics.RetrieveAPIView):
    '''获取特定的小说分类'''
    queryset = NovelCategory.objects.all()
    serializer_class = CategorySerializer


class AuthorListView(generics.ListAPIView):
    '''获取小说作者列表'''
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = AuthorFilter
    # filter_fields = ("name",)


class AuthorDetailView(generics.RetrieveAPIView):
    '''获取特定的小说作者'''
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer


class ChapterListView(generics.GenericAPIView):
    '''获取小说的章节列表'''
    serializer_class = ChapterSerializer

    def get(self, request, novel_id):
        self.novel_id = novel_id
        queryset = self.get_queryset()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        novel = Novel.objects.filter(pk=self.novel_id).first()
        chapters = NovelChapter.objects.filter(novel=novel).values("id", "chapter_index", "chapter_name")
        return chapters


class ChapterContentView(generics.RetrieveAPIView):
    '''获取章节内容'''
    serializer_class = ChapterSerializer

    def get(self, request, *args, **kwargs):
        self.chapter_id = kwargs.get("chapter_id")
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        novel_id = kwargs.get("novel_id")
        novel = get_object_or_404(Novel, pk=novel_id)
        get_chapter_content = getattr(chapterParser, novel.spider_name)
        chapter_content = get_chapter_content(instance.chapter_url)

        re_dict = serializer.data
        re_dict["chapter_content"] = chapter_content
        return Response(re_dict)

    def get_object(self):
        return get_object_or_404(NovelChapter, pk=self.chapter_id)
