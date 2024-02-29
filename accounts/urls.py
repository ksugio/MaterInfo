from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('password_change/', views.PasswordChangeView.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDoneView.as_view(), name='password_change_done'),
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),
    path('profile', views.ProfileView.as_view(), name='profile'),
    path('profile_update', views.ProfileUpdateView.as_view(), name='profile_update'),
    path('token', views.TokenView.as_view(), name='token'),
    path('user/add/', views.UserAddView.as_view(), name='user_add'),
    path('user/list/', views.UserListView.as_view(), name='user_list'),
    path('user/<int:pk>/update', views.UserUpdateView.as_view(), name='user_update'),
    path('user/<int:pk>/delete', views.UserDeleteView.as_view(), name='user_delete'),
    path('user/upload/', views.UserUploadView.as_view(), name='user_upload'),
    path('user/download/', views.UserDownloadView.as_view(), name='user_download'),
    #path('user/clone/', views.UserCloneView.as_view(), name='user_clone'),
    # API
    #path('api/user/list', views.ListAPIView.as_view(), name='api_user_list'),
    #path('api/user/<int:pk>', views.RetrieveAPIView.as_view(), name='api_user_retrieve'),
]
