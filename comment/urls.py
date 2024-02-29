from django.urls import path
from . import views

app_name = 'comment'
urlpatterns = [
    path('<int:pk>/add', views.AddView.as_view(), name='add'),
    path('<int:pk>/list', views.ListView.as_view(), name='list'),
    path('comment/<int:pk>', views.DetailView.as_view(), name='detail'),
    path('comment/<int:pk>/file', views.FileView.as_view(), name='file'),
    path('comment/<int:pk>/response', views.ResponseView.as_view(), name='response'),
    path('response/<int:pk>/file', views.ResponseFileView.as_view(), name='response_file'),
    # API
    path('api/<int:pk>/add', views.AddAPIView.as_view(), name='api_add'),
    path('api/<int:pk>/list', views.ListAPIView.as_view(), name='api_list'),
    path('api/comment/<int:pk>', views.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/comment/<int:pk>/file', views.FileAPIView.as_view(), name='api_file'),
    path('api/comment/<int:pk>/response/add', views.ResponseAddAPIView.as_view(), name='api_response_add'),
    path('api/comment/<int:pk>/response/list', views.ResponseListAPIView.as_view(), name='api_response_list'),
    path('api/response/<int:pk>', views.ResponseRetrieveAPIView.as_view(), name='api_response_retrieve'),
    path('api/response/<int:pk>/file', views.ResponseFileAPIView.as_view(), name='api_response_file'),
]
