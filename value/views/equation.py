from django.shortcuts import render, redirect
from config.settings import VALUE_CURVE_EQUATION
from project.views import base, base_api, remote
from ..models.curve import Curve
from ..models.equation import Equation, Constant, Gaussian, Linear, Quadratic, Polynomial, Exponential, PowerLaw, Sine, Logistic, Expression
from ..serializer import EquationSerializer

class AddView(base.AddView):
    model = Equation
    upper = Curve
    template_name = "project/default_add.html"
    bdcl_remove = 1

    def form_valid(self, form):
        model = form.save(commit=False)
        model.upper = self.upper.objects.get(pk=self.kwargs['pk'])
        model.updated_by = self.request.user
        model.name = self.model.__name__
        return super().form_valid(form)

class UpdateView(base.UpdateView):
    model = Equation
    template_name = "project/default_update.html"
    bdcl_remove = 1

class DeleteView(base.View):
    model = Equation
    template_name = 'project/default_delete.html'

    def get(self, request, **kwargs):
        process = self.model.objects.get(pk=kwargs['pk'])
        object = process.entity()
        params = {
            'object': object,
            'brand_name': self.brandName(),
            'breadcrumb_list': self.breadcrumbList(object, 1)
        }
        return render(request, self.template_name, params)

    def post(self, request, **kwargs):
        process = self.model.objects.get(pk=kwargs['pk'])
        upper = process.upper
        process.delete()
        upper.updated_by = self.request.user
        upper.save()
        return redirect(upper.get_update_url())

#
# Constant
#
class ConstantAddView(AddView):
    model = Constant
    fields = ('prefix', 'const', 'min', 'max')

class ConstantUpdateView(UpdateView):
    model = Constant
    fields = ('prefix', 'const', 'min', 'max')

#
# Gaussian
#
class GaussianAddView(AddView):
    model = Gaussian
    fields = ('prefix', 'center', 'height', 'width',
              'center_min', 'height_min', 'width_min',
              'center_max', 'height_max', 'width_max')

class GaussianUpdateView(UpdateView):
    model = Gaussian
    fields = ('prefix', 'center', 'height', 'width',
              'center_min', 'height_min', 'width_min',
              'center_max', 'height_max', 'width_max')

#
# Linear
#
class LinearAddView(AddView):
    model = Linear
    fields = ('prefix', 'slope', 'inter', 'slope_min', 'slope_max',
              'inter_min', 'inter_max')

class LinearUpdateView(UpdateView):
    model = Linear
    fields = ('prefix', 'slope', 'inter', 'slope_min', 'slope_max',
              'inter_min', 'inter_max')

#
# Quadratic
#
class QuadraticAddView(AddView):
    model = Quadratic
    fields = ('prefix', 'a_val', 'b_val', 'c_val',
              'a_min', 'b_min', 'c_min',
              'a_max', 'b_max', 'c_max')

class QuadraticUpdateView(UpdateView):
    model = Quadratic
    fields = ('prefix', 'a_val', 'b_val', 'c_val',
              'a_min', 'b_min', 'c_min',
              'a_max', 'b_max', 'c_max')

#
# Polynomial
#
class PolynomialAddView(AddView):
    model = Polynomial
    fields = ('prefix', 'values', 'mins', 'maxs')

class PolynomialUpdateView(UpdateView):
    model = Polynomial
    fields = ('prefix', 'values', 'mins', 'maxs')

#
# Exponential
#
class ExponentialAddView(AddView):
    model = Exponential
    fields = ('prefix', 'amp', 'decay', 'amp_min', 'decay_min',
              'amp_max', 'decay_max')

class ExponentialUpdateView(UpdateView):
    model = Exponential
    fields = ('prefix', 'amp', 'decay', 'amp_min', 'decay_min',
              'amp_max', 'decay_max')

#
# PowerLaw
#
class PowerLawAddView(AddView):
    model = PowerLaw
    fields = ('prefix', 'amp', 'exp', 'amp_min', 'exp_min',
              'amp_max', 'exp_max')

class PowerLawUpdateView(UpdateView):
    model = PowerLaw
    fields = ('prefix', 'amp', 'exp', 'amp_min', 'exp_min',
              'amp_max', 'exp_max')

#
# Sine
#
class SineAddView(AddView):
    model = Sine
    fields = ('prefix', 'amp', 'freq', 'shift',
              'amp_min', 'freq_min', 'shift_min',
              'amp_max', 'freq_max', 'shift_max')

class SineUpdateView(UpdateView):
    model = Sine
    fields = ('prefix', 'amp', 'freq', 'shift',
              'amp_min', 'freq_min', 'shift_min',
              'amp_max', 'freq_max', 'shift_max')

#
# Logistic
#
class LogisticAddView(AddView):
    model = Logistic
    fields = ('prefix', 'K_val', 'A_val', 'x0_val',
              'K_min', 'A_min', 'x0_min',
              'K_max', 'A_max', 'x0_max')

class LogisticUpdateView(UpdateView):
    model = Logistic
    fields = ('prefix', 'K_val', 'A_val', 'x0_val',
              'K_min', 'A_min', 'x0_min',
              'K_max', 'A_max', 'x0_max')

#
# Expression
#
class ExpressionAddView(AddView):
    model = Expression
    fields = ('expr', 'values', 'mins', 'maxs')

class ExpressionUpdateView(UpdateView):
    model = Expression
    fields = ('expr', 'values', 'mins', 'maxs')
