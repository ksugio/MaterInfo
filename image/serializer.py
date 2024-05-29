from rest_framework import serializers
from .models.image import Image
from .models.filter import Filter
from .models.size import Size
from .models.ln2d import LN2D
from .models.imfp import IMFP
from .models import process

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'file', 'scale', 'scaleunit', 'scalepixels',
                  'device', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class FilterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filter
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'template', 'format', 'alias', 'file',
                  'pixelsize', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class FilterAliasSerializer(serializers.Serializer):
    template = serializers.IntegerField()

    def create(self, validated_data):
        id = validated_data['template']
        user = validated_data['user']
        upper = validated_data['upper']
        source = Filter.objects.get(id=id)
        title = source.title + ' (Alias)'
        object = Filter.objects.create(created_by=user, updated_by=user, upper=upper,
                                       title=title, alias=source.id)
        return object

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'prefix', 'mindia', 'roiarea', 'results',
                  'file', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class LN2DSerializer(serializers.ModelSerializer):
    class Meta:
        model = LN2D
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'prefix', 'lnmax', 'ntrials', 'randseed', 'areafraction',
                  'ln2d_tot', 'ln2d_ave', 'ln2d_var', 'ln2dr_tot', 'ln2dr_ave', 'ln2dr_var',
                  'file', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

class IMFPSerializer(serializers.ModelSerializer):
    class Meta:
        model = IMFP
        fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at',
                  'title', 'status', 'note', 'prefix', 'barrier', 'nclass', 'ntrials', 'randseed',
                  'single_ave', 'single_std', 'double_ave', 'double_std',
                  'file', 'unique')
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_by', 'updated_at')

#
# Process Serializer
#
class ProcessSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Process
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class ResizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Resize
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order', 'width', 'height')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class TrimSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Trim
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order', 'startx', 'starty', 'endx', 'endy')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class SmoothingSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Smoothing
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order', 'method', 'size', 'sigma0', 'sigma1')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class ThresholdSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Threshold
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order', 'method', 'thresh', 'blocksize', 'parameter', 'invert')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class MolphologySerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Molphology
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order', 'method', 'iteration', 'kernelsize')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class DrawScaleSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.DrawScale
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order', 'scale', 'width',
                  'fontsize', 'pos', 'color', 'marginx', 'marginy', 'bg', 'bgcolor')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class ToneSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Tone
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order', 'method',
                  'min', 'max', 'low', 'high', 'invert', 'option')
        read_only_fields = ('id', 'updated_by', 'updated_at')

class TransformSerializer(serializers.ModelSerializer):
    class Meta:
        model = process.Transform
        fields = ('id', 'updated_by', 'updated_at', 'name', 'order', 'method', 'angle')
        read_only_fields = ('id', 'updated_by', 'updated_at')
