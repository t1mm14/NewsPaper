from django.contrib import admin
from .models import Post , Category 


class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category')
    list_filter = ('title', 'category', 'rating')
    search_fields = ('title', 'category__name')


# Register your models here.
admin.site.register(Category)
admin.site.register(Post)
