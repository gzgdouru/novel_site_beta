import xadmin

from .models import Author

class AuthorAdmin:
    list_display = ["name", "desc", "add_time"]
    search_fields = ["name", "desc"]
    list_filter = ["name", "desc", "add_time"]


xadmin.site.register(Author, AuthorAdmin)