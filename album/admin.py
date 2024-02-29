from django.contrib import admin
from .models.album import Album
from .models.item import Item

admin.site.register(Album)
admin.site.register(Item)
