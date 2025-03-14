from rest_framework import serializers
from .models.collect import Collect
from .models.filter import Filter
from .models.process import Process, Fillna, Dropna, Drop, Select, Agg, Query, Exclude, PCAF
from .models.reduction import Reduction
from .models.correlation import Correlation
from .models.clustering import Clustering
from .models.classification import Classification
from .models.regression import Regression
from .models.classshap import ClassSHAP
from .models.regreshap import RegreSHAP
from. models.regrepred import RegrePred
from. models.classpred import ClassPred
from .models.inverse import Inverse

class CollectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collect
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'projectids', 'disp_head', 'disp_tail',
                  'file', 'columns_text', 'overview_text', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'disp_head', 'disp_tail', 'hist_bins',
                  'file', 'columns_text', 'describe', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ReductionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reduction
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'scaler', 'method', 'hparam', 'drop',
                  'label', 'colormap', 'colorbar', 'nplot', 'file', 'results', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class CorrelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Correlation
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note',  'method', 'drop', 'mincorr',
                  'sizex', 'sizey', 'colormap', 'colorbar', 'annotate', 'label', 'file')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ClusteringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clustering
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'scaler', 'reduction', 'n_components',
                  'method', 'hparam', 'drop', 'colormap', 'ntrials', 'score', 'file',
                  'results', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ClassificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Classification
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'task_id',
                  'title', 'status', 'note', 'testsize', 'randomts', 'scaler', 'pca', 'n_components',
                  'method', 'hparam', 'objective', 'drop', 'nsplits', 'random', 'ntrials', 'nplot',
                  'file', 'file_type', 'results', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class RegressionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regression
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'task_id',
                  'title', 'status', 'note', 'testsize', 'randomts', 'scaler', 'pca', 'n_components',
                  'method', 'hparam', 'objective', 'drop', 'nsplits', 'random', 'ntrials', 'nplot',
                  'file', 'file2', 'results', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ClassSHAPSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassSHAP
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'task_id',
                  'title', 'status', 'note', 'nsample', 'use_kernel', 'results')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ClassPredSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassPred
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'task_id',
                  'title', 'status', 'note', 'file', 'objective', 'drop')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')


class RegreSHAPSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegreSHAP
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'task_id',
                  'title', 'status', 'note', 'use_kernel', 'kmeans', 'nsample', 'results')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class RegrePredSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegrePred
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'task_id',
                  'title', 'status', 'note', 'file', 'objective', 'drop')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class InverseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Inverse
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'task_id',
                  'title', 'status', 'note', 'regression1', 'target1', 'regression2', 'target2',
                  'regression3', 'target3', 'ntrials', 'seed', 'file')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Process
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class FillnaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fillna
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'groupby', 'start', 'end', 'method')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class DropnaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dropna
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'axis', 'how', 'thresh')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class DropSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drop
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'start', 'end')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class SelectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Select
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order', 'method', 'columns')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class AggSerializer(serializers.ModelSerializer):
    class Meta:
        model = Agg
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'groupby', 'method')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class QuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = Query
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'condition')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class ExcludeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exclude
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'percentile', 'condition', 'start', 'end')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class PCAFSerializer(serializers.ModelSerializer):
    class Meta:
        model = PCAF
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order',
                  'scaler', 'n_components', 'start', 'end', 'prefix', 'replace')
        read_only_fields = ('id', 'updated_by', 'updated_at')
