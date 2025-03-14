from rest_framework import serializers
from .models import Density, Material

class DensitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Density
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'prefix', 'unit', 'measured')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ('id', 'updated_by', 'updated_at', 'name', 'density', 'fraction')
        read_only_fields = ('id', 'updated_by', 'updated_at')