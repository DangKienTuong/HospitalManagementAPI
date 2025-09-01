-- ===============================================
-- Create Test Users for Hospital Management System
-- Run this AFTER Django migrations are complete
-- ===============================================

USE He_thong_Dat_lich_kham_benh;
GO

-- ===============================================
-- Insert Medical Facilities (Co_so_y_te)
-- ===============================================
INSERT INTO Co_so_y_te (Ten_co_so, Loai_hinh, Dia_chi, So_dien_thoai, Email) VALUES
(N'Bệnh viện Chợ Rẫy', N'Bệnh viện công', N'201B Nguyễn Chí Thanh, Quận 5, TP.HCM', '0283855137', 'info@choray.vn'),
(N'Bệnh viện Đại học Y Dược TP.HCM', N'Bệnh viện công', N'215 Hồng Bàng, Quận 5, TP.HCM', '0283855287', 'contact@umc.edu.vn'),
(N'Bệnh viện FV', N'Bệnh viện tư', N'6 Nguyễn Lương Bằng, Quận 7, TP.HCM', '02854113333', 'info@fvhospital.com'),
(N'Phòng khám Đa khoa Quốc tế Columbia Asia', N'Phòng khám', N'08 Alexandre De Rhodes, Quận 1, TP.HCM', '02838238888', 'info@columbiaasia.com'),
(N'Trung tâm Y tế Quận 1', N'Trung tâm y tế', N'93 Pasteur, Quận 1, TP.HCM', '02838297235', 'ttyt.quan1@tphcm.gov.vn'),
(N'Bệnh viện Nhi đồng 1', N'Bệnh viện công', N'341 Sư Vạn Hạnh, Quận 10, TP.HCM', '02838326262', 'info@bvnd1.org.vn'),
(N'Bệnh viện Vinmec Central Park', N'Bệnh viện tư', N'208 Nguyễn Hữu Cảnh, Bình Thạnh, TP.HCM', '02836221166', 'info@vinmec.com');
GO

-- ===============================================
-- Insert Medical Specialties (Chuyen_khoa)
-- ===============================================
INSERT INTO Chuyen_khoa (Ma_co_so, Ten_chuyen_khoa, Mo_ta) VALUES
-- Bệnh viện Chợ Rẫy
(1, N'Tim mạch', N'Khoa khám và điều trị các bệnh về tim mạch'),
(1, N'Nội tiết', N'Khoa khám và điều trị các bệnh về nội tiết, tiểu đường'),
(1, N'Thần kinh', N'Khoa khám và điều trị các bệnh về thần kinh'),
-- Bệnh viện Đại học Y Dược
(2, N'Ngoại tổng quát', N'Khoa phẫu thuật tổng quát'),
(2, N'Sản phụ khoa', N'Khoa khám thai và điều trị các bệnh phụ khoa'),
(2, N'Nhi khoa', N'Khoa khám và điều trị bệnh cho trẻ em'),
-- Bệnh viện FV
(3, N'Tai mũi họng', N'Khoa khám và điều trị các bệnh tai mũi họng'),
(3, N'Mắt', N'Khoa khám và điều trị các bệnh về mắt'),
(3, N'Da liễu', N'Khoa khám và điều trị các bệnh về da'),
-- Phòng khám Columbia Asia
(4, N'Nội tổng quát', N'Khoa khám nội tổng quát'),
(4, N'Răng hàm mặt', N'Khoa khám và điều trị răng miệng'),
-- Trung tâm Y tế Quận 1
(5, N'Y học gia đình', N'Khoa khám bệnh tổng quát cho gia đình'),
(5, N'Phục hồi chức năng', N'Khoa vật lý trị liệu và phục hồi chức năng'),
-- Bệnh viện Nhi đồng 1
(6, N'Nhi khoa', N'Khoa khám và điều trị bệnh nhi'),
(6, N'Ngoại nhi', N'Khoa phẫu thuật nhi'),
-- Bệnh viện Vinmec
(7, N'Ung bướu', N'Khoa khám và điều trị ung thư'),
(7, N'Tim mạch', N'Khoa tim mạch can thiệp'),
(7, N'Chấn thương chỉnh hình', N'Khoa xương khớp và chấn thương');
GO

