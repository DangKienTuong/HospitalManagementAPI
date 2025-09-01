import os
import sys
import random
from decimal import Decimal
from datetime import datetime, timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from users.models import BenhNhan
from medical.models import CoSoYTe, ChuyenKhoa, BacSi, DichVu
from appointments.models import LichHen, PhienTuVanTuXa, LichLamViec
from payments.models import ThanhToan

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting database seeding...'))
        
        # Clear existing data
        self.clear_database()
        
        # Create data
        self.create_admin_user()
        patients = self.create_users_and_patients()
        facilities = self.create_medical_facilities()
        specialties = self.create_specialties(facilities)
        doctors = self.create_doctors(facilities, specialties)
        services = self.create_services(facilities)
        schedules = self.create_work_schedules(doctors)
        appointments = self.create_appointments(patients, doctors, services, schedules)
        sessions = self.create_telemedicine_sessions(appointments)
        payments = self.create_payments(appointments)
        
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully!'))
        self.stdout.write(f"Created {len(patients)} patients, {len(doctors)} doctors, {len(appointments)} appointments")

    def clear_database(self):
        """Clear existing data"""
        self.stdout.write("Clearing existing data...")
        ThanhToan.objects.all().delete()
        PhienTuVanTuXa.objects.all().delete()
        LichHen.objects.all().delete()
        LichLamViec.objects.all().delete()
        DichVu.objects.all().delete()
        BacSi.objects.all().delete()
        ChuyenKhoa.objects.all().delete()
        CoSoYTe.objects.all().delete()
        BenhNhan.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()
        self.stdout.write("Database cleared.")

    def create_admin_user(self):
        """Create admin user if not exists"""
        self.stdout.write("Creating admin user...")
        if not User.objects.filter(username="admin").exists():
            admin_user = User.objects.create_superuser(
                username="admin",
                email="admin@hospital.com",
                password="admin123"
            )
            self.stdout.write(f"  Created admin user: {admin_user.username}")
        else:
            self.stdout.write("  Admin user already exists")

    def create_users_and_patients(self):
        """Create sample users and patients"""
        self.stdout.write("Creating users and patients...")
        patients = []
        
        patient_data = [
            {"username": "patient1", "email": "patient1@example.com", "ho_ten": "Nguyen Van A", 
             "ngay_sinh": "1990-01-15", "gioi_tinh": "Nam", "cmnd_cccd": "123456789012", 
             "so_dien_thoai": "0123456789", "dia_chi": "123 Main St, Ho Chi Minh City"},
            {"username": "patient2", "email": "patient2@example.com", "ho_ten": "Tran Thi B", 
             "ngay_sinh": "1985-05-20", "gioi_tinh": "Nu", "cmnd_cccd": "123456789013", 
             "so_dien_thoai": "0123456790", "dia_chi": "456 Oak Ave, Hanoi"},
            {"username": "patient3", "email": "patient3@example.com", "ho_ten": "Le Van C", 
             "ngay_sinh": "1992-08-10", "gioi_tinh": "Nam", "cmnd_cccd": "123456789014", 
             "so_dien_thoai": "0123456791", "dia_chi": "789 Pine Rd, Da Nang"},
        ]
        
        for data in patient_data:
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password="password123"
            )
            
            patient = BenhNhan.objects.create(
                ma_nguoi_dung=user,
                ho_ten=data["ho_ten"],
                ngay_sinh=datetime.strptime(data["ngay_sinh"], "%Y-%m-%d").date(),
                gioi_tinh=data["gioi_tinh"],
                cmnd_cccd=data["cmnd_cccd"],
                so_dien_thoai=data["so_dien_thoai"],
                email=data["email"],
                dia_chi=data["dia_chi"]
            )
            patients.append(patient)
            self.stdout.write(f"  Created patient: {patient.ho_ten}")
        
        return patients

    def create_medical_facilities(self):
        """Create sample medical facilities"""
        self.stdout.write("Creating medical facilities...")
        facilities = []
        
        facility_data = [
            {"ten_co_so": "Benh vien Bach Mai", "dia_chi": "78 Giai Phong, Hanoi", 
             "so_dien_thoai": "0243-8692595", "email": "info@bachmai.gov.vn"},
            {"ten_co_so": "Benh vien Cho Ray", "dia_chi": "201B Nguyen Chi Thanh, Ho Chi Minh City", 
             "so_dien_thoai": "028-38553301", "email": "info@choray.vn"},
        ]
        
        for data in facility_data:
            facility = CoSoYTe.objects.create(**data)
            facilities.append(facility)
            self.stdout.write(f"  Created facility: {facility.ten_co_so}")
        
        return facilities

    def create_specialties(self, facilities):
        """Create medical specialties"""
        self.stdout.write("Creating specialties...")
        specialties = []
        
        specialty_names = ["Tim mach", "Noi khoa", "Ngoai khoa", "San phu khoa", "Nhi khoa"]
        
        for facility in facilities:
            for name in specialty_names:
                specialty = ChuyenKhoa.objects.create(
                    ma_co_so=facility,
                    ten_chuyen_khoa=name,
                    mo_ta=f"Chuyen khoa {name} tai {facility.ten_co_so}"
                )
                specialties.append(specialty)
                self.stdout.write(f"  Created specialty: {specialty.ten_chuyen_khoa} at {facility.ten_co_so}")
        
        return specialties

    def create_doctors(self, facilities, specialties):
        """Create sample doctors"""
        self.stdout.write("Creating doctors...")
        doctors = []
        
        doctor_data = [
            {"username": "doctor1", "email": "doctor1@hospital.com", "ho_ten": "Dr. Pham Van D", 
             "gioi_tinh": "Nam", "hoc_vi": "Tien si", "kinh_nghiem": 10},
            {"username": "doctor2", "email": "doctor2@hospital.com", "ho_ten": "Dr. Hoang Thi E", 
             "gioi_tinh": "Nu", "hoc_vi": "Thac si", "kinh_nghiem": 8},
            {"username": "doctor3", "email": "doctor3@hospital.com", "ho_ten": "Dr. Vu Van F", 
             "gioi_tinh": "Nam", "hoc_vi": "Tien si", "kinh_nghiem": 15},
        ]
        
        for i, data in enumerate(doctor_data):
            user = User.objects.create_user(
                username=data["username"],
                email=data["email"],
                password="password123"
            )
            
            facility = facilities[i % len(facilities)]
            specialty = specialties[i % len(specialties)]
            
            doctor = BacSi.objects.create(
                ma_nguoi_dung=user,
                ma_co_so=facility,
                ma_chuyen_khoa=specialty,
                ho_ten=data["ho_ten"],
                gioi_tinh=data["gioi_tinh"],
                hoc_vi=data["hoc_vi"],
                kinh_nghiem=data["kinh_nghiem"],
                gioi_thieu=f"Bac si chuyen khoa {specialty.ten_chuyen_khoa}"
            )
            doctors.append(doctor)
            self.stdout.write(f"  Created doctor: {doctor.ho_ten}")
        
        return doctors

    def create_services(self, facilities):
        """Create medical services"""
        self.stdout.write("Creating services...")
        services = []
        
        service_data = [
            {"ten_dich_vu": "Kham tong quat", "gia_tien": Decimal("200000"), 
             "mo_ta": "Kham suc khoe tong quat"},
            {"ten_dich_vu": "Sieu am", "gia_tien": Decimal("300000"), 
             "mo_ta": "Chup sieu am"},
            {"ten_dich_vu": "Xet nghiem mau", "gia_tien": Decimal("150000"), 
             "mo_ta": "Xet nghiem mau co ban"},
        ]
        
        for facility in facilities:
            for data in service_data:
                service = DichVu.objects.create(
                    ma_co_so=facility,
                    **data
                )
                services.append(service)
                self.stdout.write(f"  Created service: {service.ten_dich_vu}")
        
        return services

    def create_work_schedules(self, doctors):
        """Create work schedules for doctors"""
        self.stdout.write("Creating work schedules...")
        schedules = []
        
        for doctor in doctors:
            # Create 5 work schedules for each doctor
            for i in range(5):
                work_date = datetime.now().date() + timedelta(days=random.randint(1, 15))
                start_time = datetime.strptime(f"{8 + i % 4}:00", "%H:%M").time()
                end_time = datetime.strptime(f"{12 + i % 4}:00", "%H:%M").time()
                
                try:
                    schedule = LichLamViec.objects.create(
                        ma_bac_si=doctor,
                        ngay_lam_viec=work_date,
                        gio_bat_dau=start_time,
                        gio_ket_thuc=end_time,
                        so_luong_kham=random.randint(10, 20),
                        so_luong_da_dat=0
                    )
                    schedules.append(schedule)
                except:
                    continue
        
        self.stdout.write(f"  Created {len(schedules)} work schedules")
        return schedules

    def create_appointments(self, patients, doctors, services, schedules):
        """Create sample appointments"""
        self.stdout.write("Creating appointments...")
        appointments = []
        
        for i in range(5):
            patient = random.choice(patients)
            doctor = random.choice(doctors)
            service = random.choice(services)
            
            # Find a schedule for this doctor
            doctor_schedules = [s for s in schedules if s.ma_bac_si == doctor and s.con_cho_trong > 0]
            if not doctor_schedules:
                continue
                
            schedule = random.choice(doctor_schedules)
            
            appointment = LichHen.objects.create(
                ma_benh_nhan=patient,
                ma_bac_si=doctor,
                ma_dich_vu=service,
                ma_lich=schedule,
                ngay_kham=schedule.ngay_lam_viec,
                gio_kham=schedule.gio_bat_dau,
                so_thu_tu=schedule.so_luong_da_dat + 1,
                trang_thai=random.choice(["Cho xac nhan", "Da xac nhan", "Hoan thanh"]),
                ghi_chu=f"Regular checkup - Appointment {i+1}"
            )
            
            # Update schedule booking count
            schedule.so_luong_da_dat += 1
            schedule.save()
            
            appointments.append(appointment)
            self.stdout.write(f"  Created appointment: {appointment.ma_lich_hen}")
        
        return appointments

    def create_telemedicine_sessions(self, appointments):
        """Create telemedicine sessions for some appointments"""
        self.stdout.write("Creating telemedicine sessions...")
        sessions = []
        
        completed_appointments = [a for a in appointments if a.trang_thai == "Hoan thanh"]
        
        for appointment in completed_appointments[:2]:
            session = PhienTuVanTuXa.objects.create(
                ma_lich_hen=appointment,
                ma_cuoc_goi=f"CALL{random.randint(10000, 99999)}",
                thoi_gian_bat_dau=datetime.now() - timedelta(days=random.randint(1, 5)),
                thoi_gian_ket_thuc=datetime.now() - timedelta(days=random.randint(0, 4)),
                trang_thai="Da ket thuc",
                ghi_chu_bac_si="Telemedicine session completed successfully"
            )
            sessions.append(session)
            self.stdout.write(f"  Created telemedicine session for appointment: {appointment.ma_lich_hen}")
        
        return sessions

    def create_payments(self, appointments):
        """Create payments for appointments"""
        self.stdout.write("Creating payments...")
        payments = []
        
        for appointment in appointments:
            if appointment.trang_thai in ["Hoan thanh", "Da xac nhan"]:
                total = appointment.ma_dich_vu.gia_tien + Decimal("200000")  # Service + Doctor fee
                
                payment = ThanhToan.objects.create(
                    ma_thanh_toan=f"TT{str(len(payments)+1).zfill(4)}",
                    lich_hen=appointment,
                    so_tien=total,
                    phuong_thuc=random.choice(["Tiền mặt", "Chuyển khoản", "Thẻ tín dụng"]),
                    trang_thai="Đã thanh toán" if appointment.trang_thai == "Hoan thanh" else "Chưa thanh toán",
                    ngay_thanh_toan=datetime.now() - timedelta(days=random.randint(0, 10)) if appointment.trang_thai == "Hoan thanh" else None,
                    ghi_chu="Payment processed successfully" if appointment.trang_thai == "Hoan thanh" else "Pending payment"
                )
                payments.append(payment)
                self.stdout.write(f"  Created payment: {payment.ma_thanh_toan} - Amount: {payment.so_tien}")
        
        return payments
