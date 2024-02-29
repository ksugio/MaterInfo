from django.contrib import admin
from .models import Comment, Response

admin.site.register(Comment)
admin.site.register(Response)