-- ===============================================
-- Insert Medical Services (Dich_vu)
-- ===============================================
INSERT INTO Dich_vu (Ma_co_so, Ma_chuyen_khoa, Ten_dich_vu, Loai_dich_vu, Gia_tien, Thoi_gian_kham, Mo_ta) VALUES
-- Bệnh viện Chợ Rẫy services
(1, 1, N'Khám tim mạch tổng quát', N'Khám bệnh', 300000, 30, N'Khám tổng quát tim mạch, điện tâm đồ'),
(1, 1, N'Siêu âm tim', N'Chẩn đoán hình ảnh', 500000, 20, N'Siêu âm tim doppler màu'),
(1, 1, N'Holter điện tâm đồ 24h', N'Xét nghiệm', 800000, 15, N'Theo dõi điện tâm đồ 24 giờ'),
(1, 2, N'Khám nội tiết', N'Khám bệnh', 250000, 30, N'Khám và tư vấn bệnh nội tiết'),
(1, 2, N'Xét nghiệm đường huyết', N'Xét nghiệm', 150000, 10, N'Xét nghiệm glucose máu'),
(1, 3, N'Khám thần kinh', N'Khám bệnh', 280000, 30, N'Khám và đánh giá thần kinh'),
(1, 3, N'Điện não đồ', N'Xét nghiệm', 400000, 30, N'Ghi điện não đồ'),

-- Bệnh viện Đại học Y Dược services
(2, 4, N'Khám ngoại khoa', N'Khám bệnh', 200000, 30, N'Khám ngoại tổng quát'),
(2, 4, N'Phẫu thuật nội soi', N'Thủ thuật', 5000000, 120, N'Phẫu thuật nội soi ổ bụng'),
(2, 5, N'Khám thai định kỳ', N'Khám bệnh', 250000, 30, N'Khám thai và siêu âm'),
(2, 5, N'Siêu âm 4D', N'Chẩn đoán hình ảnh', 600000, 30, N'Siêu âm thai 4D'),
(2, 6, N'Khám nhi tổng quát', N'Khám bệnh', 200000, 30, N'Khám sức khỏe trẻ em'),

-- Bệnh viện FV services
(3, 7, N'Khám tai mũi họng', N'Khám bệnh', 350000, 30, N'Khám TMH và nội soi'),
(3, 7, N'Nội soi tai mũi họng', N'Chẩn đoán hình ảnh', 500000, 20, N'Nội soi TMH chẩn đoán'),
(3, 8, N'Khám mắt tổng quát', N'Khám bệnh', 300000, 30, N'Khám mắt và đo thị lực'),
(3, 8, N'Đo khúc xạ máy', N'Xét nghiệm', 200000, 15, N'Đo độ cận thị, loạn thị'),
(3, 9, N'Khám da liễu', N'Khám bệnh', 350000, 30, N'Khám và tư vấn da'),
(3, 9, N'Laser trị liệu', N'Thủ thuật', 1500000, 45, N'Điều trị bằng laser'),

-- Phòng khám Columbia Asia services
(4, 10, N'Khám nội tổng quát', N'Khám bệnh', 400000, 30, N'Khám sức khỏe tổng quát'),
(4, 10, N'Tư vấn sức khỏe từ xa', N'Tư vấn từ xa', 200000, 20, N'Tư vấn online với bác sĩ'),
(4, 11, N'Khám răng', N'Khám bệnh', 250000, 30, N'Khám và tư vấn răng miệng'),
(4, 11, N'Cạo vôi răng', N'Thủ thuật', 300000, 45, N'Lấy cao răng và đánh bóng'),

-- Trung tâm Y tế Quận 1 services
(5, 12, N'Khám bệnh thông thường', N'Khám bệnh', 100000, 20, N'Khám bệnh cơ bản'),
(5, 13, N'Vật lý trị liệu', N'Thủ thuật', 200000, 45, N'Phục hồi chức năng vận động'),

-- Bệnh viện Nhi đồng 1 services
(6, 14, N'Khám nhi khoa', N'Khám bệnh', 180000, 30, N'Khám bệnh cho trẻ em'),
(6, 14, N'Tiêm chủng', N'Thủ thuật', 150000, 15, N'Tiêm vắc xin cho trẻ'),
(6, 15, N'Khám ngoại nhi', N'Khám bệnh', 200000, 30, N'Khám ngoại khoa cho trẻ'),

