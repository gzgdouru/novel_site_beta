import time
import tempfile

from django.shortcuts import render, get_object_or_404, Http404
from django.views.generic import View
from django.db.models import Q
from pure_pagination import Paginator, EmptyPage, PageNotAnInteger
from django.http import FileResponse, HttpResponse, StreamingHttpResponse
from w3lib.html import remove_tags

from .models import Novel, NovelCategory, NovelChapter
from .forms import SearchForm
from authors.models import Author
from operation.models import UserFavorite
from utils import chapterParser


# Create your views here.


class IndexView(View):
    '''
    首页
    '''

    def get(self, request):
        categorys = NovelCategory.objects.all()[:12]
        authors = Author.objects.all()[:8]
        novels = Novel.objects.filter(enable=True).order_by("-read_nums")[:8]

        return render(request, "index.html", context={
            "categorys": categorys,
            "authors": authors,
            "novels": novels,
        })


class NovelListView(View):
    '''
    小说列表
    '''

    def get(self, request):
        all_novels = Novel.objects.filter(enable=True)

        keyword = request.GET.get("search", "")
        if keyword:
            all_novels = all_novels.filter(Q(novel_name__icontains=keyword) | Q(author__name__icontains=keyword))

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_novels, 5, request=request)
        novels = p.page(page)

        return render(request, "novel/novel-list.html", context={
            "novels": novels,
        })


class NovelDetaiView(View):
    '''小说详情页'''

    def get(self, request, novel_id):
        novel = get_object_or_404(Novel, pk=novel_id)
        relation_novels = Novel.objects.filter(category=novel.category, enable=True).exclude(id=novel.id).order_by(
            "-read_nums")[:8]

        # 获取最新章节
        new_chapter = NovelChapter.objects.filter(novel=novel).order_by("-chapter_index").first()

        has_fav = False
        if request.user.is_authenticated and UserFavorite.objects.filter(novel=novel, user=request.user).exists():
            has_fav = True

        return render(request, "novel/novel-detail.html", context={
            "novel": novel,
            "relation_novels": relation_novels,
            "new_chapter": new_chapter,
            "has_fav": has_fav,
        })


class ChapterListView(View):
    '''
    章节列表
    '''

    def get(self, request, novel_id):
        novel = get_object_or_404(Novel, pk=novel_id)
        new_chapters = NovelChapter.objects.filter(novel=novel).values("id", "chapter_name", "chapter_index").order_by(
            "-chapter_index")[:12]
        all_chapters = NovelChapter.objects.filter(novel=novel).values("id", "chapter_name", "chapter_index").order_by(
            "chapter_index")

        # 阅读数+1
        novel.read_nums += 1
        novel.save()

        # 排序
        sortby = request.GET.get("sort", "")
        if sortby:
            all_chapters = all_chapters.order_by("-chapter_index")

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_chapters, 100, request=request)
        chapters = p.page(page)

        return render(request, "novel/chapter-list.html", context={
            "novel": novel,
            "chapters": chapters,
            "sortby": sortby,
            "new_chapters": new_chapters,
            "page": page,
        })


class ChapterDetailView(View):
    '''
    章节详情
    '''

    def get(self, request, chapter_id):
        chapterObj = get_object_or_404(NovelChapter, pk=chapter_id)
        novelObj = get_object_or_404(Novel, pk=chapterObj.novel_id)
        sortby = request.GET.get("sort", "")
        page = request.GET.get("page", 1)

        # 取上一章节
        pre_chapter = NovelChapter.objects.filter(novel_id=novelObj.id,
                                                  chapter_index__lt=chapterObj.chapter_index).order_by(
            "-chapter_index").first()
        if not pre_chapter:
            pre_chapter = chapterObj

        # 取下一章节
        next_chapter = NovelChapter.objects.filter(novel_id=novelObj.id,
                                                   chapter_index__gt=chapterObj.chapter_index).order_by(
            "chapter_index").first()
        if not next_chapter:
            next_chapter = chapterObj

        # 解析小说内容
        try:
            get_chapter_content = getattr(chapterParser, novelObj.spider_name)
            content = get_chapter_content(chapterObj.chapter_url)
        except Exception as e:
            raise Http404(e)

        return render(request, "novel/chapter-detail.html", context={
            "chapter": chapterObj,
            "chapter_content": content,
            "novel": novelObj,
            "pre_chapter": pre_chapter,
            "next_chapter": next_chapter,
            "sortby": sortby,
            "page": page,
        })


class CategoryListView(View):
    '''
    分类列表
    '''

    def get(self, request):
        all_categorys = NovelCategory.objects.all()

        return render(request, "novel/category-list.html", context={
            "categorys": all_categorys,
        })


class CategoryDetailView(View):
    '''
    分类详细
    '''

    def get(self, request, category_id):
        all_novels = Novel.objects.filter(category_id=category_id, enable=True)

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_novels, 5, request=request)
        novels = p.page(page)

        return render(request, "novel/novel-list.html", context={
            "novels": novels,
        })


class NovelDownloadView(View):
    def get(self, request, novel_id):
        novel = get_object_or_404(Novel, pk=novel_id)
        chapters = NovelChapter.objects.filter(novel=novel)
        get_chapter_content = getattr(chapterParser, novel.spider_name)
        f = tempfile.TemporaryFile()
        for chapter in chapters:
            try:
                content = get_chapter_content(chapter.chapter_url)
                content = "{0}\n{1}\n".format(chapter.chapter_name, remove_tags(content))
                f.write(content.encode("utf-8"))
            except Exception as e:
                raise Http404(e)
        f.seek(0)
        response = FileResponse(f.read())
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{0}.txt"'.format(novel.novel_name)
        f.close()
        return response
