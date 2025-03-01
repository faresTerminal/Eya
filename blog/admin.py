from django.contrib import admin
from blog.models import Contact, Article, comment_put

# Register your models here.

class BlogAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'slug')    


admin.site.register(Contact)
admin.site.register(Article, BlogAdmin)
admin.site.register(comment_put)