-- Bệnh viện Vinmec services
(7, 16, N'Tầm soát ung thư', N'Xét nghiệm', 2000000, 60, N'Gói tầm soát ung thư cơ bản'),
(7, 17, N'Khám tim mạch chuyên sâu', N'Khám bệnh', 500000, 45, N'Khám tim mạch can thiệp'),
(7, 17, N'Thông tim chẩn đoán', N'Chẩn đoán hình ảnh', 8000000, 90, N'Thông tim và chụp mạch vành'),
(7, 18, N'Khám xương khớp', N'Khám bệnh', 350000, 30, N'Khám chấn thương chỉnh hình'),
(7, 18, N'MRI khớp', N'Chẩn đoán hình ảnh', 3000000, 45, N'Chụp cộng hưởng từ khớp');
GO

-- ===============================================
-- Insert Test Users (Nguoi_dung)
-- ===============================================
-- WARNING: Using plain text passwords for testing only!
-- After running this script, use Django's management command to set proper passwords:
-- python manage.py changepassword <phone_number>

-- Admin users
INSERT INTO Nguoi_dung (So_dien_thoai, Mat_khau, Vai_tro, is_staff, is_superuser, is_active, Trang_thai, Ngay_tao) VALUES
('0901111111', 'password123', N'Admin', 1, 1, 1, 1, GETDATE()),
('0901111112', 'password123', N'Admin', 1, 0, 1, 1, GETDATE());

-- Doctor users
INSERT INTO Nguoi_dung (So_dien_thoai, Mat_khau, Vai_tro, is_staff, is_superuser, is_active, Trang_thai, Ngay_tao) VALUES
('0902222221', 'password123', N'Bác sĩ', 0, 0, 1, 1, GETDATE()),
('0902222222', 'password123', N'Bác sĩ', 0, 0, 1, 1, GETDATE()),
('0902222223', 'password123', N'Bác sĩ', 0, 0, 1, 1, GETDATE()),
('0902222224', 'password123', N'Bác sĩ', 0, 0, 1, 1, GETDATE()),
('0902222225', 'password123', N'Bác sĩ', 0, 0, 1, 1, GETDATE()),
('0902222226', 'password123', N'Bác sĩ', 0, 0, 1, 1, GETDATE()),
('0902222227', 'password123', N'Bác sĩ', 0, 0, 1, 1, GETDATE()),
('0902222228', 'password123', N'Bác sĩ', 0, 0, 1, 1, GETDATE());

-- Patient users
INSERT INTO Nguoi_dung (So_dien_thoai, Mat_khau, Vai_tro, is_staff, is_superuser, is_active, Trang_thai, Ngay_tao) VALUES
('0903333331', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE()),
('0903333332', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE()),
('0903333333', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE()),
('0903333334', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE()),
('0903333335', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE()),
('0903333336', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE()),
('0903333337', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE()),
('0903333338', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE()),
('0903333339', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE()),
('0903333340', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE()),
('0903333341', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE()),
('0903333342', 'password123', N'Bệnh nhân', 0, 0, 1, 1, GETDATE());

-- Staff users
INSERT INTO Nguoi_dung (So_dien_thoai, Mat_khau, Vai_tro, is_staff, is_superuser, is_active, Trang_thai, Ngay_tao) VALUES
('0904444441', 'password123', N'Nhân viên', 1, 0, 1, 1, GETDATE()),
('0904444442', 'password123', N'Nhân viên', 1, 0, 1, 1, GETDATE()),
('0904444443', 'password123', N'Nhân viên', 1, 0, 1, 1, GETDATE());
GO

-- ===============================================
-- Note: Django has already created foreign key constraints
-- ===============================================

