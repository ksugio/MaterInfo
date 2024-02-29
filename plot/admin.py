from django.contrib import admin
from .models.plot import Plot
from .models.area import Area
from .models.item import Item

admin.site.register(Plot)
admin.site.register(Area)
admin.site.register(Item)
