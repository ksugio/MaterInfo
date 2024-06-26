# Generated by Django 4.2 on 2024-02-27 09:12

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import project.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('sample', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Curve',
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
                ('category', models.PositiveSmallIntegerField(choices=[(0, 'process'), (1, 'structure'), (2, 'property'), (3, 'performance')], default=0, verbose_name='Category')),
                ('template', models.BooleanField(default=False, verbose_name='Template')),
                ('columnx', models.CharField(max_length=50, verbose_name='Column X')),
                ('columny', models.CharField(max_length=50, verbose_name='Column Y')),
                ('params', models.TextField(blank=True, verbose_name='Parameters')),
                ('alias', models.IntegerField(blank=True, null=True, verbose_name='Alias ID')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Equation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('name', models.CharField(blank=True, max_length=16, verbose_name='Name')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='value.curve', verbose_name='Curve')),
            ],
            options={
                'abstract': False,
            },
        ),
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
                ('disp_head', models.PositiveIntegerField(default=50, verbose_name='Display Head')),
                ('disp_tail', models.PositiveIntegerField(default=50, verbose_name='Display Tail')),
                ('alias', models.IntegerField(blank=True, null=True, verbose_name='Alias ID')),
                ('file', models.FileField(blank=True, null=True, upload_to=project.models.ModelUploadTo, verbose_name='File')),
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
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='value.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Beads',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.process')),
                ('targetcolumn', models.CharField(max_length=50, verbose_name='Target column')),
                ('newname', models.CharField(max_length=50, verbose_name='New name')),
                ('withbg', models.BooleanField(default=False, verbose_name='With background')),
                ('leftext', models.PositiveSmallIntegerField(default=500, verbose_name='Left extend')),
                ('rightext', models.PositiveSmallIntegerField(default=500, verbose_name='Right extend')),
                ('fc', models.FloatField(default=0.006, verbose_name='Cutoff frequency')),
                ('amp', models.FloatField(default=0.8, verbose_name='Amplitude')),
                ('disp', models.PositiveSmallIntegerField(choices=[(0, 'Table'), (1, 'Plot')], default=0, verbose_name='Display')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.process',),
        ),
        migrations.CreateModel(
            name='Constant',
            fields=[
                ('equation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.equation')),
                ('prefix', models.CharField(max_length=50, verbose_name='Prefix')),
                ('const', models.FloatField(default=0.0, verbose_name='Const')),
                ('min', models.FloatField(blank=True, null=True, verbose_name='Minimum')),
                ('max', models.FloatField(blank=True, null=True, verbose_name='Maximum')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.equation',),
        ),
        migrations.CreateModel(
            name='Drop',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.process')),
                ('columns', models.CharField(max_length=300, verbose_name='Columns')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.process',),
        ),
        migrations.CreateModel(
            name='Eval',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.process')),
                ('expr', models.TextField(verbose_name='Expression')),
                ('newname', models.CharField(blank=True, max_length=50, null=True, verbose_name='New Name')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.process',),
        ),
        migrations.CreateModel(
            name='Exponential',
            fields=[
                ('equation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.equation')),
                ('prefix', models.CharField(max_length=50, verbose_name='Prefix')),
                ('amp', models.FloatField(default=0.0, verbose_name='Amplitude')),
                ('decay', models.FloatField(default=0.0, verbose_name='Decay')),
                ('amp_min', models.FloatField(blank=True, null=True, verbose_name='Amplitude Minimum')),
                ('decay_min', models.FloatField(blank=True, null=True, verbose_name='Decay Minimum')),
                ('amp_max', models.FloatField(blank=True, null=True, verbose_name='Amplitude Maximum')),
                ('decay_max', models.FloatField(blank=True, null=True, verbose_name='Decay Maximum')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.equation',),
        ),
        migrations.CreateModel(
            name='Expression',
            fields=[
                ('equation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.equation')),
                ('expr', models.TextField(default='p0 + p1 * x + p2 * x * x', verbose_name='Expression')),
                ('values', models.TextField(default='1.0, 1.0, 1.0', verbose_name='Values')),
                ('mins', models.TextField(blank=True, verbose_name='Minimums')),
                ('maxs', models.TextField(blank=True, verbose_name='Maximums')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.equation',),
        ),
        migrations.CreateModel(
            name='Gaussian',
            fields=[
                ('equation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.equation')),
                ('prefix', models.CharField(max_length=50, verbose_name='Prefix')),
                ('center', models.FloatField(default=0.0, verbose_name='Center')),
                ('height', models.FloatField(default=1.0, verbose_name='Height')),
                ('width', models.FloatField(default=1.0, verbose_name='Width')),
                ('center_min', models.FloatField(blank=True, null=True, verbose_name='Center Minimum')),
                ('height_min', models.FloatField(blank=True, null=True, verbose_name='Height Minimum')),
                ('width_min', models.FloatField(blank=True, null=True, verbose_name='Width Minimum')),
                ('center_max', models.FloatField(blank=True, null=True, verbose_name='Center Maximum')),
                ('height_max', models.FloatField(blank=True, null=True, verbose_name='Height Maximum')),
                ('width_max', models.FloatField(blank=True, null=True, verbose_name='Width Maximum')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.equation',),
        ),
        migrations.CreateModel(
            name='Gradient',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.process')),
                ('x_target', models.CharField(max_length=50, verbose_name='X target')),
                ('y_target', models.CharField(max_length=50, verbose_name='Y target')),
                ('newname', models.CharField(blank=True, max_length=50, null=True, verbose_name='New Name')),
                ('disp', models.PositiveSmallIntegerField(choices=[(0, 'Table'), (1, 'Plot')], default=0, verbose_name='Display')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.process',),
        ),
        migrations.CreateModel(
            name='Linear',
            fields=[
                ('equation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.equation')),
                ('prefix', models.CharField(max_length=50, verbose_name='Prefix')),
                ('slope', models.FloatField(default=1.0, verbose_name='Slope')),
                ('inter', models.FloatField(default=0.0, verbose_name='Intercept')),
                ('slope_min', models.FloatField(blank=True, null=True, verbose_name='Slope Minimum')),
                ('inter_min', models.FloatField(blank=True, null=True, verbose_name='Intercept Minimum')),
                ('slope_max', models.FloatField(blank=True, null=True, verbose_name='Slope Maximum')),
                ('inter_max', models.FloatField(blank=True, null=True, verbose_name='Intercept Maximum')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.equation',),
        ),
        migrations.CreateModel(
            name='Logistic',
            fields=[
                ('equation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.equation')),
                ('prefix', models.CharField(max_length=50, verbose_name='Prefix')),
                ('K_val', models.FloatField(default=0.0, verbose_name='K')),
                ('A_val', models.FloatField(default=0.0, verbose_name='A')),
                ('x0_val', models.FloatField(default=0.0, verbose_name='x0')),
                ('K_min', models.FloatField(blank=True, null=True, verbose_name='K Minimum')),
                ('A_min', models.FloatField(blank=True, null=True, verbose_name='A Minimum')),
                ('x0_min', models.FloatField(blank=True, null=True, verbose_name='x0 Minimum')),
                ('K_max', models.FloatField(blank=True, null=True, verbose_name='K Maximum')),
                ('A_max', models.FloatField(blank=True, null=True, verbose_name='A Maximum')),
                ('x0_max', models.FloatField(blank=True, null=True, verbose_name='x0 Maximum')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.equation',),
        ),
        migrations.CreateModel(
            name='Operate',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.process')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'AddConst'), (1, 'SubConst'), (2, 'MultiConst'), (3, 'DivConst'), (4, 'PowConst'), (5, 'ModConst'), (6, 'AddColumn'), (7, 'SubColumn'), (8, 'MultiColumn'), (9, 'DivColumn'), (10, 'PowColumn'), (11, 'ModColumn'), (12, 'Exp'), (13, 'Log'), (14, 'Log2'), (15, 'Log10'), (16, 'Log1p'), (17, 'Sin'), (18, 'Cos'), (19, 'Tan'), (20, 'ArcSin'), (21, 'ArcCos'), (22, 'ArcTan'), (23, 'Sqrt'), (24, 'Abs'), (25, 'Round'), (26, 'Floor'), (27, 'Ceil')], default=0, verbose_name='Method')),
                ('targetcolumn', models.CharField(blank=True, max_length=50, null=True, verbose_name='Target Column')),
                ('useindex', models.BooleanField(default=False, verbose_name='Use Index')),
                ('const', models.FloatField(blank=True, null=True, verbose_name='Const')),
                ('column', models.CharField(blank=True, max_length=50, null=True, verbose_name='Column')),
                ('newname', models.CharField(blank=True, max_length=50, null=True, verbose_name='New Name')),
                ('replace', models.BooleanField(default=False, verbose_name='Replace')),
                ('disp', models.PositiveSmallIntegerField(choices=[(0, 'Table'), (1, 'Plot')], default=0, verbose_name='Display')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.process',),
        ),
        migrations.CreateModel(
            name='Polynomial',
            fields=[
                ('equation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.equation')),
                ('prefix', models.CharField(max_length=50, verbose_name='Prefix')),
                ('values', models.TextField(default='1.0, 1.0, 1.0', verbose_name='Values')),
                ('mins', models.TextField(blank=True, verbose_name='Minimums')),
                ('maxs', models.TextField(blank=True, verbose_name='Maximums')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.equation',),
        ),
        migrations.CreateModel(
            name='PowerLaw',
            fields=[
                ('equation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.equation')),
                ('prefix', models.CharField(max_length=50, verbose_name='Prefix')),
                ('amp', models.FloatField(default=0.0, verbose_name='Amplitude')),
                ('exp', models.FloatField(default=0.0, verbose_name='Exponent')),
                ('amp_min', models.FloatField(blank=True, null=True, verbose_name='Amplitude Minimum')),
                ('exp_min', models.FloatField(blank=True, null=True, verbose_name='Exponent Minimum')),
                ('amp_max', models.FloatField(blank=True, null=True, verbose_name='Amplitude Maximum')),
                ('exp_max', models.FloatField(blank=True, null=True, verbose_name='Exponent Maximum')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.equation',),
        ),
        migrations.CreateModel(
            name='Quadratic',
            fields=[
                ('equation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.equation')),
                ('prefix', models.CharField(max_length=50, verbose_name='Prefix')),
                ('a_val', models.FloatField(default=0.0, verbose_name='A')),
                ('b_val', models.FloatField(default=0.0, verbose_name='B')),
                ('c_val', models.FloatField(default=0.0, verbose_name='C')),
                ('a_min', models.FloatField(blank=True, null=True, verbose_name='A Minimum')),
                ('b_min', models.FloatField(blank=True, null=True, verbose_name='B Minimum')),
                ('c_min', models.FloatField(blank=True, null=True, verbose_name='C Minimum')),
                ('a_max', models.FloatField(blank=True, null=True, verbose_name='A Maximum')),
                ('b_max', models.FloatField(blank=True, null=True, verbose_name='B Maximum')),
                ('c_max', models.FloatField(blank=True, null=True, verbose_name='C Maximum')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.equation',),
        ),
        migrations.CreateModel(
            name='Query',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.process')),
                ('condition', models.TextField(verbose_name='Condition')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.process',),
        ),
        migrations.CreateModel(
            name='Reduce',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.process')),
                ('step', models.PositiveSmallIntegerField(verbose_name='Step')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.process',),
        ),
        migrations.CreateModel(
            name='Rolling',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.process')),
                ('method', models.PositiveSmallIntegerField(choices=[(0, 'Mean'), (1, 'Sum')], default=0, verbose_name='Method')),
                ('window', models.PositiveSmallIntegerField(verbose_name='Window')),
                ('targetcolumn', models.CharField(max_length=50, verbose_name='Target column')),
                ('center', models.BooleanField(default=False, verbose_name='Center')),
                ('newname', models.CharField(blank=True, max_length=50, null=True, verbose_name='New Name')),
                ('replace', models.BooleanField(default=False, verbose_name='Replace')),
                ('disp', models.PositiveSmallIntegerField(choices=[(0, 'Table'), (1, 'Plot')], default=0, verbose_name='Display')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.process',),
        ),
        migrations.CreateModel(
            name='Select',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.process')),
                ('columns', models.CharField(max_length=300, verbose_name='Columns')),
                ('newnames', models.CharField(blank=True, max_length=300, null=True, verbose_name='New Names')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.process',),
        ),
        migrations.CreateModel(
            name='Sine',
            fields=[
                ('equation_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.equation')),
                ('prefix', models.CharField(max_length=50, verbose_name='Prefix')),
                ('amp', models.FloatField(default=1.0, verbose_name='Amplitude')),
                ('freq', models.FloatField(default=1.0, verbose_name='Frequency')),
                ('shift', models.FloatField(default=0.0, verbose_name='Shift')),
                ('amp_min', models.FloatField(blank=True, null=True, verbose_name='Amplitude Minimum')),
                ('freq_min', models.FloatField(blank=True, null=True, verbose_name='Frequency Minimum')),
                ('shift_min', models.FloatField(blank=True, null=True, verbose_name='Shift Minimum')),
                ('amp_max', models.FloatField(blank=True, null=True, verbose_name='Amplitude Maximum')),
                ('freq_max', models.FloatField(blank=True, null=True, verbose_name='Frequency Maximum')),
                ('shift_max', models.FloatField(blank=True, null=True, verbose_name='Shift Maximum')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.equation',),
        ),
        migrations.CreateModel(
            name='Trim',
            fields=[
                ('process_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='value.process')),
                ('start_method', models.PositiveSmallIntegerField(choices=[(0, 'First'), (1, 'Index'), (2, 'Larger'), (3, 'Smaller'), (4, 'Max'), (5, 'Min')], default=0, verbose_name='Start method')),
                ('start_index', models.PositiveIntegerField(blank=True, null=True, verbose_name='Start index')),
                ('start_target', models.CharField(blank=True, max_length=50, null=True, verbose_name='Start target')),
                ('start_value', models.FloatField(blank=True, null=True, verbose_name='Start value')),
                ('end_method', models.PositiveSmallIntegerField(choices=[(0, 'Last'), (1, 'Index'), (2, 'Larger'), (3, 'Smaller'), (4, 'Max'), (5, 'Min')], default=0, verbose_name='End method')),
                ('end_index', models.PositiveIntegerField(blank=True, null=True, verbose_name='End index')),
                ('end_target', models.CharField(blank=True, max_length=50, null=True, verbose_name='End target')),
                ('end_value', models.FloatField(blank=True, null=True, verbose_name='End value')),
                ('disp', models.PositiveSmallIntegerField(choices=[(0, 'Table'), (1, 'Plot')], default=0, verbose_name='Display')),
            ],
            options={
                'abstract': False,
            },
            bases=('value.process',),
        ),
        migrations.CreateModel(
            name='Value',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Created at')),
                ('updated_at', models.DateTimeField(verbose_name='Updated at')),
                ('remoteid', models.IntegerField(blank=True, null=True, verbose_name='Remote ID')),
                ('remoteat', models.DateTimeField(blank=True, null=True, verbose_name='Remote updated at')),
                ('localupd', models.BooleanField(default=False, verbose_name='Local updated')),
                ('delimiter', models.PositiveSmallIntegerField(choices=[(0, 'Comma'), (1, 'Space'), (2, 'Tab')], default=0, verbose_name='Delimiter')),
                ('encoding', models.PositiveSmallIntegerField(choices=[(0, 'utf-8'), (1, 'shift-jis'), (2, 'cp932')], default=0, verbose_name='Encoding')),
                ('skiprows', models.PositiveSmallIntegerField(default=0, verbose_name='Skiprows')),
                ('skipends', models.PositiveSmallIntegerField(default=0, verbose_name='Skipends')),
                ('header', models.BooleanField(default=False, verbose_name='Header')),
                ('startstring', models.CharField(blank=True, max_length=100, verbose_name='Start string')),
                ('endstring', models.CharField(blank=True, max_length=100, verbose_name='End string')),
                ('title', models.CharField(max_length=100, verbose_name='Title')),
                ('status', models.PositiveSmallIntegerField(choices=[(0, 'Valid'), (1, 'Invalid'), (2, 'Pending')], default=0, verbose_name='Status')),
                ('note', models.TextField(blank=True, verbose_name='Note')),
                ('file', models.FileField(upload_to=project.models.ModelUploadTo, verbose_name='Value file')),
                ('datatype', models.PositiveSmallIntegerField(choices=[(0, 'General'), (1, 'SSCureve'), (2, 'XRD'), (3, 'DSC')], default=0, verbose_name='Data type')),
                ('disp_head', models.PositiveIntegerField(default=50, verbose_name='Display Head')),
                ('disp_tail', models.PositiveIntegerField(default=50, verbose_name='Display Tail')),
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
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='value.value', verbose_name='Value'),
        ),
        migrations.AddField(
            model_name='curve',
            name='upper',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='value.filter', verbose_name='Filter'),
        ),
        migrations.CreateModel(
            name='Aggregate',
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
                ('category', models.PositiveSmallIntegerField(choices=[(0, 'process'), (1, 'structure'), (2, 'property'), (3, 'performance')], default=0, verbose_name='Category')),
                ('column', models.CharField(max_length=50, verbose_name='Column')),
                ('mean', models.FloatField(blank=True, null=True, verbose_name='Mean')),
                ('std', models.FloatField(blank=True, null=True, verbose_name='STD')),
                ('min', models.FloatField(blank=True, null=True, verbose_name='Min')),
                ('median', models.FloatField(blank=True, null=True, verbose_name='Median')),
                ('max', models.FloatField(blank=True, null=True, verbose_name='Max')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_created_by', to=settings.AUTH_USER_MODEL, verbose_name='Created by')),
                ('updated_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='%(app_label)s_%(class)s_updated_by', to=settings.AUTH_USER_MODEL, verbose_name='Updated by')),
                ('upper', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='value.filter', verbose_name='Filter')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
