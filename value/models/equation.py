from config.settings import VALUE_CURVE_EQUATION
from django.utils.module_loading import import_string
from django.db import models
from django.urls import reverse
from project.models import Updated, Remote
from .curve import Curve
import numpy as np
import lmfit

class Equation(Updated, Remote):
    upper = models.ForeignKey(Curve, verbose_name='Curve', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Name', max_length=16, blank=True)

    def title(self):
        return '%s : %s' % (self.upper.title, self.name)

    def get_detail_url(self):
        return reverse('value:curve_update', kwargs={'pk': self.upper.id})

    def get_update_url(self):
        pass

    def get_delete_url(self):
        return reverse('value:equation_delete', kwargs={'pk': self.id})

    def entity(self):
        if self.name:
            for item in VALUE_CURVE_EQUATION:
                if item['Model'].split('.')[-1] == self.name:
                    cls = import_string(item['Model'])
                    return cls.objects.get(id=self.id)
        else:
            for item in VALUE_CURVE_EQUATION:
                cls = import_string(item['Model'])
                obj = cls.objects.filter(id=self.id)
                if obj:
                    return obj[0]

    def lmmodel(self):
        return self.entity().lmmodel()

    def set_params(self, params):
        return self.entity().set_params(params)

class Constant(Equation):
    prefix = models.CharField(verbose_name='Prefix', max_length=50)
    const = models.FloatField(verbose_name='Const', default=0.0)
    min = models.FloatField(verbose_name='Minimum', blank=True, null=True)
    max = models.FloatField(verbose_name='Maximum', blank=True, null=True)

    def get_update_url(self):
        return reverse('value:constant_update', kwargs={'pk': self.id})

    def lmmodel(self):
        return lmfit.models.ConstantModel(prefix=self.prefix)

    def set_params(self, params):
        key = '%sc' % self.prefix
        params[key].set(value=self.const)
        if self.min is not None:
            params[key].set(min=self.min)
        if self.max is not None:
            params[key].set(max=self.max)
        return params

class Gaussian(Equation):
    prefix = models.CharField(verbose_name='Prefix', max_length=50)
    center = models.FloatField(verbose_name='Center', default=0.0)
    height = models.FloatField(verbose_name='Height', default=1.0)
    width = models.FloatField(verbose_name='Width', default=1.0)
    center_min = models.FloatField(verbose_name='Center Minimum', blank=True, null=True)
    height_min = models.FloatField(verbose_name='Height Minimum', blank=True, null=True)
    width_min = models.FloatField(verbose_name='Width Minimum', blank=True, null=True)
    center_max = models.FloatField(verbose_name='Center Maximum', blank=True, null=True)
    height_max = models.FloatField(verbose_name='Height Maximum', blank=True, null=True)
    width_max = models.FloatField(verbose_name='Width Maximum', blank=True, null=True)

    def get_update_url(self):
        return reverse('value:gaussian_update', kwargs={'pk': self.id})

    @staticmethod
    def func(x, center, height, width):
        return height * np.exp(-0.5 * ((x - center) / width) ** 2)

    def lmmodel(self):
        return lmfit.models.Model(Gaussian.func, prefix=self.prefix)

    def set_params(self, params):
        key = '%scenter' % self.prefix
        params[key].set(value=self.center)
        if self.center_min is not None:
            params[key].set(min=self.center_min)
        if self.center_max is not None:
            params[key].set(max=self.center_max)
        key = '%sheight' % self.prefix
        params[key].set(value=self.height)
        if self.height_min is not None:
            params[key].set(min=self.height_min)
        if self.height_max is not None:
            params[key].set(max=self.height_max)
        key = '%swidth' % self.prefix
        params[key].set(value=self.width)
        if self.width_min is not None:
            params[key].set(min=self.width_min)
        if self.width_max is not None:
            params[key].set(max=self.width_max)
        return params

class Linear(Equation):
    prefix = models.CharField(verbose_name='Prefix', max_length=50)
    slope = models.FloatField(verbose_name='Slope', default=1.0)
    inter = models.FloatField(verbose_name='Intercept', default=0.0)
    slope_min = models.FloatField(verbose_name='Slope Minimum', blank=True, null=True)
    inter_min = models.FloatField(verbose_name='Intercept Minimum', blank=True, null=True)
    slope_max = models.FloatField(verbose_name='Slope Maximum', blank=True, null=True)
    inter_max = models.FloatField(verbose_name='Intercept Maximum', blank=True, null=True)

    def get_update_url(self):
        return reverse('value:linear_update', kwargs={'pk': self.id})

    def lmmodel(self):
        return lmfit.models.LinearModel(prefix=self.prefix)

    def set_params(self, params):
        key = '%sslope' % self.prefix
        params[key].set(value=self.slope)
        if self.slope_min is not None:
            params[key].set(min=self.slope_min)
        if self.slope_max is not None:
            params[key].set(max=self.slope_max)
        key = '%sintercept' % self.prefix
        params[key].set(value=self.inter)
        if self.inter_min is not None:
            params[key].set(min=self.inter_min)
        if self.inter_max is not None:
            params[key].set(max=self.inter_max)
        return params

class Quadratic(Equation):
    prefix = models.CharField(verbose_name='Prefix', max_length=50)
    a_val = models.FloatField(verbose_name='A', default=0.0)
    b_val = models.FloatField(verbose_name='B', default=0.0)
    c_val = models.FloatField(verbose_name='C', default=0.0)
    a_min = models.FloatField(verbose_name='A Minimum', blank=True, null=True)
    b_min = models.FloatField(verbose_name='B Minimum', blank=True, null=True)
    c_min = models.FloatField(verbose_name='C Minimum', blank=True, null=True)
    a_max = models.FloatField(verbose_name='A Maximum', blank=True, null=True)
    b_max = models.FloatField(verbose_name='B Maximum', blank=True, null=True)
    c_max = models.FloatField(verbose_name='C Maximum', blank=True, null=True)

    def get_update_url(self):
        return reverse('value:quadratic_update', kwargs={'pk': self.id})

    def lmmodel(self):
        return lmfit.models.QuadraticModel(prefix=self.prefix)

    def set_params(self, params):
        key = '%sa' % self.prefix
        params[key].set(value=self.a_val)
        if self.a_min is not None:
            params[key].set(min=self.a_min)
        if self.a_max is not None:
            params[key].set(max=self.a_max)
        key = '%sb' % self.prefix
        params[key].set(value=self.b_val)
        if self.b_min is not None:
            params[key].set(min=self.b_min)
        if self.b_max is not None:
            params[key].set(max=self.b_max)
        key = '%sc' % self.prefix
        params[key].set(value=self.c_val)
        if self.c_min is not None:
            params[key].set(min=self.c_min)
        if self.c_max is not None:
            params[key].set(max=self.c_max)
        return params

class Polynomial(Equation):
    prefix = models.CharField(verbose_name='Prefix', max_length=50)
    values = models.TextField(verbose_name='Values', default='1.0, 1.0, 1.0')
    mins = models.TextField(verbose_name='Minimums', blank=True)
    maxs = models.TextField(verbose_name='Maximums', blank=True)
    max_degree = 7

    def get_update_url(self):
        return reverse('value:polynomial_update', kwargs={'pk': self.id})

    def lmmodel(self):
        degree = len(self.values.split(',')) - 1
        if degree > self.max_degree:
            degree = self.max_degree
        return lmfit.models.PolynomialModel(degree, prefix=self.prefix)

    def set_params(self, params):
        i = 0;
        for val in self.values.split(','):
            key = '%sc%d' % (self.prefix, i)
            params[key].set(value=float(val))
            i += 1
            if i > self.max_degree:
                break
        if self.mins:
            i = 0;
            for val in self.mins.split(','):
                key = '%sc%d' % (self.prefix, i)
                params[key].set(min=float(val))
                i += 1
                if i > self.max_degree:
                    break
        if self.maxs:
            i = 0;
            for val in self.maxs.split(','):
                key = '%sc%d' % (self.prefix, i)
                params[key].set(max=float(val))
                i += 1
                if i > self.max_degree:
                    break
        return params

class Exponential(Equation):
    prefix = models.CharField(verbose_name='Prefix', max_length=50)
    amp = models.FloatField(verbose_name='Amplitude', default=0.0)
    decay = models.FloatField(verbose_name='Decay', default=0.0)
    amp_min = models.FloatField(verbose_name='Amplitude Minimum', blank=True, null=True)
    decay_min = models.FloatField(verbose_name='Decay Minimum', blank=True, null=True)
    amp_max = models.FloatField(verbose_name='Amplitude Maximum', blank=True, null=True)
    decay_max = models.FloatField(verbose_name='Decay Maximum', blank=True, null=True)

    def get_update_url(self):
        return reverse('value:exponential_update', kwargs={'pk': self.id})

    def lmmodel(self):
        return lmfit.models.ExponentialModel(prefix=self.prefix)

    def set_params(self, params):
        key = '%samplitude' % self.prefix
        params[key].set(value=self.amp)
        if self.amp_min is not None:
            params[key].set(min=self.amp_min)
        if self.amp_max is not None:
            params[key].set(max=self.amp_max)
        key = '%sdecay' % self.prefix
        params[key].set(value=self.decay)
        if self.decay_min is not None:
            params[key].set(min=self.decay_min)
        if self.decay_max is not None:
            params[key].set(max=self.decay_max)
        return params

class PowerLaw(Equation):
    prefix = models.CharField(verbose_name='Prefix', max_length=50)
    amp = models.FloatField(verbose_name='Amplitude', default=0.0)
    exp = models.FloatField(verbose_name='Exponent', default=0.0)
    amp_min = models.FloatField(verbose_name='Amplitude Minimum', blank=True, null=True)
    exp_min = models.FloatField(verbose_name='Exponent Minimum', blank=True, null=True)
    amp_max = models.FloatField(verbose_name='Amplitude Maximum', blank=True, null=True)
    exp_max = models.FloatField(verbose_name='Exponent Maximum', blank=True, null=True)

    def get_update_url(self):
        return reverse('value:powerlaw_update', kwargs={'pk': self.id})

    def lmmodel(self):
        return lmfit.models.PowerLawModel(prefix=self.prefix)

    def set_params(self, params):
        key = '%samplitude' % self.prefix
        params[key].set(value=self.amp)
        if self.amp_min is not None:
            params[key].set(min=self.amp_min)
        if self.amp_max is not None:
            params[key].set(max=self.amp_max)
        key = '%sexponent' % self.prefix
        params[key].set(value=self.exp)
        if self.exp_min is not None:
            params[key].set(min=self.exp_min)
        if self.exp_max is not None:
            params[key].set(max=self.exp_max)
        return params

class Sine(Equation):
    prefix = models.CharField(verbose_name='Prefix', max_length=50)
    amp = models.FloatField(verbose_name='Amplitude', default=1.0)
    freq = models.FloatField(verbose_name='Frequency', default=1.0)
    shift = models.FloatField(verbose_name='Shift', default=0.0)
    amp_min = models.FloatField(verbose_name='Amplitude Minimum', blank=True, null=True)
    freq_min = models.FloatField(verbose_name='Frequency Minimum', blank=True, null=True)
    shift_min = models.FloatField(verbose_name='Shift Minimum', blank=True, null=True)
    amp_max = models.FloatField(verbose_name='Amplitude Maximum', blank=True, null=True)
    freq_max = models.FloatField(verbose_name='Frequency Maximum', blank=True, null=True)
    shift_max = models.FloatField(verbose_name='Shift Maximum', blank=True, null=True)

    def get_update_url(self):
        return reverse('value:sine_update', kwargs={'pk': self.id})

    def lmmodel(self):
        return lmfit.models.SineModel(prefix=self.prefix)

    def set_params(self, params):
        key = '%samplitude' % self.prefix
        params[key].set(value=self.amp)
        if self.amp_min is not None:
            params[key].set(min=self.amp_min)
        if self.amp_max is not None:
            params[key].set(max=self.amp_max)
        key = '%sfrequency' % self.prefix
        params[key].set(value=self.freq)
        if self.freq_min is not None:
            params[key].set(min=self.freq_min)
        if self.freq_max is not None:
            params[key].set(max=self.freq_max)
        key = '%sshift' % self.prefix
        params[key].set(value=self.shift)
        if self.shift_min is not None:
            params[key].set(min=self.shift_min)
        if self.shift_max is not None:
            params[key].set(max=self.shift_max)
        return params

class Logistic(Equation):
    prefix = models.CharField(verbose_name='Prefix', max_length=50)
    K_val = models.FloatField(verbose_name='K', default=0.0)
    A_val = models.FloatField(verbose_name='A', default=0.0)
    x0_val = models.FloatField(verbose_name='x0', default=0.0)
    K_min = models.FloatField(verbose_name='K Minimum', blank=True, null=True)
    A_min = models.FloatField(verbose_name='A Minimum', blank=True, null=True)
    x0_min = models.FloatField(verbose_name='x0 Minimum', blank=True, null=True)
    K_max = models.FloatField(verbose_name='K Maximum', blank=True, null=True)
    A_max = models.FloatField(verbose_name='A Maximum', blank=True, null=True)
    x0_max = models.FloatField(verbose_name='x0 Maximum', blank=True, null=True)

    def get_update_url(self):
        return reverse('value:logistic_update', kwargs={'pk': self.id})

    @staticmethod
    def func(x, K, A, x0):
        return K / (1 + np.exp(- A * (x - x0)))

    def lmmodel(self):
        return lmfit.models.Model(Logistic.func, prefix=self.prefix)

    def set_params(self, params):
        key = '%sK' % self.prefix
        params[key].set(value=self.K_val)
        if self.K_min is not None:
            params[key].set(min=self.K_min)
        if self.K_max is not None:
            params[key].set(max=self.K_max)
        key = '%sA' % self.prefix
        params[key].set(value=self.A_val)
        if self.A_min is not None:
            params[key].set(min=self.A_min)
        if self.A_max is not None:
            params[key].set(max=self.A_max)
        key = '%sx0' % self.prefix
        params[key].set(value=self.x0_val)
        if self.x0_min is not None:
            params[key].set(min=self.x0_min)
        if self.x0_max is not None:
            params[key].set(max=self.x0_max)
        return params

class Expression(Equation):
    expr = models.TextField(verbose_name='Expression', default='p0 + p1 * x + p2 * x * x')
    values = models.TextField(verbose_name='Values', default='1.0, 1.0, 1.0')
    mins = models.TextField(verbose_name='Minimums', blank=True)
    maxs = models.TextField(verbose_name='Maximums', blank=True)

    def get_update_url(self):
        return reverse('value:expression_update', kwargs={'pk': self.id})

    def lmmodel(self):
        return lmfit.models.ExpressionModel(self.expr)

    def set_params(self, params):
        keys = params.keys()
        vals = self.values.split(',')
        while len(keys) > len(vals):
            vals.append('0.0')
        for key, val in zip(keys, vals):
            params[key].set(value=float(val))
        if self.mins:
            vals = self.mins.split(',')
            for key, val in zip(keys, vals):
                params[key].set(min=float(val))
        if self.maxs:
            vals = self.maxs.split(',')
            for key, val in zip(keys, vals):
                params[key].set(max=float(val))
        return params
