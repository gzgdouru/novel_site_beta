from .models import Novel, NovelCategory

import xadmin


class NovellAdmin:
    list_display = ["novel_name", "site_name", "url", "category", "author", "add_time"]
    search_fields = ["novel_name", "site_name", "url", "category", "author"]
    list_filter = ["novel_name", "site_name", "url", "category", "author", "add_time"]


class NovelCategoryAdmin:
    list_display = ["name", "add_time"]
    search_fields = ["name"]
    list_filter = ["name", "add_time"]


xadmin.site.register(Novel, NovellAdmin)
xadmin.site.register(NovelCategory, NovelCategoryAdmin)