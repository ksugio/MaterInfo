from rest_framework import serializers
from .models import Sample

class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'title', 'status', 'note')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')
