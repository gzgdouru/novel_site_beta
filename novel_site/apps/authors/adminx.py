import xadmin

from .models import Author


class AuthorAdmin:
    list_display = ["name", "add_time"]
    search_fields = ["name"]
    list_filter = ["name", "add_time"]


xadmin.site.register(Author, AuthorAdmin)
