from django.contrib import admin
from .models.reference import Reference
from .models.article import Article
from .models.image import Image
from .models.digitizer import Digitizer
from .models.text import Text

admin.site.register(Reference)
admin.site.register(Article)
admin.site.register(Image)
admin.site.register(Digitizer)
admin.site.register(Text)
