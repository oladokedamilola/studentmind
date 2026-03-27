from django.urls import path
from . import views

app_name = 'mood'

urlpatterns = [
    path('save/', views.save_mood, name='save_mood'),
    path('today/', views.get_today_mood, name='today_mood'),
    path('history/', views.get_mood_history, name='mood_history'),
]