from django.contrib import admin
from .models import Public, PublicArticle, PublicMenu, PublicFile

admin.site.register(Public)
admin.site.register(PublicArticle)
admin.site.register(PublicMenu)
admin.site.register(PublicFile)