-- ===============================================
-- Insert Doctors (Bac_si) - Using phone numbers to find user IDs
-- ===============================================
INSERT INTO Bac_si (Ma_nguoi_dung, Ma_co_so, Ma_chuyen_khoa, Ho_ten, Gioi_tinh, Hoc_vi, Kinh_nghiem, Gioi_thieu)
SELECT 
    nd.Ma_nguoi_dung,
    1, 1, N'Nguyễn Văn An', N'Nam', N'Bác sĩ', 25, N'Chuyên gia tim mạch hàng đầu với 25 năm kinh nghiệm'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0902222221'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    1, 2, N'Trần Thị Bình', N'Nữ', N'Phó giáo sư', 20, N'Chuyên gia về nội tiết và tiểu đường'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0902222222'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    2, 4, N'Lê Văn Cường', N'Nam', N'Tiến sĩ', 15, N'Bác sĩ phẫu thuật ngoại khoa giàu kinh nghiệm'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0902222223'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    2, 5, N'Phạm Thị Dung', N'Nữ', N'Thạc sĩ', 12, N'Chuyên khoa sản phụ khoa, thai sản'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0902222224'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    3, 7, N'Hoàng Minh Đức', N'Nam', N'Bác sĩ', 8, N'Bác sĩ tai mũi họng, chuyên về nội soi'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0902222225'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    3, 8, N'Võ Thị Em', N'Nữ', N'Tiến sĩ', 18, N'Chuyên gia về bệnh lý võng mạc và đục thủy tinh thể'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0902222226'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    4, 10, N'Đặng Văn Phong', N'Nam', N'Thạc sĩ', 10, N'Bác sĩ nội khoa tổng quát'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0902222227'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    6, 14, N'Ngô Thị Hoa', N'Nữ', N'Tiến sĩ', 16, N'Chuyên gia nhi khoa, chuyên về bệnh lý hô hấp ở trẻ'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0902222228';
GO

-- ===============================================
-- Insert Patients (Benh_nhan) - Using phone numbers to find user IDs
-- ===============================================
INSERT INTO Benh_nhan (Ma_nguoi_dung, Ho_ten, Ngay_sinh, Gioi_tinh, CMND_CCCD, So_BHYT, So_dien_thoai, Email, Dia_chi)
SELECT 
    nd.Ma_nguoi_dung,
    N'Trần Minh Tuấn', '1990-05-15', N'Nam', '079090123456', 'HS4010120456789', '0903333331', 'tuan.tran@gmail.com', N'123 Lê Lợi, Quận 1, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333331'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    N'Nguyễn Thị Mai', '1985-08-22', N'Nữ', '079085234567', 'HS4010120456790', '0903333332', 'mai.nguyen@gmail.com', N'456 Nguyễn Huệ, Quận 1, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333332'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    N'Lê Văn Hùng', '1978-03-10', N'Nam', '079078345678', 'HS4010120456791', '0903333333', 'hung.le@yahoo.com', N'789 Trần Hưng Đạo, Quận 5, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333333'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    N'Phạm Thị Lan', '1995-12-01', N'Nữ', '079095456789', 'HS4010120456792', '0903333334', 'lan.pham@gmail.com', N'321 Võ Văn Tần, Quận 3, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333334'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    N'Hoàng Minh Khôi', '2000-07-18', N'Nam', '079000567890', NULL, '0903333335', 'khoi.hoang@gmail.com', N'654 Cách Mạng Tháng 8, Quận 10, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333335'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    N'Đỗ Thị Ngọc', '1992-09-25', N'Nữ', '079092678901', 'HS4010120456793', '0903333336', 'ngoc.do@gmail.com', N'987 Điện Biên Phủ, Bình Thạnh, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333336'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    N'Võ Văn Nam', '1988-11-30', N'Nam', '079088789012', 'HS4010120456794', '0903333337', 'nam.vo@outlook.com', N'147 Lý Thường Kiệt, Quận 11, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333337'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    N'Bùi Thị Oanh', '1982-04-14', N'Nữ', '079082890123', NULL, '0903333338', 'oanh.bui@gmail.com', N'258 Nam Kỳ Khởi Nghĩa, Quận 3, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333338'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    N'Trương Văn Phúc', '1975-06-20', N'Nam', '079075901234', 'HS4010120456795', '0903333339', 'phuc.truong@gmail.com', N'369 Nguyễn Văn Cừ, Quận 5, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333339'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    N'Lý Thị Quỳnh', '1998-02-28', N'Nữ', NULL, 'HS4010120456796', '0903333340', 'quynh.ly@gmail.com', N'741 Phan Văn Trị, Gò Vấp, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333340'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    N'Đinh Văn Sơn', '1993-10-05', N'Nam', '079093012345', NULL, '0903333341', 'son.dinh@gmail.com', N'852 Xô Viết Nghệ Tĩnh, Bình Thạnh, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333341'
