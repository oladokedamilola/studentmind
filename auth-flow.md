┌─────────────────┐
│  Enter Matric   │  → POST /api/accounts/api/verify-matric/
└─────────────────┘
         ↓
┌─────────────────┐
│  Show Student   │  → Display student details for confirmation
│  Confirmation   │
└─────────────────┘
         ↓
┌─────────────────┐
│  User Confirms  │  → Click "Yes, Continue"
└─────────────────┘
         ↓
┌─────────────────┐
│  Generate Token │  → Create registration token
│  Send Email     │  → Send registration link to student email
└─────────────────┘
         ↓
┌─────────────────┐
│  Check Email    │  → User clicks link in email
└─────────────────┘
         ↓
┌─────────────────┐
│  Create Password│  → Set password
└─────────────────┘
         ↓
┌─────────────────┐
│  AUTO LOGIN     │  → User is automatically logged in
└─────────────────┘
         ↓
┌─────────────────┐
│  DASHBOARD      │  → Redirected to dashboard
└─────────────────┘