# Hệ thống Quản lý Đặt lịch Khám bệnh - Hospital Management API

## Tổng quan

Hệ thống Web API backend được xây dựng bằng Django REST Framework để quản lý việc đặt lịch khám bệnh và tư vấn từ xa. Hệ thống hỗ trợ đầy đủ các chức năng từ quản lý người dùng, cơ sở y tế, bác sĩ, dịch vụ khám, lịch hẹn, thanh toán đến tư vấn từ xa.

## Công nghệ sử dụng

- **Backend Framework**: Django 4.2.7 + Django REST Framework 3.14.0
- **Database**: Microsoft SQL Server
- **Authentication**: JWT (JSON Web Token)
- **File Processing**: pandas, openpyxl
- **Report Generation**: reportlab (PDF)
- **Others**: django-cors-headers, python-decouple

## Cấu trúc dự án

```
HospitalManagementAPI/
├── database/
│   ├── init_database.sql              # Script SQL khởi tạo CSDL gốc
│   └── init_database_updated.sql      # Script SQL với tên bảng không dấu
├── hospital_management/
│   ├── authentication/                # App xác thực và phân quyền
│   ├── users/                         # App quản lý bệnh nhân
│   ├── medical/                       # App quản lý cơ sở y tế, bác sĩ, dịch vụ
│   ├── appointments/                  # App quản lý lịch hẹn, tư vấn từ xa
│   ├── payments/                      # App quản lý thanh toán
│   ├── utils/                         # Utilities nhập/xuất dữ liệu
│   └── hospital_management/           # Settings và URL configuration
├── requirements.txt                   # Dependencies
└── README.md                         # Tài liệu này
```

## Cài đặt và chạy dự án

### 1. Yêu cầu hệ thống

- Python 3.8+
- Microsoft SQL Server
- pip (Python package manager)

### 2. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 3. Cấu hình database

1. Tạo database SQL Server:
   - Chạy script `database/init_database_updated.sql` để tạo database và dữ liệu mẫu
   - Database name: `He_thong_Dat_lich_kham_benh`

2. Cập nhật cấu hình database trong `hospital_management/settings.py`:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'mssql',
           'NAME': 'He_thong_Dat_lich_kham_benh',
           'USER': 'your_username',
           'PASSWORD': 'your_password',
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

### 4. Chạy migration

```bash
cd hospital_management
python manage.py makemigrations
python manage.py migrate
```

### 5. Tạo superuser

```bash
python manage.py createsuperuser
```

### 6. Chạy server

```bash
python manage.py runserver
```

API sẽ chạy tại: `http://localhost:8000/`

## API Endpoints

### Authentication (Xác thực)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/auth/register/` | Đăng ký tài khoản |
| POST | `/api/auth/login/` | Đăng nhập |
| POST | `/api/auth/refresh/` | Refresh token |
| GET | `/api/auth/profile/` | Xem profile |
| POST | `/api/auth/change-password/` | Đổi mật khẩu |
| GET | `/api/auth/permissions/` | Kiểm tra quyền |

### Users (Người dùng)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/users/benh-nhan/` | Danh sách bệnh nhân |
| POST | `/api/users/benh-nhan/` | Tạo bệnh nhân mới |
| GET | `/api/users/benh-nhan/{id}/` | Chi tiết bệnh nhân |
| PUT/PATCH | `/api/users/benh-nhan/{id}/` | Cập nhật bệnh nhân |
| GET | `/api/users/benh-nhan/profile/` | Profile bệnh nhân hiện tại |
| GET | `/api/users/benh-nhan/{id}/lich-su-kham/` | Lịch sử khám |

### Medical (Y tế)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/medical/co-so-y-te/` | Danh sách cơ sở y tế |
| GET | `/api/medical/chuyen-khoa/` | Danh sách chuyên khoa |
| GET | `/api/medical/bac-si/` | Danh sách bác sĩ |
| GET | `/api/medical/dich-vu/` | Danh sách dịch vụ |
| GET | `/api/medical/bac-si/profile/` | Profile bác sĩ hiện tại |
| GET | `/api/medical/dich-vu/tu-van-tu-xa/` | Dịch vụ tư vấn từ xa |

### Appointments (Lịch hẹn)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/appointments/lich-lam-viec/` | Lịch làm việc bác sĩ |
| POST | `/api/appointments/lich-lam-viec/` | Tạo lịch làm việc |
| GET | `/api/appointments/lich-hen/` | Danh sách lịch hẹn |
| POST | `/api/appointments/lich-hen/` | Đặt lịch hẹn |
| PATCH | `/api/appointments/lich-hen/{id}/update-status/` | Cập nhật trạng thái |
| POST | `/api/appointments/lich-hen/{id}/cancel/` | Hủy lịch hẹn |
| GET | `/api/appointments/phien-tu-van/` | Phiên tư vấn từ xa |
| POST | `/api/appointments/phien-tu-van/{id}/start-session/` | Bắt đầu tư vấn |
| POST | `/api/appointments/phien-tu-van/{id}/end-session/` | Kết thúc tư vấn |

### Payments (Thanh toán)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| GET | `/api/payments/thanh-toan/` | Danh sách thanh toán |
| POST | `/api/payments/thanh-toan/` | Tạo thanh toán |
| PATCH | `/api/payments/thanh-toan/{id}/update-status/` | Cập nhật trạng thái |
| POST | `/api/payments/thanh-toan/{id}/process-payment/` | Xử lý thanh toán |
| GET | `/api/payments/thanh-toan/statistics/` | Thống kê thanh toán |

