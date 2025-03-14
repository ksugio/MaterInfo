from django.contrib import admin
from .models.design import Design
from .models.condition import Condition
from .models.experiment import Experiment

admin.site.register(Design)
admin.site.register(Condition)
admin.site.register(Experiment)
