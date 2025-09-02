# 🚀 HƯỚNG DẪN CHẠY HOSPITAL MANAGEMENT API

## 📋 Yêu Cầu Hệ Thống

### 1. Phần Mềm Cần Thiết
- **Python 3.8+** (Khuyến nghị Python 3.9 hoặc 3.10)
- **SQL Server** (SQL Server Express hoặc SQL Server Developer Edition)
- **Git** (để clone project)
- **Visual Studio Code** hoặc IDE khác (tùy chọn)

### 2. Cài Đặt SQL Server
1. Tải và cài đặt SQL Server từ Microsoft
2. Cài đặt SQL Server Management Studio (SSMS)
3. Đảm bảo SQL Server đang chạy với cấu hình:
   - Server: `localhost`
   - Port: `1433`
   - Username: `sa`
   - Password: `123`

## 🛠️ Cài Đặt Project

### Bước 1: Clone Project
```bash
git clone <repository-url>
cd HospitalManagementAPI
```

### Bước 2: Tạo Virtual Environment
```bash
# Tạo virtual environment
python -m venv hospital_env

# Kích hoạt virtual environment
# Trên Windows:
hospital_env\Scripts\activate

# Trên macOS/Linux:
source hospital_env/bin/activate
```

### Bước 3: Cài Đặt Dependencies
```bash
# Cài đặt các package từ requirements.txt
pip install -r requirements.txt

# Nếu gặp lỗi với mssql-django, cài đặt thêm:
pip install pyodbc
```

### Bước 4: Cài Đặt ODBC Driver
- **Windows**: Tải và cài đặt "ODBC Driver 17 for SQL Server" từ Microsoft
- **macOS**: `brew install msodbcsql17`
- **Linux**: Làm theo hướng dẫn của Microsoft cho distribution của bạn

## 🗄️ Thiết Lập Database

### Bước 1: Tạo Database
```bash
# Mở SQL Server Management Studio (SSMS)
# Kết nối với server: localhost
# Chạy script trong file: database/database_setup.sql
```

Hoặc chạy từ command line:
```bash
sqlcmd -S localhost -U sa -P 123 -i database/database_setup.sql
```

### Bước 2: Chạy Django Migrations
```bash
# Di chuyển vào thư mục hospital_management
cd hospital_management

# Tạo migrations
python manage.py makemigrations

# Chạy migrations
python manage.py migrate

# Tạo superuser (tùy chọn)
python manage.py createsuperuser
```

### Bước 3: Load Test Data (Tùy chọn)
```bash
# Chạy script để tạo dữ liệu test
python manage.py seed_db

# Hoặc chạy SQL script để tạo test users
sqlcmd -S localhost -U sa -P 123 -i ../database/create_test_users.sql
```

## 🚀 Chạy Server

### Chạy Development Server
```bash
# Đảm bảo bạn đang ở trong thư mục hospital_management
cd hospital_management

# Chạy server
python manage.py runserver

# Server sẽ chạy tại: http://127.0.0.1:8000/
```

### Chạy với Port Khác
```bash
python manage.py runserver 8080
# Server sẽ chạy tại: http://127.0.0.1:8080/
```

## 📚 Truy Cập API Documentation

### Swagger UI
- **URL**: http://127.0.0.1:8000/api/schema/swagger-ui/
- **Mô tả**: Giao diện tương tác để test API

### ReDoc
- **URL**: http://127.0.0.1:8000/api/schema/redoc/
- **Mô tả**: Documentation đẹp và dễ đọc

### OpenAPI Schema
- **URL**: http://127.0.0.1:8000/api/schema/
- **Mô tả**: Schema JSON/YAML để import vào Postman

## 🔐 Authentication

### Endpoints Chính
- **Login**: `POST /api/v1/auth/login/`
- **Register**: `POST /api/v1/auth/register/`
- **Refresh Token**: `POST /api/v1/auth/token/refresh/`

### Test Users (Nếu đã load test data)
```json
{
  "admin": {
    "username": "admin",
    "password": "admin123"
  },
  "doctor": {
    "username": "doctor1",
    "password": "doctor123"
  },
  "patient": {
    "username": "patient1",
    "password": "patient123"
  }
}
```

## 🧪 Test API

### Sử dụng curl
```bash
# Login
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# Sử dụng token để gọi API
curl -X GET http://127.0.0.1:8000/api/v1/appointments/ \
  -H "Authorization: Bearer <your-access-token>"
```

### Sử dụng Postman
1. Import OpenAPI schema từ: http://127.0.0.1:8000/api/schema/
2. Thiết lập Bearer Token authentication
3. Test các endpoints

## 📁 Cấu Trúc API Endpoints

```
/api/v1/
├── auth/
│   ├── login/
│   ├── register/
│   ├── token/refresh/
│   └── profile/
├── users/
├── medical/
│   ├── hospitals/
│   ├── specialties/
│   └── doctors/
├── appointments/
├── payments/
└── utils/
    ├── export/
    └── import/
```

## ⚠️ Troubleshooting

### Lỗi Kết Nối Database
```bash
# Kiểm tra SQL Server có đang chạy không
services.msc # Tìm SQL Server services

# Kiểm tra kết nối
sqlcmd -S localhost -U sa -P 123
```

### Lỗi ODBC Driver
```bash
# Cài đặt lại ODBC Driver 17 for SQL Server
# Đảm bảo version match với hệ điều hành
```

### Lỗi Migrations
```bash
# Reset migrations (cẩn thận - sẽ mất data)
python manage.py migrate --fake-initial

# Hoặc xóa migrations và tạo lại
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete
python manage.py makemigrations
python manage.py migrate
```

### Lỗi Static Files
```bash
# Collect static files
python manage.py collectstatic --noinput
```

## 🔧 Cấu Hình Môi Trường

### File .env (Tạo trong thư mục hospital_management)
```env
DEBUG=True
SECRET_KEY=your-secret-key-here
DB_NAME=He_thong_Dat_lich_kham_benh
DB_USER=sa
DB_PASSWORD=123
DB_HOST=localhost
DB_PORT=1433
```

## 📊 Monitoring và Logs

### Xem Logs
```bash
# Django logs sẽ hiển thị trong terminal khi chạy runserver
python manage.py runserver --verbosity=2
```

### Health Check
- **URL**: http://127.0.0.1:8000/health/
- **Mô tả**: Kiểm tra trạng thái server và database

## 🎯 Next Steps

1. **Khám phá API Documentation** tại Swagger UI
2. **Test các endpoints** cơ bản
3. **Tạo dữ liệu test** cho ứng dụng của bạn
4. **Tích hợp với frontend** (nếu có)
5. **Cấu hình production** khi deploy

---

**Chúc bạn thành công! 🎉**

Nếu gặp vấn đề gì, hãy kiểm tra logs và đảm bảo tất cả dependencies đã được cài đặt đúng cách.
