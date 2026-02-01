from django.contrib import admin
from .models import CategoryBlog,BlogPost,BlogContents,AuthorModel


admin.site.register(AuthorModel)
admin.site.register(CategoryBlog)


class BlogContentInline(admin.TabularInline):
    model = BlogContents
    raw_id_fields = ['post']


@admin.register(BlogPost)
class AdminModel(admin.ModelAdmin):
    list_display = ['title','author','category','category','created']
    list_filter = ['category','author','created',]
    inlines = [BlogContentInline]