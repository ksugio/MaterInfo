# Generated by Django 4.2 on 2024-02-27 09:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import project.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('project', '__first__'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Classification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('scaler', models.PositiveSmallIntegerField(choices=[(0, 'None'), (1, 'MinMax'), (2, 'Standard')], default=0, verbose_name='Scaler')),
                ('pca', models.BooleanField(default=False, verbose_name='PCA')),
                ('n_components', models.PositiveSmallIntegerField(default=8, verbose_name='Number of components')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'Ridge'), (1, 'Logistic'), (2, 'GaussianProcess'), (3, 'GaussianNB'), (4, 'KNeighbors'), (5, 'RandomForest'), (6, 'GradientBoosting'), (7, 'LinearSVC'), (8, 'SVC'), (9, 'MLPC'), (10, 'XGBoost'), (11, 'LightGBM')], default=0, verbose_name='Method')),
                ('hparam', models.TextField(blank=True, verbose_name='Hyperparameter')),
                ('objective', models.CharField(max_length=50, verbose_name='Objective')),
                ('drop', models.CharField(blank=True, max_length=250, verbose_name='Drop columns')),
                ('nsplits', models.PositiveSmallIntegerField(default=5, verbose_name='Number of splits')),
                ('random', models.PositiveIntegerField(blank=True, null=True, verbose_name='Random State')),
                ('ntrials', models.PositiveIntegerField(default=20, verbose_name='Number of trials')),
                ('nplot', models.PositiveSmallIntegerField(default=10, verbose_name='Number of plot features')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='Model file')),
                ('file_type', models.PositiveSmallIntegerField(default=0, verbose_name='File type')),
                ('results', models.TextField(blank=True, verbose_name='JSON Results')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Collect',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('remoteurl', models.URLField(blank=True, verbose_name='Remote URL')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('projectids', models.CharField(blank=True, max_length=100, verbose_name='Other Project IDs')),
                ('disp_head', models.PositiveIntegerField(default=50, verbose_name='Display Head')),
                ('disp_tail', models.PositiveIntegerField(default=50, verbose_name='Display Tail')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='Feature file')),
                ('columns_text', models.TextField(blank=True, verbose_name='Columns Text')),
                ('overview_text', models.TextField(blank=True, verbose_name='Overview Text')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='project.project', verbose_name='Project')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Filter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('disp_head', models.PositiveIntegerField(default=50, verbose_name='Display Head')),
                ('disp_tail', models.PositiveIntegerField(default=50, verbose_name='Display Tail')),
                ('hist_bins', models.PositiveIntegerField(default=10, verbose_name='Histgram Bins')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='File')),
                ('columns_text', models.TextField(blank=True, verbose_name='Columns Text')),
                ('describe', models.TextField(blank=True, verbose_name='Describe')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collect.collect', verbose_name='Collect')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('name', models.CharField(blank=True, max_length=16, verbose_name='Name')),
                ('order', models.SmallIntegerField(verbose_name='Order')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collect.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Agg',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collect.process')),
                ('groupby', models.PositiveSmallIntegerField(choices=[(0, 'Project_id'), (1, 'Sample_id'), (2, 'Image_id'), (3, 'Image_Filter_id'), (4, 'Value_id'), (5, 'Value_Filter_id')], default=1, verbose_name='Groupby')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'Mean'), (1, 'Median'), (2, 'Min'), (3, 'Max')], default=0, verbose_name='Method')),
            ],
            options={
                'abstract': False,
            },
            bases=('collect.process',),
        ),
        migrations.CreateModel(
            name='Drop',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collect.process')),
                ('start', models.CharField(max_length=50, verbose_name='Start column')),
                ('end', models.CharField(max_length=50, verbose_name='End column')),
            ],
            options={
                'abstract': False,
            },
            bases=('collect.process',),
        ),
        migrations.CreateModel(
            name='Dropna',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collect.process')),
                ('axis', models.PositiveSmallIntegerField(choices=[(0, 'rows'), (1, 'columns')], default=0, verbose_name='Axis')),
                ('how', models.PositiveSmallIntegerField(choices=[(0, 'any'), (1, 'all')], default=0, verbose_name='How')),
                ('thresh', models.PositiveIntegerField(blank=True, null=True, verbose_name='Thresh')),
            ],
            options={
                'abstract': False,
            },
            bases=('collect.process',),
        ),
        migrations.CreateModel(
            name='Exclude',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collect.process')),
                ('percentile', models.FloatField(verbose_name='Percentile')),
                ('condition', models.PositiveSmallIntegerField(choices=[(0, 'Greater'), (1, 'Smaller')], default=0, verbose_name='Condition')),
                ('start', models.CharField(max_length=50, verbose_name='Start column')),
                ('end', models.CharField(max_length=50, verbose_name='End column')),
            ],
            options={
                'abstract': False,
            },
            bases=('collect.process',),
        ),
        migrations.CreateModel(
            name='Fillna',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collect.process')),
                ('groupby', models.PositiveSmallIntegerField(choices=[(0, 'Project_id'), (1, 'Sample_id'), (2, 'Image_id'), (3, 'Image_Filter_id'), (4, 'Value_id'), (5, 'Value_Filter_id')], default=1, verbose_name='Groupby')),
                ('start', models.CharField(max_length=50, verbose_name='Start column')),
                ('end', models.CharField(max_length=50, verbose_name='End column')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'Mean'), (1, 'Median'), (2, 'FBFill'), (3, 'BFFill')], default=0, verbose_name='Method')),
            ],
            options={
                'abstract': False,
            },
            bases=('collect.process',),
        ),
        migrations.CreateModel(
            name='PCAF',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collect.process')),
                ('scaler', models.PositiveSmallIntegerField(choices=[(0, 'None'), (1, 'MinMax'), (2, 'Standard')], default=2, verbose_name='Scaler')),
                ('n_components', models.PositiveSmallIntegerField(default=8, verbose_name='N Components')),
                ('start', models.CharField(max_length=50, verbose_name='Start column')),
                ('end', models.CharField(max_length=50, verbose_name='End column')),
                ('prefix', models.CharField(max_length=100, verbose_name='Prefix')),
                ('replace', models.BooleanField(default=True, verbose_name='Replace')),
            ],
            options={
                'abstract': False,
            },
            bases=('collect.process',),
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collect.process')),
                ('condition', models.TextField(verbose_name='Condition')),
            ],
            options={
                'abstract': False,
            },
            bases=('collect.process',),
        ),
        migrations.CreateModel(
            name='Select',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='collect.process')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'Keep'), (1, 'Drop')], default=0, verbose_name='Method')),
                ('columns', models.TextField(blank=True, verbose_name='Columns')),
            ],
            options={
                'abstract': False,
            },
            bases=('collect.process',),
        ),
        migrations.CreateModel(
            name='Regression',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('scaler', models.PositiveSmallIntegerField(choices=[(0, 'None'), (1, 'MinMax'), (2, 'Standard')], default=0, verbose_name='Scaler')),
                ('pca', models.BooleanField(default=False, verbose_name='PCA')),
                ('n_components', models.PositiveSmallIntegerField(default=8, verbose_name='PCA n_components')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'Linear'), (1, 'Ridge'), (2, 'Lasso'), (3, 'ElasticNet'), (4, 'GaussianProcess'), (5, 'KNeighbors'), (6, 'RandomForest'), (7, 'GradientBoosting'), (8, 'SVR'), (9, 'MLPR'), (10, 'XGBoost'), (11, 'LightGBM')], default=0, verbose_name='Method')),
                ('hparam', models.TextField(blank=True, verbose_name='Hyperparameter')),
                ('objective', models.CharField(max_length=50, verbose_name='Objective')),
                ('drop', models.CharField(blank=True, max_length=250, verbose_name='Drop columns')),
                ('nsplits', models.PositiveSmallIntegerField(default=5, verbose_name='Number of splits')),
                ('random', models.PositiveIntegerField(blank=True, null=True, verbose_name='Random State')),
                ('ntrials', models.PositiveIntegerField(default=20, verbose_name='Number of trials')),
                ('nplot', models.PositiveSmallIntegerField(default=10, verbose_name='Number of plot features')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='Prediction file')),
                ('file2', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='Model file')),
                ('file2_type', models.PositiveSmallIntegerField(default=0, verbose_name='File2 type')),
                ('results', models.TextField(blank=True, verbose_name='JSON Results')),
                ('unique', models.CharField(default=project.models.UniqueID, max_length=36, verbose_name='Unique ID')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collect.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='RegreSHAP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('test_size', models.FloatField(default=0.2, verbose_name='Test Size')),
                ('results', models.TextField(blank=True, verbose_name='JSON Results')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collect.regression', verbose_name='Regression')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Reduction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('scaler', models.PositiveSmallIntegerField(choices=[(0, 'None'), (1, 'MinMax'), (2, 'Standard')], default=2, verbose_name='Scaler')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'PCA'), (1, 'KernelPCA'), (2, 'SparsePCA'), (3, 'SpectralEmbedding'), (4, 'Isomap'), (5, 'LocallyLinearEmbedding'), (6, 't-SNE'), (7, 'UMAP')], default=0, verbose_name='Method')),
                ('hparam', models.TextField(blank=True, verbose_name='Hyperparameter')),
                ('drop', models.CharField(blank=True, max_length=250, verbose_name='Drop columns')),
                ('label', models.CharField(blank=True, max_length=50, null=True, verbose_name='Label')),
                ('colormap', models.PositiveSmallIntegerField(choices=[(0, 'viridis'), (1, 'gray'), (2, 'rainbow'), (3, 'jet')], default=0, verbose_name='Colormap')),
                ('colorbar', models.BooleanField(default=False, verbose_name='Colorbar')),
                ('nplot', models.PositiveSmallIntegerField(default=10, verbose_name='Number of plot features')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='File')),
                ('results', models.TextField(blank=True, verbose_name='JSON Results')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collect.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Inverse',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('regression1', models.CharField(blank=True, max_length=36, verbose_name='Regression 1')),
                ('target1', models.FloatField(default=0.0, verbose_name='Target value 1')),
                ('regression2', models.CharField(blank=True, max_length=36, verbose_name='Regression 2')),
                ('target2', models.FloatField(default=0.0, verbose_name='Target value 2')),
                ('regression3', models.CharField(blank=True, max_length=36, verbose_name='Regression 3')),
                ('target3', models.FloatField(default=0.0, verbose_name='Target value 3')),
                ('ntrials', models.PositiveIntegerField(default=100, verbose_name='Number of trials')),
                ('seed', models.IntegerField(default=0, verbose_name='Seed of sampler')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='File')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collect.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Correlation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'pearson'), (1, 'kendall'), (2, 'spearman')], default=0, verbose_name='Method')),
                ('drop', models.BooleanField(default=True, verbose_name='Drop Same Group')),
                ('mincorr', models.FloatField(default=0.7, verbose_name='Minimum Correlation')),
                ('sizex', models.FloatField(default=9.6, verbose_name='Size X')),
                ('sizey', models.FloatField(default=9.6, verbose_name='Size Y')),
                ('colormap', models.PositiveSmallIntegerField(choices=[(0, 'RdBu'), (1, 'PiYG'), (2, 'PRGn'), (3, 'BrBG'), (4, 'PuOr'), (5, 'RdGy'), (6, 'RdYlBu'), (7, 'RdYlGn'), (8, 'Spectral'), (9, 'coolwarm'), (10, 'bwr'), (11, 'seismic')], default=0, verbose_name='Colormap')),
                ('colorbar', models.BooleanField(default=False, verbose_name='Colorbar')),
                ('annotate', models.BooleanField(default=False, verbose_name='Annotate')),
                ('label', models.CharField(blank=True, max_length=50, null=True, verbose_name='Label')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='File')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collect.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Clustering',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('scaler', models.PositiveSmallIntegerField(choices=[(0, 'None'), (1, 'MinMax'), (2, 'Standard')], default=0, verbose_name='Scaler')),
                ('reduction', models.PositiveSmallIntegerField(choices=[(0, 'PCA'), (1, 'Isomap'), (2, 't-SNE'), (3, 'UMAP')], default=0, verbose_name='Reduction')),
                ('n_components', models.PositiveSmallIntegerField(default=8, verbose_name='Number of PCA components')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'K-Means'), (1, 'Mean-shift'), (2, 'SpectralClustering'), (3, 'AgglomerativeClustering'), (4, 'DBSCAN'), (5, 'GaussianMixtures')], default=0, verbose_name='Method')),
                ('hparam', models.TextField(blank=True, verbose_name='Hyperparameter')),
                ('drop', models.CharField(blank=True, max_length=250, verbose_name='Drop columns')),
                ('colormap', models.PositiveSmallIntegerField(choices=[(0, 'viridis'), (1, 'gray'), (2, 'rainbow'), (3, 'jet')], default=0, verbose_name='Colormap')),
                ('ntrials', models.PositiveIntegerField(default=20, verbose_name='Number of trials')),
                ('score', models.PositiveSmallIntegerField(choices=[(0, 'Silhouette'), (1, 'Davies-Bouldin'), (2, 'Calinski-Harabasz')], default=0, verbose_name='Score')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='File')),
                ('results', models.TextField(blank=True, verbose_name='JSON Results')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collect.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ClassSHAP',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('test_size', models.FloatField(default=0.2, verbose_name='Test Size')),
                ('results', models.TextField(blank=True, verbose_name='JSON Results')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collect.classification', verbose_name='Classification')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='classification',
            name='upper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='collect.filter', verbose_name='Filter'),
        ),
    ]
