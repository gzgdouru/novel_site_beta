from django.shortcuts import render, get_object_or_404
from django.views.generic import View

from .models import Author

from pure_pagination import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.


class AuthorsListView(View):
    '''
    作者列表
    '''
    def get(self, request):
        all_authors = Author.objects.all()

        try:
            page = request.GET.get('page', 1)
        except PageNotAnInteger:
            page = 1
        p = Paginator(all_authors, 5, request=request)
        authors = p.page(page)

        return render(request, "authors/authors-list.html", context={
            "authors" : authors,
        })


class AuthorsDetailView(View):
    '''
    作者详细
    '''
    def get(self, request, author_id):
        author = get_object_or_404(Author, pk=author_id)
        novels = author.novel_set.filter(enable=True)
        return render(request, "authors/author-detail.html", context={
            "author" : author,
            "novels" : novels,
        })

