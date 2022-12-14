from django.contrib import admin
from .models import Post, Comments, Follow
# Register your models here.


class PostAdmin(admin.ModelAdmin):
    list_display = ("pk","text", "pub_date", "author","group")
    search_fields = ("text",)
    list_filter = ("pub_date",)
    empty_value_display = "-пусто-"

class CommentsAdmin(admin.ModelAdmin):
    list_display = ("post","author", "text", "created")
    search_fields = ("text",)
    list_filter = ("created",)
    empty_value_display = "-пусто-"


class FollowAdmin(admin.ModelAdmin):
    list_display = ("user", "author")


admin.site.register(Follow, FollowAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comments, CommentsAdmin)
