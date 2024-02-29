"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path, reverse_lazy
from django.views.generic import RedirectView
from django.contrib.staticfiles.urls import static
from . import settings

IndexUrl = reverse_lazy(settings.INDEX_URL[0], kwargs=settings.INDEX_URL[1])

urlpatterns = [
    path('mi7398527/', admin.site.urls),
    path('', RedirectView.as_view(url=IndexUrl), name='index'),
    path('api/auth/', include('djoser.urls.jwt')),
    path('mdeditor/', include('mdeditor.urls')),
    path('accounts/', include('accounts.urls')),
    path('project/', include('project.urls')),
    path('sample/', include('sample.urls')),
    path('comment/', include('comment.urls')),
    path('reference/', include('reference.urls')),
    path('document/', include('document.urls')),
    path('schedule/', include('schedule.urls')),
    path('poll/', include('poll.urls')),
    path('image/', include('image.urls')),
    path('value/', include('value.urls')),
    path('material/', include('material.urls')),
    path('density/', include('density.urls')),
    path('hardness/', include('hardness.urls')),
    path('plot/', include('plot.urls')),
    path('album/', include('album.urls')),
    path('article/', include('article.urls')),
    path('public/', include('public.urls')),
    path('calendars/', include('calendars.urls')),
    path('collect/', include('collect.urls')),
    path('general/', include('general.urls')),
    path('repository/', include('repository.urls')),
]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
