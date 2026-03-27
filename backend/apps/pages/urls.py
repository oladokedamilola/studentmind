from django.urls import path, include
from . import views
from apps.accounts.views import register_confirm  # Import the view

app_name = 'pages'

urlpatterns = [
    # ======================
    # PUBLIC PAGES
    # ======================
    path('', views.landing, name='landing'),
    path('about/', views.about, name='about'),
    path('privacy/', views.privacy, name='privacy'),
    path('terms/', views.terms, name='terms'),
    path('contact/', views.contact, name='contact'),
    
    # Authentication Flow
    path('verify/', views.matric_verification, name='matric_verification'),
    path('confirm/', views.student_confirmation, name='student_confirmation'),
    path('create-password/', views.create_password, name='create_password'),
    path('login/', views.login_page, name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password-confirm/', views.reset_password_confirm_page, name='reset_password_confirm_page'),
    path('email-verification-sent/', views.email_verification_sent, name='email_verification_sent'),
    path('resend-verification/', views.resend_verification_page, name='resend_verification_page'),
    
    # Registration confirmation from email - ADD THIS LINE
    path('register/<str:matric_number>/<str:token>/', register_confirm, name='register_confirm'),
    
    # ======================
    # PROTECTED PAGES (Dashboard)
    # ======================
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # ======================
    # CHAT PAGES
    # ======================
    path('chat/', views.chat_list, name='chat_list'),
    path('chat/new/', views.chat_new, name='chat_new'),
    path('chat/<int:conversation_id>/', views.chat_detail, name='chat_detail'),
    path('chat/search/', views.chat_search, name='chat_search'),
    
    # ======================
    # MOOD TRACKING PAGES
    # ======================
    path('mood/log/', views.mood_log, name='mood_log'),
    path('mood/history/', views.mood_history, name='mood_history'),
    path('mood/calendar/', views.mood_calendar, name='mood_calendar'),
    
    # ======================
    # RESOURCES PAGES
    # ======================
    path('resources/', views.resources_list, name='resources_list'),
    path('resources/<int:resource_id>/', views.resource_detail, name='resource_detail'),
    path('resources/saved/', views.resources_saved, name='resources_saved'),
    path('resources/search/', views.resources_search, name='resources_search'),
    
    # ======================
    # ASSESSMENTS PAGES
    # ======================
    path('assessments/', views.assessments_list, name='assessments_list'),
    path('assessments/take/<int:assessment_id>/', views.assessment_take, name='assessment_take'),
    path('assessments/results/<int:result_id>/', views.assessment_results, name='assessment_results'),
    path('assessments/history/', views.assessment_history, name='assessment_history'),
    path('assessments/compare/', views.assessment_compare, name='assessment_compare'),
    
    # ======================
    # ACCOUNT MANAGEMENT PAGES
    # ======================
    path('settings/', views.settings, name='settings'),
    path('change-password/', views.change_password, name='change_password'),
    path('notification-preferences/', views.notification_preferences, name='notification_preferences'),
    path('delete-account/', views.delete_account, name='delete_account'),
    
    
    # ======================
    # SUPPORT PAGES
    # ======================
    path('crisis-support/', views.crisis_support, name='crisis_support'),
    path('find-counselor/', views.find_counselor, name='find_counselor'),
    path('support-groups/', views.support_groups, name='support_groups'),
    path('help-faqs/', views.help_faqs, name='help_faqs'),
    
    # ======================
    # API ROUTES (from other apps)
    # ======================
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/chat/', include('apps.chat.urls')),
    path('api/resources/', include('apps.resources.urls')),
    path('api/emergency/', include('apps.emergency.urls')),
    path('api/university/', include('apps.university.urls')),
    path('api/mood/', include('apps.mood.urls')),
    path('api/assessments/', include('apps.assessment.urls')),
]

# ======================
# ERROR HANDLERS
# ======================
handler404 = 'apps.pages.views.custom_404'
handler500 = 'apps.pages.views.custom_500'