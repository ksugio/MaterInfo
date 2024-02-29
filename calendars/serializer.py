from rest_framework import serializers
from .models import Calendar, Plan

class CalendarSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calendar
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'start', 'finish', 'note')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')