# RedConnect - Blood Donation & Emergency Management System

A comprehensive, role-based blood donation platform that connects donors, hospitals, camps, and patients in a unified network for efficient blood management and emergency response.

## 🩸 System Overview

RedConnect is designed to handle real-world blood donation workflows with medical safety, emergency management, and role-based access control. The system supports:

- **Donors**: Registration, camp applications, hospital alerts, donation tracking
- **Hospitals**: Blood stock management, patient requests, emergency alerts, inter-hospital exchange
- **Camps**: Blood camp organization, donor management, attendance tracking
- **Patients**: Blood requests with emergency classification
- **Admins**: System oversight, verification, emergency management

## 🏗️ Architecture

### Backend (Django + DRF)
- **Framework**: Django 4.2 with Django REST Framework
- **Authentication**: JWT-based with role-based permissions
- **Database**: SQLite (development) / PostgreSQL (production)
- **API**: RESTful APIs with comprehensive validation

### Frontend (Vanilla JavaScript)
- **Technology**: HTML5, CSS3, Vanilla JavaScript
- **Design**: Modern, responsive UI with accessibility compliance
- **Architecture**: Modular JavaScript with authentication management

## 📁 Project Structure

```
BloodSystem/
├── frontend/                    # Complete frontend separation
│   ├── html/                   # All HTML templates
│   │   ├── index.html          # Landing page
│   │   └── auth/               # Authentication pages
│   ├── css/                    # Styling
│   │   ├── global.css          # Global styles
│   │   ├── landing.css         # Landing page styles
│   │   └── auth.css            # Authentication styles
│   ├── js/                     # JavaScript modules
│   │   ├── landing.js          # Landing page logic
│   │   ├── auth.js             # Authentication utilities
│   │   └── donor-register.js   # Donor registration
│   └── assets/                 # Images, icons, etc.
└── backend/                    # Django backend
    ├── manage.py
    ├── bloodsystem/            # Main project
    ├── accounts/               # Authentication & User Management
    ├── donor/                  # Donor module
    ├── hospital/               # Hospital module
    ├── camp/                   # Camp module
    ├── patient/                # Patient module
    ├── adminpanel/             # Admin module
    └── notifications/          # Notification system
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd BloodSystem/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start development server**
   ```bash
   python manage.py runserver
   ```

   Backend will be available at: `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd ../frontend
   ```

2. **Serve frontend files**
   
   **Option 1: Python HTTP Server**
   ```bash
   python -m http.server 3000
   ```
   
   **Option 2: Node.js HTTP Server**
   ```bash
   npx http-server -p 3000
   ```
   
   **Option 3: Live Server (VS Code Extension)**
   - Install Live Server extension
   - Right-click on `index.html` → "Open with Live Server"

   Frontend will be available at: `http://localhost:3000`

## 🔐 User Roles & Access

### Landing Page Flow
- **Single Entry Point**: Clean landing page with role-based registration
- **No Login Button**: Login accessible only through registration pages
- **4 Registration Types**: Donor, Hospital, Camp, Patient

### Authentication Flow
```
Registration → Email Verification → Auto-Login → JWT Token → Role Dashboard
```

### Role-Based Dashboards
- **Donor Dashboard**: Camp suggestions, hospital alerts, donation history
- **Hospital Dashboard**: Patient requests, blood stock, emergency panel
- **Camp Dashboard**: Camp management, donor applications, attendance
- **Patient Dashboard**: Blood requests with emergency options
- **Admin Dashboard**: System verification and monitoring

## 🩺 Medical Safety Features

### Donor Eligibility Rules
- **Age**: 18-65 years
- **Weight**: Minimum 50 kg
- **Donation Gap**: 56 days minimum between donations
- **Health Screening**: Medical conditions and medication checks

### Blood Compatibility
- Full compatibility matrix implementation
- Safe blood type matching
- Cross-matching validation

### Emergency Classification
- **Normal**: Standard blood requests
- **Emergency**: Critical patient needs
- **Disaster**: Mass casualty events

## 🚨 Emergency Management

### Alert Levels
1. **Low Priority**: City-level donors, single hospital
2. **Emergency**: State-level donors, multiple hospitals
3. **Disaster**: National alert, all hospitals activated

### Emergency Validation
- Reason justification required (50+ characters)
- Hospital verification mandatory
- Admin review for all emergency requests
- Abuse prevention through pattern tracking

## 🏥 Hospital Network Features

### Blood Exchange System
- Inter-hospital blood sharing
- Automated matching based on availability
- Transportation coordination
- Quality assurance protocols

### Stock Management
- Real-time inventory tracking
- Expiry date management
- Automatic stock updates
- Low stock alerts

## 📱 API Endpoints

### Authentication
```
POST /api/auth/register/donor/
POST /api/auth/register/hospital/
POST /api/auth/register/camp/
POST /api/auth/register/patient/
POST /api/auth/login/
POST /api/auth/logout/
GET  /api/auth/profile/
```

### Role-Specific APIs
```
# Donor APIs
GET  /api/donor/dashboard/
GET  /api/donor/camps/suggestions/
POST /api/donor/camps/apply/

# Hospital APIs
GET  /api/hospital/dashboard/
POST /api/hospital/blood-requests/
GET  /api/hospital/blood-stock/

# Patient APIs
GET  /api/patient/dashboard/
POST /api/patient/blood-request/

# Admin APIs
GET  /api/admin/dashboard/
POST /api/admin/verify-hospital/
```

## 🔧 Configuration

### Environment Variables
Create `.env` file in backend directory:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

### CORS Settings
Frontend and backend are configured for cross-origin requests during development.

## 🧪 Testing

### Backend Testing
```bash
cd backend
python manage.py test
```

### Frontend Testing
- Manual testing through browser
- API testing with tools like Postman
- Form validation testing

## 🚀 Deployment

### Backend Deployment (Heroku/Railway)
1. Configure production settings
2. Set environment variables
3. Configure PostgreSQL database
4. Deploy with gunicorn

### Frontend Deployment (Netlify/Vercel)
1. Build static files
2. Configure API endpoints
3. Deploy frontend assets

## 🔒 Security Features

- JWT authentication with refresh tokens
- Role-based access control
- Input validation and sanitization
- CORS protection
- Password strength requirements
- Medical data protection

## 📊 Database Schema

### Core Models
- **User**: Base authentication with roles
- **DonorProfile**: Medical information, donation history
- **HospitalProfile**: Verification, blood bank details
- **CampProfile**: Organization details, verification
- **PatientProfile**: Basic information, emergency contacts

### Operational Models
- **BloodStock**: Hospital inventory management
- **BloodRequest**: Patient blood requests
- **Camp**: Blood donation events
- **Notification**: System-wide notifications
- **AuditLog**: System activity tracking

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

## 🎯 Roadmap

- [ ] SMS notifications
- [ ] Mobile app development
- [ ] Advanced analytics dashboard
- [ ] Integration with hospital management systems
- [ ] Multi-language support
- [ ] Advanced reporting features

---

**RedConnect** - Connecting lives through technology. Every donation matters. 🩸❤️