UNION ALL
SELECT 
    nd.Ma_nguoi_dung,
    N'Cao Thị Tuyết', '2005-01-12', N'Nữ', '079005123456', 'HS4010120456797', '0903333342', 'tuyet.cao@gmail.com', N'963 Lê Văn Sỹ, Phú Nhuận, TP.HCM'
FROM Nguoi_dung nd WHERE nd.So_dien_thoai = '0903333342';
GO

-- ===============================================
-- Insert Work Schedules (Lich_lam_viec) - Current and future dates
-- ===============================================
DECLARE @today DATE = GETDATE();
DECLARE @tomorrow DATE = DATEADD(day, 1, @today);
DECLARE @dayAfter DATE = DATEADD(day, 2, @today);
DECLARE @nextWeek DATE = DATEADD(day, 7, @today);

INSERT INTO Lich_lam_viec (Ma_bac_si, Ngay_lam_viec, Gio_bat_dau, Gio_ket_thuc, So_luong_kham, So_luong_da_dat)
SELECT 
    bs.Ma_bac_si, @today, '08:00', '12:00', 20, 5
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222221'
UNION ALL
SELECT 
    bs.Ma_bac_si, @today, '14:00', '17:00', 15, 3
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222221'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '08:00', '12:00', 20, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222221'
UNION ALL
SELECT 
    bs.Ma_bac_si, @dayAfter, '08:00', '12:00', 20, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222221'
UNION ALL
SELECT 
    bs.Ma_bac_si, @nextWeek, '08:00', '12:00', 20, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222221'
UNION ALL
SELECT 
    bs.Ma_bac_si, @today, '08:00', '12:00', 25, 10
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222222'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '08:00', '12:00', 25, 2
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222222'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '14:00', '17:00', 20, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222222'
UNION ALL
SELECT 
    bs.Ma_bac_si, @dayAfter, '08:00', '12:00', 25, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222222'
UNION ALL
SELECT 
    bs.Ma_bac_si, @today, '09:00', '12:00', 15, 8
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222223'
UNION ALL
SELECT 
    bs.Ma_bac_si, @today, '13:00', '16:00', 15, 5
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222223'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '09:00', '12:00', 15, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222223'
UNION ALL
SELECT 
    bs.Ma_bac_si, @nextWeek, '09:00', '12:00', 15, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222223'
UNION ALL
SELECT 
    bs.Ma_bac_si, @today, '08:00', '11:00', 18, 12
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222224'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '08:00', '11:00', 18, 3
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222224'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '14:00', '17:00', 15, 1
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222224'
UNION ALL
SELECT 
    bs.Ma_bac_si, @dayAfter, '08:00', '11:00', 18, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222224'
UNION ALL
SELECT 
    bs.Ma_bac_si, @today, '08:30', '11:30', 20, 15
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222225'
UNION ALL
SELECT 
    bs.Ma_bac_si, @today, '14:00', '17:00', 20, 8
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222225'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '08:30', '11:30', 20, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222225'
UNION ALL
SELECT 
    bs.Ma_bac_si, @dayAfter, '08:30', '11:30', 20, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222225'
UNION ALL
SELECT 
    bs.Ma_bac_si, @today, '07:30', '11:30', 22, 18
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222226'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '07:30', '11:30', 22, 5
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222226'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '13:30', '16:30', 18, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222226'
UNION ALL
SELECT 
    bs.Ma_bac_si, @nextWeek, '07:30', '11:30', 22, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222226'
UNION ALL
SELECT 
    bs.Ma_bac_si, @today, '08:00', '12:00', 30, 20
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222227'
UNION ALL
SELECT 
    bs.Ma_bac_si, @today, '14:00', '18:00', 30, 10
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222227'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '08:00', '12:00', 30, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222227'
UNION ALL
SELECT 
    bs.Ma_bac_si, @dayAfter, '08:00', '12:00', 30, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222227'
