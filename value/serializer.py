from rest_framework import serializers
from .models.value import Value
from .models.filter import Filter
from .models.aggregate import Aggregate
from .models.curve import Curve
from .models import process, equation

class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'file', 'datatype', 'disp_head', 'disp_tail',
                  'delimiter', 'encoding', 'skiprows', 'skipends', 'header',
                  'startstring', 'endstring')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'template', 'disp_head', 'disp_tail', 'alias', 'file')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class FilterAliasSerializer(serializers.Serializer):
    template = serializers.IntegerField()

    def create(self, validated_data):
        id = validated_data['template']
        user = validated_data['user']
        upper = validated_data['upper']
        source = Filter.objects.get(id=id)
        title = source.title + ' (Alias)'
        object = Filter.objects.create(created_by=user, updated_by=user, upper=upper,
                                       title=title, alias=source.id)
        return object

class FilterImportSerializer(serializers.Serializer):
    template = serializers.IntegerField()
    title = serializers.CharField(max_length=100)

    def create(self, validated_data):
        id = validated_data['template']
        title = validated_data['title']
        user = validated_data['user']
        upper = validated_data['upper']
        source = Filter.objects.get(id=id)
        object = Filter.objects.create(created_by=user, updated_by=user, upper=upper, title=title, note=source.note)
        processes = Process.objects.filter(upper=source)
        for process in processes:
            process.create_copy(user, object)
        return object

class AggregateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aggregate
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'prefix', 'column',
                  'mean', 'std', 'min', 'median', 'max')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class CurveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Curve
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'prefix', 'template', 'columnx', 'columny', 'params', 'alias')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

#
# Process Serializer
#
class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Process
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class SelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Select
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'columns', 'newnames')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class TrimSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Trim
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'start_method', 'start_index', 'start_target', 'start_value',
                  'end_method', 'end_index', 'end_target', 'end_value', 'disp')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class OperateSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Operate
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'method', 'targetcolumn', 'useindex', 'const', 'column',
                  'newname', 'replace', 'disp')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class RollingSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Rolling
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'method', 'window', 'targetcolumn', 'center',
                  'newname', 'replace', 'disp')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class ReduceSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Reduce
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order', 'step')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class GradientSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Gradient
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'x_target', 'y_target', 'newname', 'disp')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class DropSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Drop
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order', 'columns')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Query
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'condition')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class EvalSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Eval
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'expr', 'newname')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class BeadsSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Beads
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'targetcolumn', 'newname', 'withbg', 'leftext', 'rightext',
                  'fc', 'amp', 'disp')
        read_only_fields = ('id', 'updated_by', 'updated_at')

#
# Equation Serializer
#
class EquationSerializer(serializers.ModelSerializer):
    class Meta:
        model = equation.Equation
        fields = ('id', 'updated_by', 'updated_at', 'name')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class ConstantSerializer(serializers.ModelSerializer):
    class Meta:
        model = equation.Constant
        fields = ('id', 'updated_by', 'updated_at', 'name',
                  'prefix', 'const', 'min', 'max')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class GaussianSerializer(serializers.ModelSerializer):
    class Meta:
        model = equation.Gaussian
        fields = ('id', 'updated_by', 'updated_at', 'name',
                  'prefix', 'center', 'height', 'width',
                  'center_min', 'height_min', 'width_min',
                  'center_max', 'height_max', 'width_max',)
        read_only_fields = ('id', 'updated_by', 'updated_at')

class LinearSerializer(serializers.ModelSerializer):
    class Meta:
        model = equation.Linear
        fields = ('id', 'updated_by', 'updated_at', 'name',
                  'prefix', 'slope', 'inter', 'slope_min', 'inter_min',
                  'slope_max', 'inter_max')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class QuadraticSerializer(serializers.ModelSerializer):
    class Meta:
        model = equation.Quadratic
        fields = ('id', 'updated_by', 'updated_at', 'name',
                  'prefix', 'a_val', 'b_val', 'c_val',
                  'a_min', 'b_min', 'c_min', 'a_max', 'b_max', 'c_max')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class PolynomialSerializer(serializers.ModelSerializer):
    class Meta:
        model = equation.Polynomial
        fields = ('id', 'updated_by', 'updated_at', 'name',
                  'prefix', 'values', 'mins', 'maxs')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class ExponentialSerializer(serializers.ModelSerializer):
    class Meta:
        model = equation.Exponential
        fields = ('id', 'updated_by', 'updated_at', 'name',
                  'prefix', 'amp', 'decay', 'amp_min', 'decay_min',
                  'amp_max', 'decay_max')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class PowerLawSerializer(serializers.ModelSerializer):
    class Meta:
        model = equation.PowerLaw
        fields = ('id', 'updated_by', 'updated_at', 'name',
                  'prefix', 'amp', 'exp', 'amp_min', 'exp_min',
                  'amp_max', 'exp_max')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class SineSerializer(serializers.ModelSerializer):
    class Meta:
        model = equation.Sine
        fields = ('id', 'updated_by', 'updated_at', 'name',
                  'prefix', 'amp', 'freq', 'shift',
                  'amp_min', 'freq_min', 'shift_min',
                  'amp_max', 'freq_max', 'shift_max')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class LogisticSerializer(serializers.ModelSerializer):
    class Meta:
        model = equation.Logistic
        fields = ('id', 'updated_by', 'updated_at', 'name',
                  'prefix', 'K_val', 'A_val', 'x0_val',
                  'K_min', 'A_min', 'x0_min',
                  'K_max', 'A_max', 'x0_max')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class ExpressionSerializer(serializers.ModelSerializer):
    class Meta:
        model = equation.Expression
        fields = ('id', 'updated_by', 'updated_at', 'name',
                  'expr', 'values', 'mins', 'maxs')
        read_only_fields = ('id', 'updated_by', 'updated_at')
