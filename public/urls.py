from django.urls import path
from .views import public, article, menu, file

app_name = 'public'
urlpatterns = [
    path('add', public.AddView.as_view(), name='add'),
    path('list', public.ListView.as_view(), name='list'),
    path('public/<int:pk>', public.DetailView.as_view(), name='detail'),
    path('public/<int:pk>/update', public.UpdateView.as_view(), name='update'),
    path('public/<int:pk>/release', public.ReleaseView.as_view(), name='release'),
    path('public/<int:pk>/delete', public.DeleteView.as_view(), name='delete'),
    path('public/<int:pk>/header_image', public.HeaderImageView.as_view(), name='header_image'),
    path('home/<str:path>', public.HomeView.as_view(), name='home'),
    # API
    path('api/add', public.AddAPIView.as_view(), name='api_add'),
    path('api/list', public.ListAPIView.as_view(), name='api_list'),
    path('api/<int:pk>', public.RetrieveAPIView.as_view(), name='api_retrieve'),
    path('api/<int:pk>/update', public.UpdateAPIView.as_view(), name='api_update'),
    path('api/<int:pk>/delete', public.DeleteAPIView.as_view(), name='api_delete'),
    # Article
    path('public/<int:pk>/article/add', article.AddView.as_view(), name='article_add'),
    path('public/<int:pk>/article/list', article.ListView.as_view(), name='article_list'),
    path('article/<int:pk>', article.DetailView.as_view(), name='article_detail'),
    path('article/<int:pk>/update', article.UpdateView.as_view(), name='article_update'),
    path('article/<int:pk>/delete', article.DeleteView.as_view(), name='article_delete'),
    path('article/home/<int:pk>', article.HomeView.as_view(), name='article_home'),
    # Article API
    path('api/public/<int:pk>/article/add', article.AddAPIView.as_view(), name='api_article_add'),
    path('api/public/<int:pk>/article/list', article.ListAPIView.as_view(), name='api_article_list'),
    path('api/article/<int:pk>', article.RetrieveAPIView.as_view(), name='api_article_retrieve'),
    path('api/article/<int:pk>/update', article.UpdateAPIView.as_view(), name='api_article_update'),
    path('api/article/<int:pk>/delete', article.DeleteAPIView.as_view(), name='api_article_delete'),
    # Menu
    path('public/<int:pk>/menu/add', menu.AddView.as_view(), name='menu_add'),
    path('public/<int:pk>/menu/list', menu.ListView.as_view(), name='menu_list'),
    path('menu/<int:pk>/update', menu.UpdateView.as_view(), name='menu_update'),
    path('menu/<int:pk>/delete', menu.DeleteView.as_view(), name='menu_delete'),
    # Menu API
    path('api/public/<int:pk>/menu/add', menu.AddAPIView.as_view(), name='api_menu_add'),
    path('api/public/<int:pk>/menu/list', menu.ListAPIView.as_view(), name='api_menu_list'),
    path('api/menu/<int:pk>', menu.RetrieveAPIView.as_view(), name='api_menu_retrieve'),
    path('api/menu/<int:pk>/update', menu.UpdateAPIView.as_view(), name='api_menu_update'),
    path('api/menu/<int:pk>/delete', menu.DeleteAPIView.as_view(), name='api_menu_delete'),
    # File
    path('public/<int:pk>/file/add', file.AddView.as_view(), name='file_add'),
    path('public/<int:pk>/file/list', file.ListView.as_view(), name='file_list'),
    path('file/<int:pk>/update', file.UpdateView.as_view(), name='file_update'),
    path('file/<int:pk>/delete', file.DeleteView.as_view(), name='file_delete'),
    path('file/<str:key>', file.FileView.as_view(), name='file'),
    # File API
    path('api/public/<int:pk>/file/add', file.AddAPIView.as_view(), name='api_file_add'),
    path('api/public/<int:pk>/file/list', file.ListAPIView.as_view(), name='api_file_list'),
    path('api/file/<int:pk>', file.RetrieveAPIView.as_view(), name='api_file_retrieve'),
    path('api/file/<int:pk>/update', file.UpdateAPIView.as_view(), name='api_file_update'),
    path('api/file/<int:pk>/delete', file.DeleteAPIView.as_view(), name='api_file_delete'),
]