UNION ALL
SELECT 
    bs.Ma_bac_si, @today, '08:00', '11:00', 25, 22
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222228'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '08:00', '11:00', 25, 8
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222228'
UNION ALL
SELECT 
    bs.Ma_bac_si, @tomorrow, '14:00', '16:00', 20, 2
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222228'
UNION ALL
SELECT 
    bs.Ma_bac_si, @dayAfter, '08:00', '11:00', 25, 0
FROM Bac_si bs 
JOIN Nguoi_dung nd ON bs.Ma_nguoi_dung = nd.Ma_nguoi_dung 
WHERE nd.So_dien_thoai = '0902222228';
GO

-- ===============================================
-- Insert Appointments (Lich_hen) - Various statuses
-- ===============================================
DECLARE @today DATE = GETDATE();
DECLARE @tomorrow DATE = DATEADD(day, 1, @today);

INSERT INTO Lich_hen (Ma_benh_nhan, Ma_bac_si, Ma_dich_vu, Ma_lich, Ngay_kham, Gio_kham, So_thu_tu, Trang_thai, Ghi_chu, Ngay_tao) VALUES
-- Today's appointments with various statuses
(1, 1, 1, 1, @today, '08:30', 1, N'Hoan thanh', N'Bệnh nhân đã khám xong', DATEADD(day, -2, GETDATE())),
(2, 1, 2, 1, @today, '09:00', 2, N'Hoan thanh', N'Đã làm siêu âm tim', DATEADD(day, -2, GETDATE())),
(3, 1, 1, 1, @today, '09:30', 3, N'Da xac nhan', NULL, DATEADD(day, -1, GETDATE())),
(4, 1, 1, 1, @today, '10:00', 4, N'Da xac nhan', N'Khám định kỳ', DATEADD(day, -1, GETDATE())),
(5, 1, 3, 1, @today, '10:30', 5, N'Cho xac nhan', N'Cần làm Holter ECG', GETDATE()),

-- Dr. Trần Thị Bình's appointments
(6, 2, 4, 6, @today, '08:00', 1, N'Hoan thanh', N'Tái khám tiểu đường', DATEADD(day, -3, GETDATE())),
(7, 2, 5, 6, @today, '08:30', 2, N'Hoan thanh', N'Xét nghiệm định kỳ', DATEADD(day, -3, GETDATE())),
(8, 2, 4, 6, @today, '09:00', 3, N'Da xac nhan', NULL, DATEADD(day, -1, GETDATE())),
(9, 2, 4, 6, @today, '09:30', 4, N'Da xac nhan', N'Bệnh nhân mới', DATEADD(day, -1, GETDATE())),

-- Tomorrow's appointments
(10, 1, 1, 3, @tomorrow, '08:00', 1, N'Cho xac nhan', N'Khám sức khỏe định kỳ', GETDATE()),
(11, 2, 4, 7, @tomorrow, '08:30', 1, N'Cho xac nhan', N'Kiểm tra đường huyết', GETDATE()),
(12, 3, 8, 13, @tomorrow, '09:00', 1, N'Da xac nhan', N'Phẫu thuật nhỏ', DATEADD(hour, -5, GETDATE())),

-- Cancelled appointments
(1, 4, 10, 15, @today, '08:30', 1, N'Da huy', N'Bệnh nhân hủy do bận việc', DATEADD(day, -4, GETDATE())),
(2, 5, 13, 19, @today, '09:00', 2, N'Da huy', N'Đổi lịch khám', DATEADD(day, -3, GETDATE())),

-- Remote consultation appointments
(3, 7, 20, 25, @today, '14:00', 1, N'Da xac nhan', N'Tư vấn online', DATEADD(day, -1, GETDATE())),
(4, 7, 20, 25, @today, '14:30', 2, N'Cho xac nhan', N'Tư vấn sức khỏe', GETDATE()),

-- More varied appointments
(5, 6, 15, 22, @today, '08:00', 1, N'Hoan thanh', N'Khám mắt định kỳ', DATEADD(day, -5, GETDATE())),
(6, 8, 25, 29, @today, '08:30', 1, N'Da xac nhan', N'Khám nhi tổng quát', DATEADD(day, -1, GETDATE())),
(7, 3, 9, 11, @today, '13:30', 1, N'Da xac nhan', N'Chuẩn bị phẫu thuật', DATEADD(day, -2, GETDATE())),
(8, 5, 14, 20, @today, '14:30', 1, N'Da xac nhan', N'Nội soi TMH', DATEADD(day, -1, GETDATE()));
GO

