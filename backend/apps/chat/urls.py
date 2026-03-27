from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Message endpoints
    path('send/', views.send_message, name='send-message'),
    path('regenerate/', views.regenerate_response, name='regenerate-response'),
    path('edit-resend/', views.edit_and_resend, name='edit-resend'),
    path('stop-generation/', views.stop_generation, name='stop-generation'),
    
    # Conversation endpoints
    path('conversations/', views.get_conversations, name='conversations'),
    path('conversations/<int:conversation_id>/', views.get_conversation_detail, name='conversation-detail'),
    path('conversations/<int:conversation_id>/close/', views.close_conversation, name='close-conversation'),
    path('conversations/<int:conversation_id>/mark-read/', views.mark_read, name='mark-read'),
]