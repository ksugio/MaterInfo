from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'username', 'password', 'first_name', 'last_name', 'email', 'is_superuser', 'is_manager',
                  'idnumber', 'fullname', 'postalcode', 'address', 'telephone', 'birthday')
        read_only_fields = ('id', 'username')
