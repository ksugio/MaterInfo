from django.contrib import admin
from .models.value import Value
from .models.filter import Filter
from .models import process
from .models.aggregate import Aggregate
from .models.curve import Curve
from .models import equation

admin.site.register(Value)
admin.site.register(Filter)
admin.site.register(process.Process)
admin.site.register(process.Select)
admin.site.register(process.Trim)
admin.site.register(process.Operate)
admin.site.register(process.Rolling)
admin.site.register(process.Reduce)
admin.site.register(process.Gradient)
admin.site.register(process.Drop)
admin.site.register(process.Query)
admin.site.register(process.Eval)
admin.site.register(process.Beads)
admin.site.register(Aggregate)
admin.site.register(Curve)
admin.site.register(equation.Equation)
admin.site.register(equation.Constant)
admin.site.register(equation.Gaussian)
admin.site.register(equation.Linear)
admin.site.register(equation.Quadratic)
admin.site.register(equation.Polynomial)
admin.site.register(equation.Exponential)
admin.site.register(equation.PowerLaw)
admin.site.register(equation.Sine)
admin.site.register(equation.Logistic)
admin.site.register(equation.Expression)
