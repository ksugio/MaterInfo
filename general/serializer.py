from rest_framework import serializers
from .models import General

class GeneralSerializer(serializers.ModelSerializer):
    class Meta:
        model = General
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'prefix', 'value')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')