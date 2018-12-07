import xadmin

from .models import UserFavorite, UserMessage, UserSuggest


class UserFavoriteAdmin:
    list_display = ["user", "novel", "notice_enable", "add_time", "update_time"]
    search_fields = ["user", "novel", "notice_enable"]
    list_filter = ["user", "novel", "notice_enable", "add_time", "update_time"]


class UserMessageAdmin:
    list_display = ["user", "message", "is_read", "add_time"]
    search_fields = ["user", "message", "is_read"]
    list_filter = ["user", "message", "is_read", "add_time"]


class UserSuggestAdmin:
    list_display = ["user", "suggest", "has_deal", "add_time"]
    search_fields = ["user", "suggest", "has_deal"]
    list_filter = ["user", "suggest", "has_deal", "add_time"]


xadmin.site.register(UserFavorite, UserFavoriteAdmin)
xadmin.site.register(UserMessage, UserMessageAdmin)
xadmin.site.register(UserSuggest, UserSuggestAdmin)