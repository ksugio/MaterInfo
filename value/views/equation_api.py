from django.utils.module_loading import import_string
from config.settings import VALUE_CURVE_EQUATION
from project.views import base_api, remote
from ..models.curve import Curve
from ..models import equation
from .. import serializer

class AddAPIView(base_api.AddAPIView):
    upper = Curve
    serializer_class = None

    def perform_create(self, serializer):
        upper = self.upper.objects.get(pk=self.kwargs['pk'])
        name = self.serializer_class.Meta.model.__name__
        serializer.save(updated_by=self.request.user, upper=upper, name=name)

class ListAPIView(base_api.ListAPIView):
    upper = Curve
    model = equation.Equation
    serializer_class = serializer.EquationSerializer

class DeleteAPIView(base_api.DeleteAPIView):
    model = equation.Equation
    serializer_class = serializer.EquationSerializer

class EquationRemote(remote.SwitchRemote):
    model = equation.Equation
    add_name = None
    list_name = 'value:api_equation_list'
    retrieve_name = None
    update_name = None
    delete_name = 'value:api_equation_delete'
    serializer_class = serializer.EquationSerializer
    synchronize = True
    upper_save = True

    def switcher(self, name):
        if name:
            for item in VALUE_CURVE_EQUATION:
                if item['Model'].split('.')[-1] == name and 'Remote' in item:
                    return import_string(item['Remote'])
        return None

    def data_switcher(self, data):
        return self.switcher(data['name'])

    def model_switcher(self, model):
        return self.switcher(model.name)

#
# Constant
#
class ConstantAddAPIView(AddAPIView):
    serializer_class = serializer.ConstantSerializer

class ConstantRetrieveAPIView(base_api.RetrieveAPIView):
    model = equation.Constant
    serializer_class = serializer.ConstantSerializer

class ConstantUpdateAPIView(base_api.UpdateAPIView):
    model = equation.Constant
    serializer_class = serializer.ConstantSerializer

class ConstantRemote(EquationRemote):
    model = equation.Constant
    add_name = 'value:api_constant_add'
    retrieve_name = 'value:api_constant_retrieve'
    update_name = 'value:api_constant_update'
    serializer_class = serializer.ConstantSerializer

#
# Gaussian
#
class GaussianAddAPIView(AddAPIView):
    serializer_class = serializer.GaussianSerializer

class GaussianRetrieveAPIView(base_api.RetrieveAPIView):
    model = equation.Gaussian
    serializer_class = serializer.GaussianSerializer

class GaussianUpdateAPIView(base_api.UpdateAPIView):
    model = equation.Gaussian
    serializer_class = serializer.GaussianSerializer

class GaussianRemote(EquationRemote):
    model = equation.Gaussian
    add_name = 'value:api_gaussian_add'
    retrieve_name = 'value:api_gaussian_retrieve'
    update_name = 'value:api_gaussian_update'
    serializer_class = serializer.GaussianSerializer

#
# Linear
#
class LinearAddAPIView(AddAPIView):
    serializer_class = serializer.LinearSerializer

class LinearRetrieveAPIView(base_api.RetrieveAPIView):
    model = equation.Linear
    serializer_class = serializer.LinearSerializer

class LinearUpdateAPIView(base_api.UpdateAPIView):
    model = equation.Linear
    serializer_class = serializer.LinearSerializer

class LinearRemote(EquationRemote):
    model = equation.Linear
    add_name = 'value:api_linear_add'
    retrieve_name = 'value:api_linear_retrieve'
    update_name = 'value:api_linear_update'
    serializer_class = serializer.LinearSerializer

#
# Quadratic
#
class QuadraticAddAPIView(AddAPIView):
    serializer_class = serializer.QuadraticSerializer

class QuadraticRetrieveAPIView(base_api.RetrieveAPIView):
    model = equation.Quadratic
    serializer_class = serializer.QuadraticSerializer

class QuadraticUpdateAPIView(base_api.UpdateAPIView):
    model = equation.Quadratic
    serializer_class = serializer.QuadraticSerializer

class QuadraticRemote(EquationRemote):
    model = equation.Quadratic
    add_name = 'value:api_quadratic_add'
    retrieve_name = 'value:api_quadratic_retrieve'
    update_name = 'value:api_quadratic_update'
    serializer_class = serializer.QuadraticSerializer

