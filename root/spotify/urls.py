from django.urls import path,include
from . import views
from django.conf import settings
# from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
# from django.contrib.auth import logout


urlpatterns = [
    # path('', views.register, name='register'),
    path('', views.spotify_login, name='spotify_login'),
    path('spotify/callback/', views.spotify_callback, name='spotify_callback'),
    path('user/', views.user_info, name='user_info'),
    path('error/', views.error, name='error'),  # Optional error handling
]
    
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    