### Utils (Tiện ích)

| Method | Endpoint | Mô tả |
|--------|----------|-------|
| POST | `/api/utils/import/benh-nhan/` | Nhập dữ liệu bệnh nhân |
| POST | `/api/utils/import/co-so-y-te/` | Nhập dữ liệu cơ sở y tế |
| POST | `/api/utils/import/bac-si/` | Nhập dữ liệu bác sĩ |
| POST | `/api/utils/import/dich-vu/` | Nhập dữ liệu dịch vụ |
| GET | `/api/utils/export/benh-nhan/` | Xuất danh sách bệnh nhân |
| GET | `/api/utils/export/lich-hen/` | Xuất báo cáo lịch hẹn |
| GET | `/api/utils/export/thong-ke/` | Xuất báo cáo thống kê |

## Phân quyền người dùng

### Vai trò trong hệ thống:

1. **Quản trị viên (Admin)**: Toàn quyền quản lý hệ thống
2. **Bác sĩ**: Quản lý lịch làm việc, xác nhận lịch hẹn, tư vấn từ xa
3. **Bệnh nhân**: Đặt lịch hẹn, xem lịch sử khám, thanh toán
4. **Nhân viên y tế**: Hỗ trợ quản lý thông tin bệnh nhân và lịch hẹn

### Quyền truy cập:

- **Anonymous**: Xem danh sách cơ sở y tế, chuyên khoa, bác sĩ, dịch vụ
- **Authenticated**: Truy cập thông tin cá nhân, đặt lịch hẹn
- **Role-based**: Phân quyền theo vai trò cụ thể

## Mô hình dữ liệu

### 10 bảng chính:

1. **Nguoi_dung**: Tài khoản người dùng
2. **Benh_nhan**: Thông tin bệnh nhân
3. **Co_so_y_te**: Cơ sở y tế
4. **Chuyen_khoa**: Chuyên khoa
5. **Bac_si**: Thông tin bác sĩ
6. **Dich_vu**: Dịch vụ khám bệnh
7. **Lich_lam_viec**: Lịch làm việc bác sĩ
8. **Lich_hen**: Lịch hẹn khám bệnh
9. **Thanh_toan**: Thanh toán
10. **Phien_tu_van_tu_xa**: Phiên tư vấn từ xa

## Tính năng chính

### 1. Quản lý người dùng
- Đăng ký/đăng nhập với JWT
- Phân quyền theo vai trò
- Quản lý profile cá nhân

### 2. Quản lý cơ sở y tế
- CRUD cơ sở y tế, chuyên khoa
- Quản lý bác sĩ và dịch vụ
- Tìm kiếm và lọc dữ liệu

### 3. Đặt lịch khám bệnh
- Xem lịch làm việc bác sĩ
- Đặt lịch hẹn online
- Quản lý trạng thái lịch hẹn
- Hủy lịch hẹn

### 4. Tư vấn từ xa
- Tạo phiên tư vấn online
- Quản lý cuộc gọi video
- Lưu ghi chú tư vấn

### 5. Thanh toán
- Đa dạng phương thức thanh toán
- Theo dõi trạng thái thanh toán
- Thống kê doanh thu

### 6. Nhập/xuất dữ liệu
- Import từ file CSV/Excel
- Export báo cáo Excel/PDF
- Thống kê và báo cáo

## Sử dụng API

### 1. Authentication

```bash
# Đăng nhập
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"so_dien_thoai": "0912345678", "mat_khau": "password123"}'

# Response
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "ma_nguoi_dung": 1,
    "so_dien_thoai": "0912345678",
    "vai_tro": "Benh nhan"
  }
}
```

### 2. Sử dụng token

```bash
# Gọi API với token
curl -X GET http://localhost:8000/api/medical/bac-si/ \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 3. Đặt lịch hẹn

```bash
curl -X POST http://localhost:8000/api/appointments/lich-hen/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ma_bac_si": 1,
    "ma_dich_vu": 1,
    "ma_lich": 1,
    "ghi_chu": "Khám định kỳ"
  }'
```

### 4. Upload file import

```bash
curl -X POST http://localhost:8000/api/utils/import/benh-nhan/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@benh_nhan.csv"
```

## Dữ liệu mẫu

Hệ thống đã có sẵn dữ liệu mẫu bao gồm:

- 10 tài khoản người dùng với các vai trò khác nhau
- 3 bệnh nhân mẫu
- 4 cơ sở y tế
- 9 chuyên khoa
- 4 bác sĩ
- 6 dịch vụ khám bệnh
- 5 lịch làm việc
- 5 lịch hẹn
- 5 thanh toán
- 1 phiên tư vấn từ xa

## Troubleshooting

### Lỗi kết nối database
- Kiểm tra SQL Server đã chạy
- Xác nhận thông tin kết nối trong settings.py
- Cài đặt ODBC Driver 17 for SQL Server

### Lỗi import file
- Kiểm tra format file CSV/Excel
- Đảm bảo có đủ cột bắt buộc
- Kiểm tra encoding UTF-8

### Lỗi authentication
- Kiểm tra token hết hạn
- Refresh token nếu cần
- Kiểm tra quyền truy cập endpoint

## Đóng góp

1. Fork dự án
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit thay đổi (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

## License

Dự án này thuộc về đại học và chỉ dành cho mục đích học tập.

## Liên hệ

- Sinh viên: [Tên sinh viên]
- Email: [Email sinh viên]
- Trường: Đại học [Tên trường]
- Môn học: [Tên môn học]