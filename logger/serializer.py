from rest_framework import serializers
from .models import Logger

class LoggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logger
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'host', 'port', 'database', 'password', 'interval')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')
