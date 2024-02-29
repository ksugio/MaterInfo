from django.contrib import admin
from .models.image import Image
from .models.filter import Filter
from .models import process
from .models.size import Size
from .models.ln2d import LN2D
from .models.imfp import IMFP

admin.site.register(Image)
admin.site.register(Filter)
admin.site.register(process.Process)
admin.site.register(process.Resize)
admin.site.register(process.Trim)
admin.site.register(process.Smoothing)
admin.site.register(process.Threshold)
admin.site.register(process.Molphology)
admin.site.register(process.DrawScale)
admin.site.register(Size)
admin.site.register(LN2D)
admin.site.register(IMFP)

