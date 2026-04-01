from django.contrib import admin
from django.urls import include, path

from blog import views as blog_views

handler404 = 'pages.views.page_not_found'
handler500 = 'pages.views.server_error'
handler403 = 'pages.views.csrf_failure'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/registration/', blog_views.registration, name='registration'),
    path('auth/', include('django.contrib.auth.urls')),
    path('pages/', include('pages.urls', namespace='pages')),
    path('', include('blog.urls', namespace='blog')),
]
