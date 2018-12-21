from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from rest_framework.response import Response
import django_filters
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework import mixins
from rest_framework.authentication import SessionAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import OrderingFilter

from novel.models import Novel, NovelCategory, NovelChapter
from authors.models import Author
from operation.models import UserFavorite, UserMessage, UserSuggest
from .serializers import NovelSerializer, CategorySerializer, AuthorSerializer, ChapterSerializer
from .serializers import UserInfoSerializer, UserRegisterSerializer
from .serializers import UserFavSerializer, UserFavDetaiSerializer, UserMessageSerializer, UserSuggestSerializer
from .filters import NovelFilter, AuthorFilter, CatrgoryFilter, ChapterFilter
from .pagination import SinglePagination
from utils import chapterParser

User = get_user_model()


class NovelViewset(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    '''
    list:
        获取小说列表
    retrieve:
        获取小说详情
    '''
    queryset = Novel.objects.all()
    serializer_class = NovelSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend, OrderingFilter)
    filterset_class = NovelFilter
    ordering_fields = ("read_nums", "fav_nums")


class CategoryViewset(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    '''
    list:
        获取小说分类列表
    retrieve:
        获取小说分类详情
    '''
    queryset = NovelCategory.objects.all()
    serializer_class = CategorySerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = CatrgoryFilter


class AuthorViewset(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    '''
    list:
        获取小说作者列表
    retrieve:
        获取小说作者详情
    '''
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filterset_class = AuthorFilter


class ChapterViewset(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    '''
    list:
        获取章节列表
    retrieve:
        获取章节详情
    '''
    queryset = NovelChapter.objects.all().order_by("chapter_index")
    serializer_class = ChapterSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_class = ChapterFilter

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()

        # 获取小说内容
        novel = get_object_or_404(Novel, pk=instance.novel_id)
        get_chapter_content = getattr(chapterParser, novel.spider_name)
        content = get_chapter_content(instance.chapter_url)

        serializer = self.get_serializer(instance)
        re_dict = serializer.data
        re_dict["content"] = content

        return Response(re_dict)


class UserViewset(GenericViewSet, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    '''
    list:
        获取用户信息
    create:
        新建用户
    '''
    queryset = User.objects.all()
    authentication_classes = (JSONWebTokenAuthentication, SessionAuthentication)

    def get_object(self):
        return self.request.user

    def get_permissions(self):
        if self.action == "create":
            return []
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegisterSerializer
        return UserInfoSerializer

    def perform_create(self, serializer):
        # 加密密码
        password = serializer.validated_data["password"]
        serializer.validated_data["password"] = make_password(password)
        serializer.save()


class UserFavViewset(ModelViewSet):
    '''
    list:
        获取用户收藏列表
    retrieve:
        判断小说是否已经收藏
    create:
        新增用户收藏
    update:
        更新用户收藏
    destroy:
        删除用户收藏
    '''
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
    pagination_class = SinglePagination
    lookup_field = "novel_id"

    def get_queryset(self):
        return UserFavorite.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return UserFavDetaiSerializer
        return UserFavSerializer


class UserMessageViewset(GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
    '''
    list:
        获取用户消息列表
    retrieve:
        获取用户消息详情
    destroy:
        删除用户消息
    '''
    serializer_class = UserMessageSerializer
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserMessage.objects.filter(user=self.request.user)


class UserSuggestViewset(GenericViewSet, mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                         mixins.DestroyModelMixin):
    '''
    list:
        获取用户意见列表
    create:
        新增用户意见
    retrieve:
        获取用户意见详情
    destroy:
        删除用户意见
    '''
    serializer_class = UserSuggestSerializer
    authentication_classes = [JSONWebTokenAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserSuggest.objects.filter(user=self.request.user)
