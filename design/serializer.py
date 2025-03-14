from rest_framework import serializers
from .models.design import Design
from .models.condition import Condition
from .models.experiment import Experiment

class DesignSerializer(serializers.ModelSerializer):
    class Meta:
        model = Design
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'prefix', 'title', 'status', 'note', 'ngen', 'modelfunc',
                  'columns', 'file')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Condition
        fields = ('id', 'updated_by', 'updated_at',
                  'prefix', 'mode', 'values')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class ExperimentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experiment
        fields = ('id', 'updated_by', 'updated_at',
                  'title', 'condition', 'property', 'note')
        read_only_fields = ('id', 'updated_by', 'updated_at')