#
# Polynomial
#
class PolynomialAddAPIView(AddAPIView):
    serializer_class = serializer.PolynomialSerializer

class PolynomialRetrieveAPIView(base_api.RetrieveAPIView):
    model = equation.Polynomial
    serializer_class = serializer.PolynomialSerializer

class PolynomialUpdateAPIView(base_api.UpdateAPIView):
    model = equation.Polynomial
    serializer_class = serializer.PolynomialSerializer

class PolynomialRemote(EquationRemote):
    model = equation.Polynomial
    add_name = 'value:api_polynomial_add'
    retrieve_name = 'value:api_polynomial_retrieve'
    update_name = 'value:api_polynomial_update'
    serializer_class = serializer.PolynomialSerializer

#
# Exponential
#
class ExponentialAddAPIView(AddAPIView):
    serializer_class = serializer.ExponentialSerializer

class ExponentialRetrieveAPIView(base_api.RetrieveAPIView):
    model = equation.Exponential
    serializer_class = serializer.ExponentialSerializer

class ExponentialUpdateAPIView(base_api.UpdateAPIView):
    model = equation.Exponential
    serializer_class = serializer.ExponentialSerializer

class ExponentialRemote(EquationRemote):
    model = equation.Exponential
    add_name = 'value:api_exponential_add'
    retrieve_name = 'value:api_exponential_retrieve'
    update_name = 'value:api_exponential_update'
    serializer_class = serializer.ExponentialSerializer

#
# PowerLaw
#
class PowerLawAddAPIView(AddAPIView):
    serializer_class = serializer.PowerLawSerializer

class PowerLawRetrieveAPIView(base_api.RetrieveAPIView):
    model = equation.PowerLaw
    serializer_class = serializer.PowerLawSerializer

class PowerLawUpdateAPIView(base_api.UpdateAPIView):
    model = equation.PowerLaw
    serializer_class = serializer.PowerLawSerializer

class PowerLawRemote(EquationRemote):
    model = equation.PowerLaw
    add_name = 'value:api_powerlaw_add'
    retrieve_name = 'value:api_powerlaw_retrieve'
    update_name = 'value:api_powerlaw_update'
    serializer_class = serializer.PowerLawSerializer

#
# Sine
#
class SineAddAPIView(AddAPIView):
    serializer_class = serializer.SineSerializer

class SineRetrieveAPIView(base_api.RetrieveAPIView):
    model = equation.Sine
    serializer_class = serializer.SineSerializer

class SineUpdateAPIView(base_api.UpdateAPIView):
    model = equation.Sine
    serializer_class = serializer.SineSerializer

class SineRemote(EquationRemote):
    model = equation.Sine
    add_name = 'value:api_sine_add'
    retrieve_name = 'value:api_sine_retrieve'
    update_name = 'value:api_sine_update'
    serializer_class = serializer.SineSerializer

#
# Logistic
#
class LogisticAddAPIView(AddAPIView):
    serializer_class = serializer.LogisticSerializer

class LogisticRetrieveAPIView(base_api.RetrieveAPIView):
    model = equation.Logistic
    serializer_class = serializer.LogisticSerializer

class LogisticUpdateAPIView(base_api.UpdateAPIView):
    model = equation.Logistic
    serializer_class = serializer.LogisticSerializer

class LogisticRemote(EquationRemote):
    model = equation.Logistic
    add_name = 'value:api_logistic_add'
    retrieve_name = 'value:api_logistic_retrieve'
    update_name = 'value:api_logistic_update'
    serializer_class = serializer.LogisticSerializer

#
# Expression
#
class ExpressionAddAPIView(AddAPIView):
    serializer_class = serializer.ExpressionSerializer

class ExpressionRetrieveAPIView(base_api.RetrieveAPIView):
    model = equation.Expression
    serializer_class = serializer.ExpressionSerializer

class ExpressionUpdateAPIView(base_api.UpdateAPIView):
    model = equation.Expression
    serializer_class = serializer.ExpressionSerializer

class ExpressionRemote(EquationRemote):
    model = equation.Expression
    add_name = 'value:api_expression_add'
    retrieve_name = 'value:api_expression_retrieve'
    update_name = 'value:api_expression_update'
    serializer_class = serializer.ExpressionSerializer