-- ===============================================
-- Insert Remote Consultation Sessions (Phien_tu_van_tu_xa)
-- ===============================================
DECLARE @now DATETIME = GETDATE();

INSERT INTO Phien_tu_van_tu_xa (Ma_lich_hen, Ma_cuoc_goi, Thoi_gian_bat_dau, Thoi_gian_ket_thuc, Trang_thai, Ghi_chu_bac_si) VALUES
(15, 'CALL-2024-001', DATEADD(hour, -2, @now), DATEADD(hour, -1.5, @now), N'Da ket thuc', N'Tư vấn về chế độ ăn uống cho bệnh nhân tiểu đường'),
(16, NULL, NULL, NULL, N'Chua bat dau', NULL);
GO

-- ===============================================
-- Insert Payments (Thanh_toan)
-- ===============================================
INSERT INTO Thanh_toan (Ma_lich_hen, So_tien, Phuong_thuc, Trang_thai, Ma_giao_dich, Thoi_gian_thanh_toan) VALUES
-- Completed payments
(1, 300000, N'Tien mat', N'Da thanh toan', NULL, DATEADD(hour, -6, GETDATE())),
(2, 500000, N'The tin dung', N'Da thanh toan', 'VISA-20240101-001', DATEADD(hour, -5, GETDATE())),
(6, 250000, N'Chuyen khoan', N'Da thanh toan', 'VCB-20240101-002', DATEADD(hour, -8, GETDATE())),
(7, 150000, N'Vi dien tu', N'Da thanh toan', 'MOMO-20240101-003', DATEADD(hour, -7, GETDATE())),
(17, 300000, N'Tien mat', N'Da thanh toan', NULL, DATEADD(hour, -4, GETDATE())),

-- Pending payments
(3, 300000, N'Tien mat', N'Chua thanh toan', NULL, NULL),
(4, 300000, N'The tin dung', N'Chua thanh toan', NULL, NULL),
(8, 250000, N'Chuyen khoan', N'Chua thanh toan', NULL, NULL),
(9, 250000, N'Vi dien tu', N'Chua thanh toan', NULL, NULL),
(12, 5000000, N'Chuyen khoan', N'Chua thanh toan', NULL, NULL),

-- Refunded payments
(13, 250000, N'The tin dung', N'Da hoan tien', 'VISA-20240101-004', DATEADD(day, -3, GETDATE())),
(14, 500000, N'Chuyen khoan', N'Da hoan tien', 'VCB-20240101-005', DATEADD(day, -2, GETDATE()));
GO

-- ===============================================
-- Create indexes for better performance
-- ===============================================
CREATE INDEX idx_nguoi_dung_phone ON Nguoi_dung(So_dien_thoai);
CREATE INDEX idx_lich_hen_date ON Lich_hen(Ngay_kham);
CREATE INDEX idx_lich_hen_status ON Lich_hen(Trang_thai);
CREATE INDEX idx_lich_hen_patient ON Lich_hen(Ma_benh_nhan);
CREATE INDEX idx_lich_hen_doctor ON Lich_hen(Ma_bac_si);
CREATE INDEX idx_lich_lam_viec_doctor ON Lich_lam_viec(Ma_bac_si);
CREATE INDEX idx_lich_lam_viec_date ON Lich_lam_viec(Ngay_lam_viec);
CREATE INDEX idx_thanh_toan_status ON Thanh_toan(Trang_thai);
CREATE INDEX idx_benh_nhan_cccd ON Benh_nhan(CMND_CCCD);
CREATE INDEX idx_benh_nhan_bhyt ON Benh_nhan(So_BHYT);
GO

-- ===============================================
-- Create views for common queries
-- ===============================================
CREATE VIEW V_AppointmentDetails AS
SELECT 
    lh.Ma_lich_hen,
    bn.Ho_ten AS Ten_benh_nhan,
    bn.So_dien_thoai AS SDT_benh_nhan,
    bs.Ho_ten AS Ten_bac_si,
    bs.Hoc_vi,
    cs.Ten_co_so,
    ck.Ten_chuyen_khoa,
    dv.Ten_dich_vu,
    dv.Gia_tien,
    lh.Ngay_kham,
    lh.Gio_kham,
    lh.So_thu_tu,
    lh.Trang_thai,
    tt.Trang_thai AS Trang_thai_thanh_toan
