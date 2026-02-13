from django.contrib import admin
from .models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'shelter', 'created_at')
    list_filter = ('shelter', 'created_at')
    search_fields = ('title', 'content')
