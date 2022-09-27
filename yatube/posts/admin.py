from django.contrib import admin
from .models import Post, Group


class PostAdmin(admin.ModelAdmin):
    """Custom admin panel for posts."""

    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    list_editable = ('group',)


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