FROM Lich_hen lh
    JOIN Benh_nhan bn ON lh.Ma_benh_nhan = bn.Ma_benh_nhan
    JOIN Bac_si bs ON lh.Ma_bac_si = bs.Ma_bac_si
    JOIN Dich_vu dv ON lh.Ma_dich_vu = dv.Ma_dich_vu
    JOIN Co_so_y_te cs ON bs.Ma_co_so = cs.Ma_co_so
    LEFT JOIN Chuyen_khoa ck ON bs.Ma_chuyen_khoa = ck.Ma_chuyen_khoa
    LEFT JOIN Thanh_toan tt ON lh.Ma_lich_hen = tt.Ma_lich_hen;
GO

CREATE VIEW V_DoctorSchedule AS
SELECT 
    bs.Ma_bac_si,
    bs.Ho_ten,
    bs.Hoc_vi,
    cs.Ten_co_so,
    ck.Ten_chuyen_khoa,
    llv.Ngay_lam_viec,
    llv.Gio_bat_dau,
    llv.Gio_ket_thuc,
    llv.So_luong_kham,
    llv.So_luong_da_dat,
    (llv.So_luong_kham - llv.So_luong_da_dat) AS Cho_trong
FROM Lich_lam_viec llv
    JOIN Bac_si bs ON llv.Ma_bac_si = bs.Ma_bac_si
    JOIN Co_so_y_te cs ON bs.Ma_co_so = cs.Ma_co_so
    LEFT JOIN Chuyen_khoa ck ON bs.Ma_chuyen_khoa = ck.Ma_chuyen_khoa;
GO

-- Add some statistics data for reporting
CREATE VIEW V_Statistics AS
SELECT 
    'Total Patients' AS Metric,
    COUNT(*) AS Value
FROM Benh_nhan
UNION ALL
SELECT 
    'Total Doctors',
    COUNT(*)
FROM Bac_si
UNION ALL
SELECT 
    'Total Appointments',
    COUNT(*)
FROM Lich_hen
UNION ALL
SELECT 
    'Completed Appointments Today',
    COUNT(*)
FROM Lich_hen
WHERE Trang_thai = 'Hoan thanh' AND Ngay_kham = CAST(GETDATE() AS DATE)
UNION ALL
SELECT 
    'Pending Appointments',
    COUNT(*)
FROM Lich_hen
WHERE Trang_thai IN ('Cho xac nhan', 'Da xac nhan')
UNION ALL
SELECT 
    'Total Revenue (Paid)',
    CAST(ISNULL(SUM(So_tien), 0) AS NVARCHAR(50))
FROM Thanh_toan
WHERE Trang_thai = 'Da thanh toan';
GO

PRINT '===============================================';
PRINT 'Test data created successfully!';
PRINT '===============================================';
PRINT '';
PRINT 'Summary of created data:';
PRINT '- Medical Facilities: 7 facilities';
PRINT '- Medical Specialties: 18 specialties';
PRINT '- Medical Services: 33 services';
PRINT '- Admin users: 2 (phone: 0901111111, 0901111112)';
PRINT '- Doctor users: 8 (phone: 0902222221-0902222228)';
PRINT '- Patient users: 12 (phone: 0903333331-0903333342)';
PRINT '- Staff users: 3 (phone: 0904444441-0904444443)';
PRINT '- Work schedules: 32 schedules for current and future dates';
PRINT '- Appointments: 20 appointments with various statuses';
PRINT '- Remote consultations: 2 sessions';
PRINT '- Payments: 12 payment records';
PRINT '- Indexes: 10 indexes for performance';
PRINT '- Views: 3 views for common queries';
PRINT '';
PRINT '';
PRINT 'IMPORTANT: Passwords are stored as plain text for testing!';
PRINT 'To set proper Django passwords, run the following Python script:';
PRINT 'python manage.py shell < set_passwords.py';
PRINT 'Or manually set passwords using: python manage.py changepassword <phone_number>';
PRINT '===============================================';
GO
