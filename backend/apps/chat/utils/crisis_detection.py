"""
Crisis detection utilities for identifying high-risk messages
"""
import re
import json
from textblob import TextBlob  

# Crisis keywords categorized by severity
CRISIS_KEYWORDS = {
    'self_harm': [
        'kill myself', 'end my life', 'commit suicide', 'take my life',
        'hurt myself', 'self-harm', 'cut myself', 'suicide'
    ],
    'severe_distress': [
        'can\'t go on', 'no reason to live', 'want to die',
        'better off dead', 'give up', 'hopeless'
    ],
    'moderate_distress': [
        'overwhelmed', 'can\'t cope', 'falling apart', 'breaking down',
        'losing control', 'desperate'
    ],
    'anxiety': [
        'panic attack', 'can\'t breathe', 'heart racing', 'terrified',
        'scared to death', 'anxiety attack'
    ]
}

# Severity mapping
KEYWORD_SEVERITY = {
    'self_harm': 4,      # Critical
    'severe_distress': 3, # High
    'moderate_distress': 2, # Medium
    'anxiety': 1          # Low
}

def detect_crisis_keywords(text):
    """
    Detect crisis keywords in text
    Returns: (detected_category, matched_keywords, severity)
    """
    text_lower = text.lower()
    detected = []
    highest_severity = 0
    matched_all = []
    
    for category, keywords in CRISIS_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                detected.append({
                    'category': category,
                    'keyword': keyword,
                    'severity': KEYWORD_SEVERITY.get(category, 1)
                })
                matched_all.append(keyword)
                if KEYWORD_SEVERITY.get(category, 1) > highest_severity:
                    highest_severity = KEYWORD_SEVERITY.get(category, 1)
    
    return detected, matched_all, highest_severity

def analyze_sentiment(text):
    """
    Analyze sentiment of text
    Returns: polarity (-1 to 1), subjectivity (0 to 1)
    """
    blob = TextBlob(text)
    return blob.sentiment.polarity, blob.sentiment.subjectivity

def calculate_priority(text):
    """
    Calculate message priority based on content
    Returns: priority (0=normal, 1=urgent, 2=crisis)
    """
    # Check for crisis keywords
    detected, matched, severity = detect_crisis_keywords(text)
    
    if severity >= 4:
        return 2  # Crisis
    
    if severity >= 2:
        return 1  # Urgent
    
    # Check sentiment for very negative messages
    polarity, _ = analyze_sentiment(text)
    if polarity < -0.7:
        return 1  # Urgent - very negative sentiment
    
    if polarity < -0.4:
        # Check message length and urgency indicators
        urgent_indicators = ['urgent', 'asap', 'immediately', 'emergency', 'help now']
        if any(indicator in text.lower() for indicator in urgent_indicators):
            return 1  # Urgent
    
    return 0  # Normal

def get_emergency_response(priority_level):
    """
    Get appropriate emergency response based on priority
    """
    responses = {
        2: {
            'message': "I'm very concerned about what you're sharing. Your safety is the most important thing. Please reach out for immediate support:",
            'resources': [
                {"name": "Emergency Services", "contact": "911 or local emergency number"},
                {"name": "Suicide Prevention Lifeline", "contact": "1-800-273-8255"},
                {"name": "Crisis Text Line", "contact": "Text HOME to 741741"}
            ],
            'action': 'immediate_escalation'
        },
        1: {
            'message': "I can hear that you're going through a difficult time. While I'm here to support you, please also consider reaching out to these resources:",
            'resources': [
                {"name": "Campus Counseling Center", "contact": "Schedule an appointment"},
                {"name": "24/7 Crisis Hotline", "contact": "1-800-273-8255"}
            ],
            'action': 'suggest_resources'
        }
    }
    return responses.get(priority_level, None)