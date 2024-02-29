from rest_framework import serializers
from .models import Density

class DensitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Density
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'prefix', 'unit', 'measured', 'theoretical')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

