#!/usr/bin/env python
"""
Script to clear all messages and conversations from the database.
Run with: python manage.py runscript clear_chat_data
Or: python scripts/clear_chat_data.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings.development')
django.setup()

from apps.chat.models import Message, Conversation
from apps.emergency.models import CrisisFlag
from apps.openai_integration.models import APICallLog

def clear_all_chat_data():
    """Clear all chat-related data from the database"""
    
    print("=" * 50)
    print("CLEARING CHAT DATA")
    print("=" * 50)
    
    # Count before deletion
    messages_count = Message.objects.count()
    conversations_count = Conversation.objects.count()
    crisis_flags_count = CrisisFlag.objects.count()
    api_logs_count = APICallLog.objects.count()
    
    print(f"\n📊 BEFORE DELETION:")
    print(f"   Messages: {messages_count}")
    print(f"   Conversations: {conversations_count}")
    print(f"   Crisis Flags: {crisis_flags_count}")
    print(f"   API Call Logs: {api_logs_count}")
    
    # Confirm with user
    print("\n⚠️  WARNING: This will permanently delete all chat data!")
    confirm = input("Type 'yes' to confirm: ")
    
    if confirm.lower() != 'yes':
        print("❌ Operation cancelled.")
        return
    
    print("\n🗑️  Deleting data...")
    
    # Delete in correct order (respecting foreign keys)
    try:
        # Delete messages first (they reference conversations)
        messages_deleted = Message.objects.all().delete()
        print(f"   ✅ Deleted {messages_deleted[0]} messages")
        
        # Delete crisis flags (they reference messages)
        crisis_deleted = CrisisFlag.objects.all().delete()
        print(f"   ✅ Deleted {crisis_deleted[0]} crisis flags")
        
        # Delete API logs (they reference messages/conversations)
        logs_deleted = APICallLog.objects.all().delete()
        print(f"   ✅ Deleted {logs_deleted[0]} API logs")
        
        # Finally delete conversations
        conversations_deleted = Conversation.objects.all().delete()
        print(f"   ✅ Deleted {conversations_deleted[0]} conversations")
        
        print("\n✅ All chat data cleared successfully!")
        
    except Exception as e:
        print(f"\n❌ Error during deletion: {e}")
        return
    
    # Verify deletion
    print("\n📊 AFTER DELETION:")
    print(f"   Messages: {Message.objects.count()}")
    print(f"   Conversations: {Conversation.objects.count()}")
    print(f"   Crisis Flags: {CrisisFlag.objects.count()}")
    print(f"   API Call Logs: {APICallLog.objects.count()}")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    clear_all_chat_data()