# 🏥 Healthcare Appointment Booking API

A comprehensive RESTful API system for managing healthcare appointment scheduling, built with Django REST Framework. This system provides focused functionality for appointment booking, patient management, medical services coordination, and payment processing to streamline the healthcare appointment experience.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture & Design Patterns](#architecture--design-patterns)
- [Features](#features)
- [Role-Based Access Control](#role-based-access-control-rbac)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Database Configuration](#database-configuration)
- [API Documentation](#api-documentation)
- [Core Modules](#core-modules)
- [Authentication & Authorization](#authentication--authorization)
- [Usage Examples](#usage-examples)

## 🔍 Overview

The Healthcare Appointment Booking API is designed to streamline the appointment scheduling process for healthcare services with a robust, scalable backend solution. The system focuses specifically on medical appointment management, allowing patients to book consultations with healthcare providers while supporting multiple user roles (Admin, Doctor, Patient, Staff) for efficient appointment coordination and management.

### Key Capabilities
- **Multi-role Authentication**: Secure JWT-based authentication system
- **Patient Management**: Complete patient registration and profile management
- **Medical Services**: Hospital, specialty, and doctor management
- **Appointment Scheduling**: Advanced scheduling with availability management and real-time booking
- **Payment Processing**: Integrated payment and billing system for appointments
- **Data Export**: Data export functionality for administrative tasks
- **API Documentation**: Complete Swagger/OpenAPI documentation
- **Audit Trail**: Comprehensive logging and audit capabilities

## 🏗️ Architecture & Design Patterns

### Clean Architecture
The project follows **Clean Architecture** principles with clear separation of concerns:

```
├── Core Layer (Business Logic)
│   ├── Models (Domain Entities)
│   ├── Services (Business Rules)
│   ├── Repositories (Data Access Abstraction)
│   └── Unit of Work Pattern
├── Application Layer (Use Cases)
│   ├── API Views
│   ├── Serializers
│   └── URL Routing
├── Infrastructure Layer
│   ├── Database (SQL Server)
│   ├── Authentication (JWT)
│   └── External Services
└── Presentation Layer
    └── REST API Endpoints
```

### Design Patterns Implemented

#### 1. **Repository Pattern**
- `BaseRepository`: Abstract base for all repository implementations
- Specific repositories: `UserRepository`, `MedicalRepository`, `AppointmentRepository`, `PaymentRepository`
- Provides consistent data access layer abstraction

#### 2. **Unit of Work Pattern**
- Manages transactions across multiple repositories
- Ensures data consistency and ACID properties
- Located in `core/unit_of_work.py`

#### 3. **Dependency Injection**
- Custom IoC container implementation (`core/dependency_injection.py`)
- Service registration and resolution
- Singleton and transient service lifetimes
- Circular dependency detection

#### 4. **Service Layer Pattern**
- Business logic separation from views
- `BaseService` and specialized service classes
- Validation and business rule enforcement

#### 5. **Decorator Pattern**
- Custom middleware for logging, authentication, and error handling
- API documentation decorators using drf-spectacular

#### 6. **Observer Pattern**
- Custom logging system with configurable handlers
- Health check monitoring system

## ✨ Features

### 🔐 Authentication & Authorization
- **JWT Authentication**: Secure token-based authentication
- **Role-based Access Control**: Admin, Doctor, Patient, Staff roles with granular permissions
- **Permission System**: Comprehensive permission matrix for different operations and data access
- **Session Management**: Access and refresh token handling with automatic timeout
- **Multi-layer Security**: API, data, and business logic level authorization enforcement

### 👥 User Management
- **Multi-role User System**: Support for different user types
- **Patient Registration**: Complete patient profile management
- **Doctor Profiles**: Doctor specialization and experience tracking
- **User Authentication**: Phone number-based authentication

### 🏥 Medical Services Management
- **Healthcare Facilities**: Hospital and clinic management
- **Medical Specialties**: Specialty categorization and management
- **Doctor Management**: Doctor profiles with specializations
- **Service Catalog**: Medical services with pricing and duration

### 📅 Appointment System
- **Schedule Management**: Doctor availability and working hours
- **Appointment Booking**: Patient appointment scheduling
- **Status Tracking**: Appointment status management (Pending, Confirmed, Completed, Cancelled)
- **Telemedicine Support**: Remote consultation sessions

### 💰 Payment Management
- **Billing System**: Service-based billing and payment tracking
- **Payment Processing**: Multiple payment method support
- **Financial Reporting**: Payment history and analytics

### 📈 Analytics & Statistics
- **Appointment Insights**: Aggregated counts and completion rates
- **Doctor Performance**: Productivity metrics and schedule utilization
- **Revenue Breakdown**: Earnings by service and month
- **Teleconsultation Analytics**: Session outcomes and average durations

### 📊 Data Management
- **Export**: Excel-based data export functionality
- **Reporting**: Comprehensive reporting system
- **Data Validation**: Robust input validation and sanitization

### 🔧 Administrative Features
- **Health Monitoring**: System health checks and monitoring
- **Audit Logging**: Comprehensive activity logging
- **Error Handling**: Centralized error management
- **API Versioning**: Version control for API endpoints

## 🔐 Role-Based Access Control (RBAC)

The Healthcare Appointment Booking API implements a comprehensive **Role-Based Access Control (RBAC)** system with four distinct user roles and granular permission management for secure and controlled access to system features.

### 👥 **User Roles & Hierarchy**

| Role | Level | Description | Access Level |
|------|-------|-------------|--------------|
| **🔴 ADMIN** | 1 | System administrator with full access | Full System Access |
| **🟡 DOCTOR** | 2 | Healthcare provider with clinical access | Clinical & Patient Management |
| **🟢 STAFF** | 3 | Administrative and support staff | Operational & Support |
| **🔵 PATIENT** | 4 | End-user patients | Self-Service & Booking |

### 📊 **Detailed Permission Matrix**

#### **🔴 ADMIN Role - Full System Access**
**Account Management:**
- ✅ **User Management**: Create, read, update, delete all user accounts
- ✅ **Role Assignment**: Assign and modify user roles and permissions
- ✅ **System Configuration**: Access to all system settings and configurations
- ✅ **Audit Logs**: View and manage all system activity logs

**Healthcare Operations:**
- ✅ **Medical Services**: Full CRUD operations on all medical services
- ✅ **Doctor Management**: Manage doctor profiles, specializations, and schedules
- ✅ **Facility Management**: Create and manage healthcare facilities
- ✅ **Specialty Management**: Manage medical specialties and categories

**Appointment System:**
- ✅ **Appointment Management**: View, create, modify, and cancel all appointments
- ✅ **Schedule Management**: Manage doctor schedules and availability
- ✅ **Booking Rules**: Configure appointment booking rules and policies
- ✅ **Override Permissions**: Override booking restrictions and policies

**Financial & Reporting:**
- ✅ **Payment Management**: Full access to payment processing and billing
- ✅ **Financial Reports**: Access to all financial and operational reports
- ✅ **Data Export**: Export all system data for analysis
- ✅ **System Analytics**: Access to comprehensive system analytics

#### **🟡 DOCTOR Role - Clinical & Patient Management**
**Patient Care:**
- ✅ **Patient Records**: View and update patient medical information
- ✅ **Appointment Management**: View and manage own appointments
- ✅ **Schedule Management**: Manage personal availability and working hours
- ✅ **Patient Communication**: Send messages and updates to patients

**Medical Services:**
- ✅ **Service Provision**: Provide and document medical services
- ✅ **Treatment Plans**: Create and manage patient treatment plans
- ✅ **Medical Notes**: Add and update patient medical notes
- ✅ **Prescription Management**: Manage patient prescriptions

**Appointment Operations:**
- ✅ **Own Appointments**: Full access to personal appointment schedule
- ✅ **Patient Booking**: Accept or decline appointment requests
- ✅ **Rescheduling**: Modify appointment times within constraints
- ✅ **Status Updates**: Update appointment status and notes

**Limited Access:**
- ❌ **User Management**: Cannot create or modify user accounts
- ❌ **System Configuration**: No access to system settings
- ❌ **Financial Reports**: Limited access to financial information
- ❌ **Other Doctors**: Cannot access other doctors' schedules

#### **🟢 STAFF Role - Operational & Support**
**Appointment Support:**
- ✅ **Appointment Booking**: Create and manage appointments for patients
- ✅ **Schedule Viewing**: View doctor schedules and availability
- ✅ **Patient Support**: Assist patients with booking and inquiries
- ✅ **Appointment Modifications**: Modify appointment details as needed

**Patient Management:**
- ✅ **Patient Registration**: Register new patients in the system
- ✅ **Patient Updates**: Update basic patient information
- ✅ **Patient Search**: Search and view patient records
- ✅ **Contact Management**: Manage patient contact information

**Operational Tasks:**
- ✅ **Basic Reporting**: Access to operational reports
- ✅ **Data Entry**: Enter and update basic system data
- ✅ **Customer Service**: Handle patient inquiries and support
- ✅ **Appointment Coordination**: Coordinate between patients and doctors

**Restricted Access:**
- ❌ **Medical Records**: Cannot view detailed medical information
- ❌ **Treatment Plans**: No access to medical treatment details
- ❌ **System Administration**: Cannot modify system settings
- ❌ **Financial Operations**: Limited access to financial data

#### **🔵 PATIENT Role - Self-Service & Booking**
**Personal Management:**
- ✅ **Profile Management**: View and update personal information
- ✅ **Medical History**: View own medical history and records
- ✅ **Appointment History**: View past and upcoming appointments
- ✅ **Personal Documents**: Access personal medical documents

**Appointment Services:**
- ✅ **Appointment Booking**: Book appointments with available doctors
- ✅ **Appointment Cancellation**: Cancel own appointments (within policy)
- ✅ **Rescheduling**: Request appointment time changes
- ✅ **Availability Viewing**: View doctor availability and schedules

**Communication:**
- ✅ **Message Reception**: Receive messages from healthcare providers
- ✅ **Notification Preferences**: Manage notification settings
- ✅ **Feedback Submission**: Submit feedback and ratings
- ✅ **Support Requests**: Request customer support assistance

**Access Limitations:**
- ❌ **Other Patients**: Cannot view other patients' information
- ❌ **Doctor Schedules**: Limited view of doctor availability
- ❌ **System Administration**: No administrative access
- ❌ **Financial Management**: Cannot access payment processing

### 🛡️ **Security Implementation**

#### **Authentication Layers**
1. **JWT Token Authentication**: Secure token-based authentication
2. **Role Verification**: Automatic role validation on each request
3. **Permission Checking**: Granular permission validation at API level
4. **Session Management**: Secure session handling with automatic timeout

#### **Authorization Enforcement**
- **API Level**: All endpoints validate user roles and permissions
- **Data Level**: Database queries filter data based on user role
- **UI Level**: Interface elements dynamically render based on permissions
- **Business Logic**: Service layer enforces role-based business rules

#### **Access Control Examples**

**Doctor Schedule Access:**
```python
# Only doctors can modify their own schedules
if user.role == 'DOCTOR' and schedule.doctor_id != user.id:
    raise PermissionDenied("Can only modify own schedule")

# Staff can view but not modify doctor schedules
if user.role == 'STAFF' and request.method in ['PUT', 'DELETE']:
    raise PermissionDenied("Staff cannot modify doctor schedules")
```

**Patient Data Access:**
```python
# Patients can only access their own data
if user.role == 'PATIENT' and patient_id != user.patient_id:
    raise PermissionDenied("Can only access own patient data")

# Doctors can access their patients' data
if user.role == 'DOCTOR' and not is_my_patient(doctor_id, patient_id):
    raise PermissionDenied("Can only access own patients' data")
```

### 🔄 **Role Transition & Management**

#### **Role Assignment Process**
1. **Initial Registration**: Users are assigned default roles based on registration type
2. **Role Upgrade**: Roles can be upgraded by administrators only
3. **Role Downgrade**: Role changes require administrative approval
4. **Temporary Roles**: Special access can be granted temporarily

#### **Permission Inheritance**
- **Higher roles inherit lower role permissions**
- **Role-specific permissions are additive**
- **Administrative overrides can grant temporary access**
- **Emergency access protocols for critical situations**

#### **Audit & Compliance**
- **All role changes are logged with administrator details**
- **Permission access is tracked for compliance reporting**
- **Regular access reviews are conducted**
- **Automated alerts for unusual access patterns**

## 🛠️ Technology Stack

### Backend Framework
- **Django 4.2.7**: Web framework
- **Django REST Framework 3.16+**: API development
- **djangorestframework-simplejwt 5.5+**: JWT authentication

### Database
- **SQL Server**: Primary database with `mssql-django` connector
- **ODBC Driver 17**: SQL Server connectivity

### API Documentation
- **drf-spectacular 0.27+**: OpenAPI 3.0 schema generation
- **Swagger UI**: Interactive API documentation
- **ReDoc**: Alternative API documentation interface

### Additional Libraries
- **django-cors-headers**: CORS handling
- **django-filter**: Advanced filtering
- **Pillow**: Image processing
- **openpyxl**: Excel file processing
- **pandas**: Data manipulation
- **reportlab**: PDF generation
- **python-dateutil**: Date/time utilities

## 📁 Project Structure

```
HospitalManagementAPI/
├── hospital_management/           # Main Django project
│   ├── hospital_management/       # Project settings
│   │   ├── settings.py            # Django configuration
│   │   ├── urls.py                # Main URL routing
│   │   └── wsgi.py                # WSGI application
│   │
│   ├── authentication/            # Authentication module
│   │   ├── models.py              # User model (NguoiDung)
│   │   ├── views.py               # Auth API endpoints
│   │   ├── serializers.py         # Auth serializers
│   │   ├── permissions.py         # Custom permissions
│   │   └── urls.py                # Auth URL routing
│   │
│   ├── users/                     # User management module
│   │   ├── models.py              # Patient model (BenhNhan)
│   │   ├── views.py               # User API endpoints
│   │   ├── serializers.py         # User serializers
│   │   └── urls.py                # User URL routing
│   │
│   ├── medical/                   # Medical services module
│   │   ├── models.py              # Medical entities (CoSoYTe, BacSi, DichVu, ChuyenKhoa)
│   │   ├── views.py               # Medical API endpoints
│   │   ├── serializers.py         # Medical serializers
│   │   └── urls.py                # Medical URL routing
│   │
│   ├── appointments/              # Appointment management
│   │   ├── models.py              # Appointment models (LichHen, LichLamViec)
│   │   ├── views.py               # Appointment API endpoints
│   │   ├── serializers.py         # Appointment serializers
│   │   └── urls.py                # Appointment URL routing
│   │
│   ├── payments/                  # Payment processing
│   │   ├── models.py              # Payment models
│   │   ├── views.py               # Payment API endpoints
│   │   ├── serializers.py         # Payment serializers
│   │   └── urls.py                # Payment URL routing
│   │
│   ├── utils/                     # Utility functions
│   │   ├── views.py               # Import/Export endpoints
│   │   └── urls.py                # Utility URL routing
│   │
│   └── core/                      # Core infrastructure
│       ├── repositories/          # Repository pattern implementation
│       │   ├── base.py            # Base repository
│       │   ├── user_repository.py # User data access
│       │   ├── medical_repository.py # Medical data access
│       │   ├── appointment_repository.py # Appointment data access
│       │   └── payment_repository.py # Payment data access
│       ├── services/              # Service layer
│       │   ├── base.py            # Base service
│       │   └── user_service.py    # User business logic
│       ├── dependency_injection.py # IoC container
│       ├── unit_of_work.py        # Unit of Work pattern
│       ├── models.py              # Base models and mixins
│       ├── exceptions.py          # Custom exceptions
│       ├── validators.py          # Input validation
│       ├── middleware.py          # Custom middleware
│       ├── pagination.py          # Custom pagination
│       ├── logging_config.py      # Logging configuration
│       ├── health_checks.py       # Health monitoring
│       └── views.py               # Core API views
│
├── database/                      # Database setup
│   ├── database_setup.sql         # Database schema
│   ├── create_test_users.sql      # Test data
│   └── set_passwords.py           # Password management
│
├── static/                        # Static files
├── requirements.txt               # Python dependencies
└── README.md                      # Project documentation
```

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- SQL Server 2019+ or SQL Server Express
- ODBC Driver 17 for SQL Server
- pip (Python package manager)

### Step-by-Step Setup

#### 1. Clone the Repository
```bash
git clone <repository-url>
cd HospitalManagementAPI
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Install ODBC Driver (Windows)
```bash
# Download and install ODBC Driver 17 for SQL Server
# https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
```

#### 5. Configure SQL Server & Create Database
```bash
# Start SQL Server service
# Configure authentication (SQL Server + Windows Authentication)

# Create database and tables using the prepared SQL script
# Run database/database_setup.sql in SQL Server Management Studio or sqlcmd
# This script will create the database 'He_thong_Dat_lich_kham_benh' and all necessary tables

# Optional: Load test data using the prepared script
# Run database/create_test_users.sql in SQL Server Management Studio or sqlcmd
# This script will insert sample users and test data for development
```

#### 6. Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DB_NAME=He_thong_Dat_lich_kham_benh
DB_USER=sa
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=1433
JWT_ALGORITHM=HS256
```

#### 7. Database Setup
```bash
# Navigate to project directory
cd hospital_management

# Run database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

#### 8. Load Test Data (Optional)
```bash
# Run test data script
python database/set_passwords.py

```

#### 9. Run Development Server
```bash
python manage.py runserver
```

#### 10. Verify Installation
```bash
# Test server is running
curl http://localhost:8000/api/docs/

# Access Swagger UI
# Open browser: http://localhost:8000/api/docs/
```

## 🗄️ Database Configuration

### Database Schema Overview

The system uses SQL Server with Vietnamese field names following the original database design:

#### Core Tables
- **Nguoi_dung**: User authentication and roles
- **Benh_nhan**: Patient information
- **Co_so_y_te**: Healthcare facilities
- **Chuyen_khoa**: Medical specialties
- **Bac_si**: Doctor profiles
- **Dich_vu**: Medical services
- **Lich_lam_viec**: Doctor schedules
- **Lich_hen**: Appointments
- **Phien_tu_van_tu_xa**: Telemedicine sessions

#### Database Connection Settings
```python
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'He_thong_Dat_lich_kham_benh',
        'USER': 'sa',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'unicode_results': True,
            'extra_params': 'MARS_Connection=Yes'
        },
    }
}
```

### Entity Relationships
```
NguoiDung (Users)
├── BenhNhan (Patients) [1:1]
└── BacSi (Doctors) [1:1]
    └── ChuyenKhoa (Specialties) [N:1]
        └── CoSoYTe (Facilities) [N:1]

LichHen (Appointments)
├── BenhNhan [N:1]
├── BacSi [N:1]
├── DichVu (Services) [N:1]
└── LichLamViec (Schedules) [N:1]
```

## 📚 API Documentation

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/api/docs/`
- **ReDoc**: `http://localhost:8000/api/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`

### Authentication Endpoints
```
POST /api/auth/login/          # User login
POST /api/auth/register/       # User registration
POST /api/auth/refresh/        # Refresh JWT token
POST /api/auth/verify/         # Verify JWT token
PUT  /api/auth/change-password/ # Change password
```

### User Management Endpoints
```
GET    /api/users/profile/     # Get user profile
PUT    /api/users/profile/     # Update user profile
GET    /api/users/patients/    # List patients (Admin only)
POST   /api/users/patients/    # Create patient
```

### Medical Services Endpoints
```
GET    /api/medical/facilities/    # List healthcare facilities
POST   /api/medical/facilities/    # Create facility (Admin)
GET    /api/medical/specialties/   # List specialties
GET    /api/medical/doctors/       # List doctors
GET    /api/medical/services/      # List medical services
```

### Appointment Endpoints
```
GET    /api/appointments/         # List appointments
POST   /api/appointments/         # Create appointment
PUT    /api/appointments/{id}/    # Update appointment
DELETE /api/appointments/{id}/    # Cancel appointment
GET    /api/appointments/schedule/ # Get doctor schedules
```

### Payment Endpoints
```
GET    /api/payments/            # List payments
POST   /api/payments/            # Process payment
GET    /api/payments/{id}/       # Get payment details
```

### Utility Endpoints
```
GET    /api/utils/export/benh-nhan/    # Export patients to Excel/CSV
GET    /api/utils/export/lich-hen/     # Export appointments to Excel/PDF
```

## 🔧 Core Modules

### Authentication Module
**Purpose**: Handles user authentication, authorization, and session management.

**Key Components**:
- **NguoiDung Model**: Custom user model with phone number authentication
- **JWT Authentication**: Token-based authentication with refresh capabilities
- **Role-based Permissions**: Admin, Doctor, Patient, Staff roles
- **Custom Serializers**: Registration, login, and password change serializers

**Key Features**:
- Phone number as username
- Vietnamese role names
- Password validation
- Token blacklisting
- Permission-based access control

### Users Module
**Purpose**: Manages patient profiles and user-related operations.

**Key Components**:
- **BenhNhan Model**: Patient information storage
- **Profile Management**: Complete patient profile CRUD operations
- **User Relationships**: Links users to patient records

**Key Features**:
- Patient registration and profile management
- Health insurance number tracking
- Contact information management
- Gender and demographic data

### Medical Module
**Purpose**: Manages healthcare facilities, doctors, specialties, and services.

**Key Components**:
- **CoSoYTe Model**: Healthcare facility management
- **ChuyenKhoa Model**: Medical specialty categorization
- **BacSi Model**: Doctor profile and specialization
- **DichVu Model**: Medical service catalog

**Key Features**:
- Multi-facility support
- Doctor specialization tracking
- Service pricing and duration
- Facility type categorization

### Appointments Module
**Purpose**: Handles appointment scheduling, doctor availability, and session management.

**Key Components**:
- **LichLamViec Model**: Doctor working schedules
- **LichHen Model**: Appointment booking and tracking
- **PhienTuVanTuXa Model**: Telemedicine session management

**Key Features**:
- Advanced scheduling system
- Availability management
- Appointment status tracking
- Telemedicine support
- Queue management

### Payments Module
**Purpose**: Manages billing, payment processing, and financial transactions.

**Key Components**:
- **Payment Models**: Transaction and billing management
- **Payment Processing**: Multiple payment method support
- **Financial Reporting**: Payment analytics and reporting

**Key Features**:
- Service-based billing
- Payment status tracking
- Financial reporting
- Transaction history

### Utils Module
**Purpose**: Provides utility functions for data export and administrative tasks.

**Key Components**:
- **Export Views**: Data export to various formats (Excel, CSV, PDF)
- **Administrative Tools**: Data management and reporting

**Key Features**:
- Excel/CSV/PDF export functionality
- Patient data export
- Appointment reporting
- Data validation and formatting

### Core Module
**Purpose**: Provides infrastructure components and shared functionality.

**Key Components**:
- **Repository Pattern**: Data access abstraction
- **Service Layer**: Business logic implementation
- **Dependency Injection**: IoC container for service management
- **Unit of Work**: Transaction management
- **Middleware**: Cross-cutting concerns
- **Validators**: Input validation and business rules

**Key Features**:
- Clean architecture implementation
- Centralized error handling
- Logging and monitoring
- Health checks
- API versioning
- Custom pagination

## 🔐 Authentication & Authorization

### JWT Authentication Flow
```python
# Login Process
1. User submits phone number + password
2. System validates credentials
3. JWT access + refresh tokens generated
4. Tokens returned to client
5. Client includes Bearer token in subsequent requests

# Token Structure
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "ma_nguoi_dung": 1,
    "so_dien_thoai": "0123456789",
    "vai_tro": "Bệnh nhân",
    "trang_thai": true
  }
}
```

### Role-based Access Control
```python
# User Roles
VAI_TRO_CHOICES = [
    ('Admin', 'Quản trị viên'),      # System Administrator
    ('Bác sĩ', 'Bác sĩ'),           # Doctor
    ('Bệnh nhân', 'Bệnh nhân'),     # Patient
    ('Nhân viên', 'Nhân viên y tế'), # Medical Staff
]

# Permission Matrix
- Admin: Full system access
- Doctor: Patient records, appointments, medical data
- Patient: Own profile, appointments, medical history
- Staff: Limited administrative functions
```

### Security Headers
```python
# JWT Configuration
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
}

# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True  # Development only
CORS_ALLOW_CREDENTIALS = True
```

## 💻 Usage Examples

### 1. User Registration and Login
```python
# Register new patient
POST /api/auth/register/
{
    "so_dien_thoai": "0123456789",
    "password": "securepassword123",
    "vai_tro": "Bệnh nhân"
}

# Login
POST /api/auth/login/
{
    "so_dien_thoai": "0123456789",
    "password": "securepassword123"
}

# Response
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "ma_nguoi_dung": 1,
        "so_dien_thoai": "0123456789",
        "vai_tro": "Bệnh nhân"
    }
}
```

### 2. Create Patient Profile
```python
# Create patient profile
POST /api/users/patients/
Authorization: Bearer <access_token>
{
    "ho_ten": "Nguyễn Văn A",
    "ngay_sinh": "1990-01-01",
    "gioi_tinh": "Nam",
    "cmnd_cccd": "123456789012",
    "so_bhyt": "HS1234567890123",
    "email": "nguyen.van.a@email.com",
    "dia_chi": "123 Đường ABC, Quận 1, TP.HCM"
}
```

### 3. Search and Book Appointment
```python
# Get available doctors
GET /api/medical/doctors/?chuyen_khoa=Tim mạch
Authorization: Bearer <access_token>

# Get doctor's schedule
GET /api/appointments/schedule/?ma_bac_si=1&ngay=2024-01-15
Authorization: Bearer <access_token>

# Book appointment
POST /api/appointments/
Authorization: Bearer <access_token>
{
    "ma_bac_si": 1,
    "ma_dich_vu": 1,
    "ngay_kham": "2024-01-15",
    "gio_kham": "09:00:00",
    "ghi_chu": "Khám định kỳ"
}
```

### 4. Process Payment
```python
# Create payment
POST /api/payments/
Authorization: Bearer <access_token>
{
    "ma_lich_hen": 1,
    "so_tien": 500000,
    "phuong_thuc_thanh_toan": "Tiền mặt",
    "ghi_chu": "Thanh toán dịch vụ khám bệnh"
}
```

### 5. Export Data
```python
# Export patients to Excel/CSV
GET /api/utils/export/benh-nhan/?format=excel
Authorization: Bearer <access_token>

# Export appointment report to Excel/PDF
GET /api/utils/export/lich-hen/?format=excel&start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <access_token>
```

### 6. Health Check
```python
# System health check
GET /api/health/
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00Z",
    "services": {
        "database": "healthy",
        "redis": "healthy",
        "external_apis": "healthy"
    }
}
```

### 7. Analytics & Statistics
```python
# Appointment statistics with optional date range
GET /api/appointments/lich-hen/statistics/?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <access_token>

# Doctor performance metrics
GET /api/medical/doctors/1/statistics/
Authorization: Bearer <access_token>

# Payment revenue breakdown
GET /api/payments/statistics/?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <admin_token>

# Teleconsultation session analytics
GET /api/appointments/teleconsultations/statistics/?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <access_token>
```
