# Generated by Django 4.2 on 2024-02-27 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import image.models.process
import project.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sample', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('template', models.BooleanField(default=False, verbose_name='Template')),
                ('format', models.PositiveSmallIntegerField(choices=[(0, 'PNG'), (1, 'JPEG')], default=0, verbose_name='Format')),
                ('alias', models.IntegerField(blank=True, null=True, verbose_name='Alias ID')),
                ('file', models.ImageField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='Image')),
                ('pixelsize', models.FloatField(blank=True, null=True, verbose_name='Pixel Size')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('name', models.CharField(blank=True, max_length=16, verbose_name='Name')),
                ('order', models.SmallIntegerField(verbose_name='Order')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DrawScale',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='image.process')),
                ('scale', models.CharField(default=1.0, max_length=32, verbose_name='Scale')),
                ('width', models.PositiveSmallIntegerField(default=10, verbose_name='Width')),
                ('fontsize', models.PositiveSmallIntegerField(default=50, verbose_name='Fontsize')),
                ('pos', models.PositiveSmallIntegerField(choices=[(0, 'BottomRight'), (1, 'TopRight'), (2, 'TopLeft'), (3, 'BottomLeft')], default=0, verbose_name='Position')),
                ('color', models.PositiveSmallIntegerField(choices=[(0, 'White'), (1, 'Olive'), (2, 'Yellow'), (3, 'Fuchsia'), (4, 'Silver'), (5, 'Aqua'), (6, 'Lime'), (7, 'Red'), (8, 'Gray'), (9, 'Blue'), (10, 'Green'), (11, 'Purple'), (12, 'Black'), (13, 'Navy'), (14, 'Teal'), (15, 'Maroon')], default=0, verbose_name='Color')),
                ('marginx', models.PositiveSmallIntegerField(default=10, verbose_name='Margin X')),
                ('marginy', models.PositiveSmallIntegerField(default=10, verbose_name='Margin Y')),
                ('bg', models.BooleanField(default=False, verbose_name='BG')),
                ('bgcolor', models.PositiveSmallIntegerField(choices=[(0, 'White'), (1, 'Olive'), (2, 'Yellow'), (3, 'Fuchsia'), (4, 'Silver'), (5, 'Aqua'), (6, 'Lime'), (7, 'Red'), (8, 'Gray'), (9, 'Blue'), (10, 'Green'), (11, 'Purple'), (12, 'Black'), (13, 'Navy'), (14, 'Teal'), (15, 'Maroon')], default=0, verbose_name='BG Color')),
            ],
            options={
                'abstract': False,
            },
            bases=('image.process',),
        ),
        migrations.CreateModel(
            name='Molphology',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='image.process')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'Opening'), (1, 'Closing'), (2, 'Erosion'), (3, 'Dilation'), (4, 'Gradient'), (5, 'TopHat'), (6, 'BlackHat')], default=0, verbose_name='Method')),
                ('iteration', models.PositiveSmallIntegerField(default=1, verbose_name='Iteration')),
                ('kernelsize', models.PositiveSmallIntegerField(default=3, verbose_name='KernelSize')),
            ],
            options={
                'abstract': False,
            },
            bases=('image.process',),
        ),
        migrations.CreateModel(
            name='Resize',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='image.process')),
                ('width', models.PositiveSmallIntegerField(default=0, verbose_name='Width')),
                ('height', models.PositiveSmallIntegerField(default=0, verbose_name='Height')),
            ],
            options={
                'abstract': False,
            },
            bases=('image.process',),
        ),
        migrations.CreateModel(
            name='Smoothing',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='image.process')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'Blur'), (1, 'Gaussian'), (2, 'Median'), (3, 'Bilateral')], default=0, verbose_name='Method')),
                ('size', models.PositiveSmallIntegerField(default=3, validators=[image.models.process.CheckOdd], verbose_name='Size')),
                ('sigma0', models.FloatField(default=1.0, verbose_name='Sigma0')),
                ('sigma1', models.FloatField(default=1.0, verbose_name='Sigma1')),
            ],
            options={
                'abstract': False,
            },
            bases=('image.process',),
        ),
        migrations.CreateModel(
            name='Threshold',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='image.process')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'Simple'), (1, 'Otsu'), (2, 'Adaptive Mean'), (3, 'Adaptive Gauss')], default=0, verbose_name='Method')),
                ('thresh', models.PositiveSmallIntegerField(default=128, verbose_name='Threshold')),
                ('blocksize', models.PositiveSmallIntegerField(default=3, validators=[image.models.process.CheckOdd], verbose_name='Blocksize')),
                ('parameter', models.SmallIntegerField(default=0, verbose_name='Parameter')),
                ('invert', models.BooleanField(default=False, verbose_name='Invert')),
            ],
            options={
                'abstract': False,
            },
            bases=('image.process',),
        ),
        migrations.CreateModel(
            name='Tone',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='image.process')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'Linear'), (1, 'Gamma'), (2, 'Sigmoid'), (3, 'Solarization'), (4, 'Posterization')], default=0, verbose_name='Method')),
                ('min', models.PositiveSmallIntegerField(default=0, validators=[image.models.process.Check256], verbose_name='Min')),
                ('max', models.PositiveSmallIntegerField(default=255, validators=[image.models.process.Check256], verbose_name='Max')),
                ('low', models.PositiveSmallIntegerField(default=0, validators=[image.models.process.Check256], verbose_name='Low')),
                ('high', models.PositiveSmallIntegerField(default=255, validators=[image.models.process.Check256], verbose_name='High')),
                ('invert', models.BooleanField(default=False, verbose_name='Invert')),
                ('option', models.FloatField(blank=True, default=1.0, verbose_name='Option')),
            ],
            options={
                'abstract': False,
            },
            bases=('image.process',),
        ),
        migrations.CreateModel(
            name='Transform',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='image.process')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'Rotate'), (1, 'Rotate90'), (2, 'Rotate-90'), (3, 'Rotate180'), (4, 'UpDown'), (5, 'LeftRight'), (6, 'UpDownLeftRight')], default=0, verbose_name='Method')),
                ('angle', models.FloatField(default=0, verbose_name='Angle')),
            ],
            options={
                'abstract': False,
            },
            bases=('image.process',),
        ),
        migrations.CreateModel(
            name='Trim',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='image.process')),
                ('startx', models.PositiveSmallIntegerField(default=0, verbose_name='StartX')),
                ('starty', models.PositiveSmallIntegerField(default=0, verbose_name='StartY')),
                ('endx', models.PositiveSmallIntegerField(default=0, verbose_name='EndX')),
                ('endy', models.PositiveSmallIntegerField(default=0, verbose_name='EndY')),
            ],
            options={
                'abstract': False,
            },
            bases=('image.process',),
        ),
        migrations.CreateModel(
            name='Size',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('prefix', models.PositiveIntegerField(default=0, verbose_name='Prefix')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('mindia', models.FloatField(default=1.0, verbose_name='Minimum Diameter')),
                ('areafraction', models.FloatField(blank=True, null=True, verbose_name='AreaFraction')),
                ('numberdensity', models.FloatField(blank=True, null=True, verbose_name='NumberDensity')),
                ('diameter_mean', models.FloatField(blank=True, null=True, verbose_name='Diameter_mean')),
                ('diameter_std', models.FloatField(blank=True, null=True, verbose_name='Diameter_std')),
                ('diameter_min', models.FloatField(blank=True, null=True, verbose_name='Diameter_min')),
                ('diameter_median', models.FloatField(blank=True, null=True, verbose_name='Diameter_median')),
                ('diameter_max', models.FloatField(blank=True, null=True, verbose_name='Diameter_max')),
                ('longside_mean', models.FloatField(blank=True, null=True, verbose_name='LongSide_mean')),
                ('longside_std', models.FloatField(blank=True, null=True, verbose_name='LongSide_std')),
                ('longside_min', models.FloatField(blank=True, null=True, verbose_name='LongSide_min')),
                ('longside_median', models.FloatField(blank=True, null=True, verbose_name='LongSide_median')),
                ('longside_max', models.FloatField(blank=True, null=True, verbose_name='LongSide_max')),
                ('narrowside_mean', models.FloatField(blank=True, null=True, verbose_name='NarrowSide_mean')),
                ('narrowside_std', models.FloatField(blank=True, null=True, verbose_name='NarrowSide_std')),
                ('narrowside_min', models.FloatField(blank=True, null=True, verbose_name='NarrowSide_min')),
                ('narrowside_median', models.FloatField(blank=True, null=True, verbose_name='NarrowSide_median')),
                ('narrowside_max', models.FloatField(blank=True, null=True, verbose_name='NarrowSide_max')),
                ('aspectratio_mean', models.FloatField(blank=True, null=True, verbose_name='AspectRatio_mean')),
                ('aspectratio_std', models.FloatField(blank=True, null=True, verbose_name='AspectRatio_std')),
                ('aspectratio_min', models.FloatField(blank=True, null=True, verbose_name='AspectRatio_min')),
                ('aspectratio_median', models.FloatField(blank=True, null=True, verbose_name='AspectRatio_median')),
                ('aspectratio_max', models.FloatField(blank=True, null=True, verbose_name='AspectRatio_max')),
                ('circularity_mean', models.FloatField(blank=True, null=True, verbose_name='Circularity_mean')),
                ('circularity_std', models.FloatField(blank=True, null=True, verbose_name='Circularity_std')),
                ('circularity_min', models.FloatField(blank=True, null=True, verbose_name='Circularity_min')),
                ('circularity_median', models.FloatField(blank=True, null=True, verbose_name='Circularity_median')),
                ('circularity_max', models.FloatField(blank=True, null=True, verbose_name='Circularity_max')),
                ('angle_mean', models.FloatField(blank=True, null=True, verbose_name='Angle_mean')),
                ('angle_std', models.FloatField(blank=True, null=True, verbose_name='Angle_std')),
                ('angle_min', models.FloatField(blank=True, null=True, verbose_name='Angle_min')),
                ('angle_median', models.FloatField(blank=True, null=True, verbose_name='Angle_median')),
                ('angle_max', models.FloatField(blank=True, null=True, verbose_name='Angle_max')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='Measure file')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='LN2D',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('prefix', models.PositiveIntegerField(default=0, verbose_name='Prefix')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('lnmax', models.PositiveSmallIntegerField(default=50, verbose_name='LNMax')),
                ('ntrials', models.PositiveIntegerField(default=1000000, verbose_name='NTrials')),
                ('randseed', models.PositiveIntegerField(default=123456789, verbose_name='RandSeed')),
                ('areafraction', models.FloatField(blank=True, null=True, verbose_name='AreaFraction')),
                ('ln2d_tot', models.PositiveIntegerField(blank=True, null=True, verbose_name='LN2D_tot')),
                ('ln2d_ave', models.FloatField(blank=True, null=True, verbose_name='LN2D_ave')),
                ('ln2d_var', models.FloatField(blank=True, null=True, verbose_name='LN2D_var')),
                ('ln2dr_tot', models.PositiveIntegerField(blank=True, null=True, verbose_name='LN2DR_tot')),
                ('ln2dr_ave', models.FloatField(blank=True, null=True, verbose_name='LN2DR_ave')),
                ('ln2dr_var', models.FloatField(blank=True, null=True, verbose_name='LN2DR_var')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='Measure file')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IMFP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('prefix', models.PositiveIntegerField(default=0, verbose_name='Prefix')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('barrier', models.PositiveSmallIntegerField(choices=[(0, 'White'), (2, 'Black')], default=0, verbose_name='Barrier')),
                ('nclass', models.PositiveSmallIntegerField(default=5000, verbose_name='NClass')),
                ('ntrials', models.PositiveIntegerField(default=1000000, verbose_name='NTrials')),
                ('randseed', models.PositiveIntegerField(default=123456789, verbose_name='RandSeed')),
                ('single_ave', models.FloatField(blank=True, null=True, verbose_name='Single_ave')),
                ('single_std', models.FloatField(blank=True, null=True, verbose_name='Single_std')),
                ('double_ave', models.FloatField(blank=True, null=True, verbose_name='Double_ave')),
                ('double_std', models.FloatField(blank=True, null=True, verbose_name='Double_std')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='Measure file')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('file', models.ImageField(upload_to=project.models.ModelUploadTo, verbose_name='Image')),
                ('scale', models.FloatField(default=1.0, verbose_name='Scale')),
                ('scaleunit', models.PositiveSmallIntegerField(choices=[(0, 'pixel'), (1, 'kilometer'), (2, 'meter'), (3, 'millimeter'), (4, 'micrometer'), (5, 'nanometer')], default=0, verbose_name='Scale unit')),
                ('scalepixels', models.PositiveIntegerField(default=1, verbose_name='Scale pixels')),
                ('device', models.PositiveSmallIntegerField(choices=[(0, 'Camera'), (1, 'OM'), (2, 'SEM'), (3, 'EPMA'), (4, 'EDS'), (5, 'EBSD'), (6, 'TEM'), (7, 'XRAY')], default=0, verbose_name='Device')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='sample.sample', verbose_name='Sample')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='filter',
            name='upper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='image.image', verbose_name='Image'),
        ),
    ]
