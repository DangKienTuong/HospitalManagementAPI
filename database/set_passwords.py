"""
Script to set proper Django hashed passwords for test users
Run this after executing create_test_users.sql:
    python manage.py shell < database/set_passwords.py
"""

from authentication.models import NguoiDung

# Default password for all test users
DEFAULT_PASSWORD = 'password123'

# List of all test user phone numbers
test_users = [
    # Admin users
    '0901111111',
    '0901111112',
    # Doctor users
    '0902222221',
    '0902222222',
    '0902222223',
    '0902222224',
    '0902222225',
    '0902222226',
    '0902222227',
    '0902222228',
    # Patient users
    '0903333331',
    '0903333332',
    '0903333333',
    '0903333334',
    '0903333335',
    '0903333336',
    '0903333337',
    '0903333338',
    '0903333339',
    '0903333340',
    '0903333341',
    '0903333342',
    # Staff users
    '0904444441',
    '0904444442',
    '0904444443',
]

# Set passwords for all test users
success_count = 0
error_count = 0

for phone in test_users:
    try:
        user = NguoiDung.objects.get(so_dien_thoai=phone)
        user.set_password(DEFAULT_PASSWORD)
        user.save()
        print(f"✓ Password set for {phone} ({user.vai_tro})")
        success_count += 1
    except NguoiDung.DoesNotExist:
        print(f"✗ User not found: {phone}")
        error_count += 1
    except Exception as e:
        print(f"✗ Error setting password for {phone}: {e}")
        error_count += 1

print("\n" + "="*50)
print(f"Password update complete!")
print(f"✓ Success: {success_count} users")
if error_count > 0:
    print(f"✗ Errors: {error_count} users")
print(f"Default password: {DEFAULT_PASSWORD}")
print("="*50)
