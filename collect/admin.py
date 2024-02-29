from django.contrib import admin
from .models.collect import Collect
from .models.filter import Filter
from .models import process
from .models.reduction import Reduction
from .models.correlation import Correlation
from .models.classification import Classification
from .models.regression import Regression
from .models.inverse import Inverse

admin.site.register(Collect)
admin.site.register(Filter)
admin.site.register(process.Process)
admin.site.register(process.Fillna)
admin.site.register(process.Dropna)
admin.site.register(process.Drop)
admin.site.register(process.Select)
admin.site.register(process.Agg)
admin.site.register(process.Query)
admin.site.register(process.PCAF)
admin.site.register(Reduction)
admin.site.register(Correlation)
admin.site.register(Classification)
admin.site.register(Regression)
admin.site.register(Inverse)
