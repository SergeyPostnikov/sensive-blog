from django.contrib import admin
from blog.models import Post, Tag, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author']
    raw_id_fields = ['likes', 'tags', 'author']
 

class CommentAdmin(admin.ModelAdmin):
    list_display = [
        'post',
        'author',
        'published_at',
    ]
    raw_id_fields = [
        'post',
        'author',
    ]


admin.site.register(Post, PostAdmin)
admin.site.register(Tag)
admin.site.register(Comment, CommentAdmin)
