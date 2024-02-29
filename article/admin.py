from django.contrib import admin
from .models import Article, File, Diff

admin.site.register(Article)
admin.site.register(File)
admin.site.register(Diff)

