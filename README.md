# MindHaven - Mental Health Support PWA for University Students

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Django](https://img.shields.io/badge/Django-4.2-green)](https://www.djangoproject.com/)
[![PWA](https://img.shields.io/badge/PWA-Ready-blue)](https://web.dev/progressive-web-apps/)
[![Deployed on PythonAnywhere](https://img.shields.io/badge/Deployed-PythonAnywhere-blueviolet)](https://www.pythonanywhere.com/)

---

## 📌 Overview

**MindHaven** is a compassionate mental health support platform designed specifically for university students. It provides a safe, private, and accessible space where students can talk about their feelings, track their emotional well-being, and access coping resources—anytime, anywhere.

The platform combines the power of AI-driven conversations with evidence-based mental health tools, creating a supportive sanctuary that students can turn to during stressful academic periods, personal challenges, or simply when they need someone to talk to.

---

## 🎯 Key Features

### 🤖 AI-Powered Chat Support
- **24/7 Availability** – Instant support whenever you need it, day or night
- **Anonymous Conversations** – Talk freely without fear of judgment
- **Real-time Typing Effect** – Natural, human-like interaction
- **Crisis Detection** – Automatic identification of distress signals with immediate resource escalation
- **Conversation History** – Review past chats to track your journey

### 📊 Mood Tracking
- **Daily Check-ins** – Quick emoji-based mood logging
- **Visual Trends** – Charts and graphs to see your emotional patterns over time
- **Calendar View** – Visual overview of your monthly mood
- **Personal Insights** – Discover patterns about your emotional well-being
- **Journal Notes** – Add context to your moods with private notes

### 📚 Resource Library
- **Curated Coping Strategies** – Articles, exercises, and techniques for managing stress, anxiety, and more
- **Breathing Exercises** – Guided relaxation techniques
- **Personalized Recommendations** – Resources tailored to your needs based on mood patterns
- **Save for Later** – Bookmark helpful resources for easy access

### 📋 Mental Health Assessments
- **PHQ-9 Depression Scale** – Standardized screening for depression
- **GAD-7 Anxiety Scale** – Assessment for generalized anxiety
- **Perceived Stress Scale** – Evaluate your stress levels
- **Progress Tracking** – Compare results over time to see improvement
- **Results History** – Track your mental health journey

### 🔐 Secure & Private
- **Email Verification** – Secure registration with university email
- **Encrypted Conversations** – All chats are encrypted for privacy
- **Session Management** – Secure login with automatic timeout
- **Data Protection** – Your information stays yours

### 📱 Progressive Web App
- **Install on Device** – Add to home screen like a native app
- **Offline Support** – Access saved resources and conversations without internet
- **Push Notifications** – Gentle reminders for check-ins and new resources
- **Fast & Responsive** – Works seamlessly on any device

---

## ✨ Benefits for Students

| Benefit | Description |
|---------|-------------|
| **Immediate Support** | No waiting lists or appointments—help is always available |
| **Zero Stigma** | Anonymous conversations eliminate fear of judgment |
| **Academic Balance** | Tools to manage stress and anxiety during exams and deadlines |
| **Self-Awareness** | Track mood patterns and identify triggers |
| **Practical Skills** | Learn evidence-based coping strategies |
| **Completely Free** | Accessible to all students at no cost |

---

## 🛠️ Technology Stack

### Backend
- **Django 4.2** – Python web framework for robust backend development
- **Django REST Framework** – API development and serialization
- **Celery** – Asynchronous task processing
- **Redis** – Caching and message broker

### Frontend
- **HTML5 / CSS3** – Semantic markup and responsive styling
- **Bootstrap 5** – Responsive UI components
- **JavaScript** – Dynamic interactions and API communication
- **Chart.js** – Data visualization for mood tracking

### AI & Machine Learning
- **GitHub Models (Azure AI Inference)** – AI-powered chat responses
- **Natural Language Processing** – Sentiment analysis and crisis detection
- **Content-Based Recommendations** – Personalized resource suggestions

### Database & Storage
- **SQLite** – Development database
- **MySQL** – Production database (PythonAnywhere)

### Deployment
- **PythonAnywhere** – Cloud hosting platform
- **Whitenoise** – Static file serving
- **Gunicorn** – WSGI server

---

## 🚀 System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Django        │────▶│   Database      │
│   (PWA)         │     │   Backend       │     │   (MySQL)       │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                │
                                ▼
                        ┌─────────────────┐
                        │   GitHub Models │
                        │   (AI Engine)   │
                        └─────────────────┘
```

---

## 📁 Project Structure

```
StudentMind/
├── backend/                 # Django project
│   ├── apps/               # Django applications
│   │   ├── accounts/       # Authentication & user management
│   │   ├── chat/           # Chat functionality
│   │   ├── mood/           # Mood tracking
│   │   ├── resources/      # Resource library
│   │   ├── assessments/    # Mental health assessments
│   │   ├── emergency/      # Crisis detection
│   │   └── university/     # Student data management
│   └── settings/           # Environment-specific settings
├── frontend/               # Frontend assets
│   ├── templates/          # HTML templates
│   ├── css/               # Stylesheets
│   ├── js/                # JavaScript modules
│   └── images/            # Images and icons
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

---

## 🔒 Security & Privacy

- **Encrypted Messages** – All chat content is encrypted at rest
- **Session Security** – Secure cookie-based authentication with automatic expiry
- **CSRF Protection** – Built-in Django CSRF protection
- **HTTPS Enforcement** – All connections are encrypted in production
- **Data Minimization** – Only essential data is collected
- **Anonymized Analytics** – Usage data is anonymized for insights

---

## 📊 Key Features in Detail

### 💬 AI Chat Assistant
The AI chat assistant is designed to provide empathetic, non-judgmental support. It follows evidence-based guidelines:
- Warm and validating responses
- Never provides medical diagnosis
- Suggests coping strategies when appropriate
- Escalates to crisis resources when needed
- Maintains appropriate boundaries

### 📈 Mood Tracking
Track your emotional well-being with:
- Daily mood check-ins (1-5 scale with emoji visualization)
- Historical trends and patterns
- Calendar view of your mood journey
- Insights about your emotional patterns
- Optional journal notes for context

### 📚 Resource Library
Access a curated collection of:
- Breathing exercises and relaxation techniques
- Articles on stress management
- Coping strategies for anxiety and depression
- Study-life balance tips
- Self-care practices

### 📋 Mental Health Assessments
Evidence-based screening tools:
- **PHQ-9** – 9-question depression screening
- **GAD-7** – 7-question anxiety screening
- **PSS** – Perceived Stress Scale
- Results tracking over time
- Educational interpretation of scores

---

## 🌟 Why MindHaven?

| Challenge | MindHaven Solution |
|-----------|-------------------|
| **Long counseling wait times** | Immediate, 24/7 AI support |
| **Stigma around seeking help** | Anonymous conversations |
| **Cost barriers** | Completely free |
| **Limited awareness** | Educational resources and self-assessment tools |
| **No time for appointments** | Available on your schedule |
| **Difficulty tracking progress** | Visual mood history and assessment tracking |

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## ⚠️ Disclaimer

MindHaven is not a substitute for professional mental health care. It is designed to provide supportive resources and a safe space to talk, but it cannot replace professional medical advice, diagnosis, or treatment.

**In case of emergency, please contact:**
- **Emergency Services:** 911 or your local emergency number
- **Suicide Prevention Lifeline:** 1-800-273-8255
- **Crisis Text Line:** Text HOME to 741741

---

## 🙏 Acknowledgments

- **OpenAI / GitHub Models** – For providing the AI capabilities
- **PythonAnywhere** – For reliable hosting infrastructure
- **All Contributors** – For their dedication to student mental health
- **The Student Community** – For inspiring this project

---


*Made with 💚 for student mental health*