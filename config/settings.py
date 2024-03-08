"""
Django settings for config project.

Generated by 'django-admin startproject' using Django 2.2.12.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os
import environ
from datetime import timedelta

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

env = environ.Env()
env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='v7u0d4hc403)rzi253ylbd5r@_oynt-vokf1aqpc8t=w-)0tkn')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', cast=bool, default=True)

ALLOWED_HOSTS = env('ALLOWED_HOSTS', cast=list, default=['*'])

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_bootstrap5',
    'rest_framework',
    'djoser',
    'mdeditor',
    'django_cleanup.apps.CleanupConfig',
    'accounts.apps.AccountsConfig',
    'album.apps.AlbumConfig',
    'article.apps.ArticleConfig',
    'calendars.apps.CalendarsConfig',
    'collect.apps.CollectConfig',
    'comment.apps.CommentConfig',
    'density.apps.DensityConfig',
    'document.apps.DocumentConfig',
    'general.apps.GeneralConfig',
    'hardness.apps.HardnessConfig',
    'image.apps.ImageConfig',
    'material.apps.MaterialConfig',
    'plot.apps.PlotConfig',
    'poll.apps.PollConfig',
    'project.apps.ProjectConfig',
    'public.apps.PublicConfig',
    'reference.apps.ReferenceConfig',
    'repository.apps.RepositoryConfig',
    'sample.apps.SampleConfig',
    'schedule.apps.ScheduleConfig',
    'value.apps.ValueConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
            'libraries': {
                'mifilter': 'templatetags.mifilter',
                'utils': 'templatetags.utils',
            },
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.2/ref/settings/#databases

DATABASES = {
    'default': env.db(default='sqlite:///db.sqlite3')
}

AUTHENTICATION_BACKENDS = [
    'accounts.ldap.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
]

# LDAP Settings
LDAP_SERVER = {
    'USE': env('LDAP_SERVER_USE', cast=bool, default=False),
    'HOST': env('LDAP_SERVER_HOST', default='ldap_server'),
    'PORT': env('LDAP_SERVER_PORT', cast=int, default=636),
    'USE_SSL': env('LDAP_SERVER_USE_SSL', cast=bool, default=True),
    'SEARCH_BASE': env('LDAP_SERVER_SEARCH_BASE', default='dc=matphys,dc=local'),
    'USER': env('LDAP_SERVER_USER', default='cn=admin,dc=matphys,dc=local'),
    'PASSWORD': env('LDAP_SERVER_PASSWORD', default='password'),
    'USERNAME': env('LDAP_SERVER_USERNAME', default='uid'),
    'EMAIL': env('LDAP_SERVER_EMAIL', default='mail'),
    'FIRST_NAME': env('LDAP_SERVER_FIRST_NAME', default='givenName'),
    'LAST_NAME': env('LDAP_SERVER_LAST_NAME', default='sn'),
    'CREATE_USER_PROJECT': env('LDAP_SERVER_CREATE_USER_PROJECT', cast=bool, default=True),
    'UPDATE_SERVER': env('LDAP_SERVER_UPDATE_SERVER', cast=bool, default=True),
}

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'project:list'
INDEX_URL = ['project:list', None]
#INDEX_URL = ['public:home', {'path': 'index'}]

#SECURE_SSL_REDIRECT = True
#SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Tokyo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# X-Frame-Options
X_FRAME_OPTIONS = 'SAMEORIGIN'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = env('STATIC_ROOT', default=os.path.join(BASE_DIR, 'static'))

MEDIA_URL = '/media/'
MEDIA_ROOT = env('MEDIA_ROOT', default=os.path.join(BASE_DIR, 'media'))
MEDIA_ACCEL_REDIRECT = env('MEDIA_ACCEL_REDIRECT', cast=bool, default=False)

REPOS_ROOT = env('REPOS_ROOT', default=os.path.join(BASE_DIR, 'repos'))

RANDOM_STRING_LENGTH = 17

USE_LOCAL_HOST = {
    'check': True,
    'hosts': ['http://localhost:8080'],
    'localhost': 'http://localhost:8000'
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=10),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'BLACKLIST_AFTER_ROTATION': False,
}

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_ACTIVE = env('EMAIL_ACTIVE', cast=bool, default=False)
EMAIL_HOST = env('EMAIL_HOST', default='server')
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='user')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='password')
EMAIL_PORT = env('EMAIL_PORT', cast=int, default=587)
EMAIL_USE_TLS = env('EMAIL_USE_TLS', cast=bool, default=True)
EMAIL_USE_SSL = env('EMAIL_USE_SSL', cast=bool, default=False)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='address')

FONT_PATH = 'fonts/NotoSansJP-Regular.ttf'

MDEDITOR_CONFIGS = {
    'default': {
        'width': '90% ',
        'height': 600,
        'toolbar': ["undo", "redo", "|",
                    "bold", "del", "italic", "quote", "ucwords", "uppercase", "lowercase", "|",
                    "h1", "h2", "h3", "h5", "h6", "|",
                    "list-ul", "list-ol", "hr", "|",
                    "link", "reference-link", "code", "preformatted-text", "code-block", "table", "datetime",
                    "emoji", "html-entities", "pagebreak", "goto-line", "|",
                    "help", "info",
                    "||", "preview", "watch", "fullscreen"],
        'watch':False,
        'language': 'en'
    }
}

# MaterInfo settings
#
BRAND_NAME = env('BRAND_NAME', default='MaterInfo')

PROJECT_LOWER = [
    {
        'ListName': ('Sample', 'sample:list'),
        'Remote': 'sample.views.SampleRemote',
        'RemoteOrder': 2,
        'Search': 'sample.views.SearchView'
    },
    {
        'ListName': ('Prefix', 'project:prefix_list'),
        'Remote': 'project.views.prefix.PrefixRemote',
        'RemoteOrder': 1,
        'Search': 'project.views.prefix.PrefixSearch'
    },
    {
        'ListName': ('Plot', 'plot:list'),
        'Remote': 'plot.views.plot.PlotRemote',
        'RemoteOrder': 100,
        'Search': 'plot.views.plot.PlotSearch'
    },
    {
        'ListName': ('Album', 'album:list'),
        'Remote': 'album.views.album.AlbumRemote',
        'RemoteOrder': 101,
        'Search': 'album.views.album.AlbumSearch'
    },
    {
        'ListName': ('Collect', 'collect:list'),
        'Remote': 'collect.views.collect.CollectRemote',
        'RemoteOrder': 10,
        'Search': 'collect.views.collect.SearchView'
    },
    {
        'ListName': ('Comment', 'comment:list'),
        'Remote': 'comment.views.CommentRemote',
        'RemoteOrder': 11,
        'Search': 'comment.views.CommentSearch'
    },
    {
        'ListName': ('Reference', 'reference:list'),
        'Remote': 'reference.views.ReferenceRemote',
        'RemoteOrder': 12,
        'Search': 'reference.views.SearchView'
    },
    {
        'ListName': ('Document', 'document:list'),
        'Remote': 'document.views.DocumentRemote',
        'RemoteOrder': 13,
        'Search': 'document.views.SearchView'
    },
    {
        'ListName': ('Article', 'article:list'),
        'Remote': 'article.views.ArticleRemote',
        'RemoteOrder': 14,
        'Search': 'article.views.SearchView'
    },
    {
        'ListName': ('Repository', 'repository:list'),
        'RemoteOrder': 15,
    },
    {
        'ListName': ('Schedule', 'schedule:list'),
        'Remote': 'schedule.views.schedule.ScheduleRemote',
        'RemoteOrder': 16,
        'Search': 'schedule.views.schedule.ScheduleSearch'
    },
    {
        'ListName': ('Calendar', 'calendars:list'),
        'Remote': 'calendars.views.calendars.CalendarRemote',
        'RemoteOrder': 17,
        'Search': 'calendars.views.calendars.CalendarSearch'
    },
    {
        'ListName': ('Poll', 'poll:list'),
        'Remote': 'poll.views.poll.PollRemote',
        'RemoteOrder': 18,
        'Search': 'poll.views.poll.PollSearch'
    },
]

SAMPLE_LOWER = [
    {
        'ListName': ('General', 'general:list'),
        'Remote': 'general.views.GeneralRemote',
        'Search': 'general.views.GeneralSearch'
    },
    {
        'ListName': ('Material', 'material:list'),
        'Remote': 'material.views.material.MaterialRemote',
        'Search': 'material.views.material.MaterialSearch'
    },
    {
        'ListName': ('Density', 'density:list'),
        'Remote': 'density.views.DensityRemote',
        'Search': 'density.views.DensitySearch'
    },
    {
        'ListName': ('Hardness', 'hardness:list'),
        'Remote': 'hardness.views.hardness.HardnessRemote',
        'Search': 'hardness.views.hardness.HardnessSearch'
    },
    {
        'ListName': ('Value', 'value:list'),
        'Remote': 'value.views.value.ValueRemote',
        'Search': 'value.views.value.SearchView'
    },
    {
        'ListName': ('Image', 'image:list'),
        'Remote': 'image.views.image.ImageRemote',
        'Search': 'image.views.image.SearchView'
    },
]

IMAGE_LOWER = [
    {
        'ListName': ('Filter', 'image:filter_list'),
        'Remote': 'image.views.filter.FilterRemote',
        'Search': 'image.views.filter.FilterSearch'
    },
]

IMAGE_FILTER_PROCESS = [
    {
        'Model': 'image.models.process.Resize',
        'AddName': ('Resize', 'image:resize_add'),
        'Remote': 'image.views.process_api.ResizeRemote'
    },
    {
        'Model': 'image.models.process.Trim',
        'AddName': ('Trim', 'image:trim_add'),
        'Remote': 'image.views.process_api.TrimRemote'
    },
    {
        'Model': 'image.models.process.Smoothing',
        'AddName': ('Smoothing', 'image:smoothing_add'),
        'Remote': 'image.views.process_api.SmoothingRemote'
    },
    {
        'Model': 'image.models.process.Threshold',
        'AddName': ('Threshold', 'image:threshold_add'),
        'Remote': 'image.views.process_api.ThresholdRemote'
    },
    {
        'Model': 'image.models.process.Molphology',
        'AddName': ('Molphology', 'image:molphology_add'),
        'Remote': 'image.views.process_api.MolphologyRemote'
    },
    {
        'Model': 'image.models.process.DrawScale',
        'AddName': ('DrawScale', 'image:drawscale_add'),
        'Remote': 'image.views.process_api.DrawScaleRemote'
    },
    {
        'Model': 'image.models.process.Tone',
        'AddName': ('Tone', 'image:tone_add'),
        'Remote': 'image.views.process_api.ToneRemote'
    },
    {
        'Model': 'image.models.process.Transform',
        'AddName': ('Transform', 'image:transform_add'),
        'Remote': 'image.views.process_api.TransformRemote'
    },
]

IMAGE_FILTER_LOWER = [
    {
        'ListName': ('Size', 'image:size_list'),
        'Remote': 'image.views.size.SizeRemote',
        'Search': 'image.views.size.SizeSearch'
    },
    {
        'ListName': ('LN2D', 'image:ln2d_list'),
        'Remote': 'image.views.ln2d.LN2DRemote',
        'Search': 'image.views.ln2d.LN2DSearch'
    },
    {
        'ListName': ('IMFP', 'image:imfp_list'),
        'Remote': 'image.views.imfp.IMFPRemote',
        'Search': 'image.views.imfp.IMFPSearch'
    },
]

VALUE_LOWER = [
    {
        'ListName': ('Filter', 'value:filter_list'),
        'Remote': 'value.views.filter.FilterRemote',
        'Search': 'value.views.filter.FilterSearch'
    },
]

VALUE_FILTER_PROCESS = [
    {
        'Model': 'value.models.process.Select',
        'AddName': ('Select', 'value:select_add'),
        'Remote': 'value.views.process_api.SelectRemote'
    },
    {
        'Model': 'value.models.process.Trim',
        'AddName': ('Trim', 'value:trim_add'),
        'Remote': 'value.views.process_api.TrimRemote'
    },
    {
        'Model': 'value.models.process.Operate',
        'AddName': ('Operate', 'value:operate_add'),
        'Remote': 'value.views.process_api.OperateRemote'
    },
    {
        'Model': 'value.models.process.Rolling',
        'AddName': ('Rolling', 'value:rolling_add'),
        'Remote': 'value.views.process_api.RollingRemote'
    },
    {
        'Model': 'value.models.process.Reduce',
        'AddName': ('Reduce', 'value:reduce_add'),
        'Remote': 'value.views.process_api.ReduceRemote'
    },
    {
        'Model': 'value.models.process.Gradient',
        'AddName': ('Gradient', 'value:gradient_add'),
        'Remote': 'value.views.process_api.GradientRemote'
    },
    {
        'Model': 'value.models.process.Drop',
        'AddName': ('Drop', 'value:drop_add'),
        'Remote': 'value.views.process_api.DropRemote'
    },
    {
        'Model': 'value.models.process.Query',
        'AddName': ('Query', 'value:query_add'),
        'Remote': 'value.views.process_api.QueryRemote'
    },
    {
        'Model': 'value.models.process.Eval',
        'AddName': ('Eval', 'value:eval_add'),
        'Remote': 'value.views.process_api.EvalRemote'
    },
    {
        'Model': 'value.models.process.Beads',
        'AddName': ('Beads', 'value:beads_add'),
        'Remote': 'value.views.process_api.BeadsRemote'
    },
]

VALUE_FILTER_LOWER = [
    {
        'ListName': ('Aggregate', 'value:aggregate_list'),
        'Remote': 'value.views.aggregate.AggregateRemote',
        'Search': 'value.views.aggregate.AggregateSearch'
    },
    {
        'ListName': ('Curve', 'value:curve_list'),
        'Remote': 'value.views.curve.CurveRemote',
        'Search': 'value.views.curve.CurveSearch'
    },
]

VALUE_CURVE_EQUATION = [
    {
        'Model': 'value.models.equation.Constant',
        'AddName': ('Constant', 'value:constant_add'),
        'Remote': 'value.views.equation_api.ConstantRemote'
    },
    {
        'Model': 'value.models.equation.Gaussian',
        'AddName': ('Gaussian', 'value:gaussian_add'),
        'Remote': 'value.views.equation_api.GaussianRemote'
    },
    {
        'Model': 'value.models.equation.Linear',
        'AddName': ('Linear', 'value:linear_add'),
        'Remote': 'value.views.equation_api.LinearRemote'
    },
    {
        'Model': 'value.models.equation.Quadratic',
        'AddName': ('Quadratic', 'value:quadratic_add'),
        'Remote': 'value.views.equation_api.QuadraticRemote'
    },
    {
        'Model': 'value.models.equation.Polynomial',
        'AddName': ('Polynomial', 'value:polynomial_add'),
        'Remote': 'value.views.equation_api.PolynomialRemote'
    },
    {
        'Model': 'value.models.equation.Exponential',
        'AddName': ('Exponential', 'value:exponential_add'),
        'Remote': 'value.views.equation_api.ExponentialRemote'
    },
    {
        'Model': 'value.models.equation.PowerLaw',
        'AddName': ('PowerLaw', 'value:powerlaw_add'),
        'Remote': 'value.views.equation_api.PowerLawRemote'
    },
    {
        'Model': 'value.models.equation.Sine',
        'AddName': ('Sine', 'value:sine_add'),
        'Remote': 'value.views.equation_api.SineRemote'
    },
    {
        'Model': 'value.models.equation.Logistic',
        'AddName': ('Logistic', 'value:logistic_add'),
        'Remote': 'value.views.equation_api.LogisticRemote'
    },
    {
        'Model': 'value.models.equation.Expression',
        'AddName': ('Expression', 'value:expression_add'),
        'Remote': 'value.views.equation_api.ExpressionRemote'
    },
]

COLLECT_FEATURES = [
    {
        'Model': 'general.models.General',
        'Depth': 2
    },
    {
        'Model': 'material.models.Material',
        'Depth': 2
    },
    {
        'Model': 'density.models.Density',
        'Depth': 2
    },
    {
        'Model': 'hardness.models.Hardness',
        'Depth': 2
    },
    {
        'Model': 'value.models.aggregate.Aggregate',
        'Depth': 4
    },
    {
        'Model': 'value.models.curve.Curve',
        'Depth': 4
    },
    {
        'Model': 'image.models.size.Size',
        'Depth': 4
    },
    {
        'Model': 'image.models.ln2d.LN2D',
        'Depth': 4
    },
    {
        'Model': 'image.models.imfp.IMFP',
        'Depth': 4
    },
]

COLLECT_LOWER = [
    {
        'ListName': ('Filter', 'collect:filter_list'),
        'Remote': 'collect.views.filter.FilterRemote',
        'Search': 'collect.views.filter.FilterSearch'
    },
]

COLLECT_FILTER_PROCESS = [
    {
        'Model': 'collect.models.process.Fillna',
        'AddName': ('Fillna', 'collect:fillna_add'),
        'Remote': 'collect.views.process_api.FillnaRemote'
    },
    {
        'Model': 'collect.models.process.Dropna',
        'AddName': ('Dropna', 'collect:dropna_add'),
        'Remote': 'collect.views.process_api.DropnaRemote'
    },
    {
        'Model': 'collect.models.process.Drop',
        'AddName': ('Drop', 'collect:drop_add'),
        'Remote': 'collect.views.process_api.DropRemote'
    },
    {
        'Model': 'collect.models.process.Select',
        'AddName': ('Select', 'collect:select_add'),
        'Remote': 'collect.views.process_api.SelectRemote'
    },
    {
        'Model': 'collect.models.process.Agg',
        'AddName': ('Agg', 'collect:agg_add'),
        'Remote': 'collect.views.process_api.AggRemote'
    },
    {
        'Model': 'collect.models.process.Query',
        'AddName': ('Query', 'collect:query_add'),
        'Remote': 'collect.views.process_api.QueryRemote'
    },
    {
        'Model': 'collect.models.process.Exclude',
        'AddName': ('Exclude', 'collect:exclude_add'),
        'Remote': 'collect.views.process_api.ExcludeRemote'
    },
    {
        'Model': 'collect.models.process.PCAF',
        'AddName': ('PCAF', 'collect:pcaf_add'),
        'Remote': 'collect.views.process_api.PCAFRemote'
    },
]

COLLECT_FILTER_LOWER = [
    {
        'ListName': ('Correlation', 'collect:correlation_list'),
        'Remote': 'collect.views.correlation.CorrelationRemote',
        'Search': 'collect.views.correlation.CorrelationSearch'
    },
    {
        'ListName': ('Reduction', 'collect:reduction_list'),
        'Remote': 'collect.views.reduction.ReductionRemote',
        'Search': 'collect.views.reduction.ReductionSearch'
    },
    {
        'ListName': ('Clustering', 'collect:clustering_list'),
        'Remote': 'collect.views.clustering.ClusteringRemote',
        'Search': 'collect.views.clustering.ClusteringSearch'
    },
    {
        'ListName': ('Classification', 'collect:classification_list'),
        'Remote': 'collect.views.classification.ClassificationRemote',
        'Search': 'collect.views.classification.ClassificationSearch'
    },
    {
        'ListName': ('Regression', 'collect:regression_list'),
        'Remote': 'collect.views.regression.RegressionRemote',
        'Search': 'collect.views.regression.RegressionSearch'
    },
    {
        'ListName': ('Inverse', 'collect:inverse_list'),
        'Remote': 'collect.views.inverse.InverseRemote',
        'Search': 'collect.views.inverse.InverseSearch'
    },
]

FILE_ITEMS = [
    {
        'Model': 'album.models.album.Album',
        'FileName': 'album:file',
        'FileField': 'file'
    },
    {
        'Model': 'image.models.image.Image',
        'FileName': 'image:file',
        'FileField': 'file'
    },
    {
        'Model': 'image.models.filter.Filter',
        'FileName': 'image:filter_file',
        'FileField': 'file'
    },
    {
        'Model': 'value.models.filter.Filter',
        'FileName': 'value:filter_file',
        'FileField': 'file'
    },
    {
        'Model': 'image.models.size.Size',
        'FileName': 'image:size_file',
        'FileField': 'file'
    },
    {
        'Model': 'image.models.ln2d.LN2D',
        'FileName': 'image:ln2d_file',
        'FileField': 'file'
    },
    {
        'Model': 'image.models.imfp.IMFP',
        'FileName': 'image:imfp_file',
        'FileField': 'file'
    },
    {
        'Model': 'article.models.File',
        'FileName': 'article:file_file',
        'FileField': 'file'
    },
    {
        'Model': 'public.models.Public',
        'FileName': 'public:header_image',
        'FileField': 'header_image'
    },
]
