from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.views.static import serve

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/emergency/', include('apps.emergency.urls')),
    path('api/resources/', include('apps.resources.urls')),
    path('api/university/', include('apps.university.urls')),
    path('api/mood/', include('apps.mood.urls')),
    
    # PWA Routes - serve from frontend folder
    path('manifest.json', serve, {
        'document_root': settings.BASE_DIR / 'frontend',
        'path': 'manifest.json'
    }),
    path('service-worker.js', serve, {
        'document_root': settings.BASE_DIR / 'frontend',
        'path': 'service-worker.js'
    }),
    path('offline/', TemplateView.as_view(template_name='pages/offline.html'), name='offline'),
    
    path('', include('apps.pages.urls')),  # Frontend pages
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)