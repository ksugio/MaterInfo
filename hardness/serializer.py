from rest_framework import serializers
from .models import Hardness, Value

class HardnessSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hardness
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'prefix', 'unit', 'load', 'load_unit', 'time')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
        fields = ('id', 'updated_by', 'updated_at', 'value', 'status')
        read_only_fields = ('id', 'updated_by', 'updated_at')
