from rest_framework import serializers
from accounts.models import CustomUser
from .models import Project, Prefix

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'title', 'status', 'note', 'member')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'first_name', 'last_name', 'email')
        read_only_fields = ('id', 'username', 'first_name', 'last_name', 'email')

class PrefixSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prefix
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at', 'prefix', 'note')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')