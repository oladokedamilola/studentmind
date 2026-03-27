from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('apps.accounts.urls')),  # API endpoints
    path('api/chat/', include('apps.chat.urls')),
    path('api/emergency/', include('apps.emergency.urls')),
    path('api/resources/', include('apps.resources.urls')),
    path('api/university/', include('apps.university.urls')),
    path('api/mood/', include('apps.mood.urls')),
    
    path('', include('apps.pages.urls')),  # Frontend pages
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)