from rest_framework import serializers
from .models import Schedule, Plan

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'xlabel', 'xlabel_step', 'color', 'tob', 'current')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'person')

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'start', 'finish', 'complete', 'person', 'note')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')
