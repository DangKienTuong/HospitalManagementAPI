-- ===============================================
-- Hospital Management System Database Setup Script
-- For SQL Server (MSSQL)
-- ===============================================
-- This script can be executed multiple times without errors
-- It will drop and recreate the database with fresh test data

USE master;
GO

-- Drop existing connections to the database
IF EXISTS (SELECT * FROM sys.databases WHERE name = 'He_thong_Dat_lich_kham_benh')
BEGIN
    ALTER DATABASE He_thong_Dat_lich_kham_benh SET SINGLE_USER WITH ROLLBACK IMMEDIATE;
    DROP DATABASE He_thong_Dat_lich_kham_benh;
END
GO

-- Create the database
CREATE DATABASE He_thong_Dat_lich_kham_benh;
GO

USE He_thong_Dat_lich_kham_benh;
GO

-- ===============================================
-- Note: Django will create the Nguoi_dung table through migrations
-- We don't create it here to avoid conflicts
-- ===============================================

-- ===============================================
-- Note: Django will create ALL tables through migrations
-- We don't create any tables here to avoid conflicts
-- ===============================================

-- ===============================================
-- Note: Django will create its own system tables
-- (auth_group, auth_permission, django_content_type, etc.)
-- during migration process. We only create application tables here.
-- ===============================================

-- ===============================================
-- Note: All data will be inserted after Django migrations
-- This is handled in the separate create_test_users.sql script
-- ===============================================

PRINT '===============================================';
PRINT 'Database setup completed successfully!';
PRINT '===============================================';
PRINT '';
PRINT 'Summary of created objects:';
PRINT '- Database: He_thong_Dat_lich_kham_benh';
PRINT '- Tables: 0 (Django will create all tables through migrations)';
PRINT '- Data: 0 (All data will be inserted after migrations)';
PRINT '';
PRINT 'Note: All tables and data will be created through Django migrations';
PRINT 'and the separate create_test_users.sql script.';
PRINT '';
PRINT 'Next steps:';
PRINT '1. Run Django migrations: python manage.py migrate';
PRINT '2. Create superuser: python manage.py createsuperuser';
PRINT '3. Create test users through Django admin or management commands';
PRINT '';
PRINT 'You can now run this script multiple times without errors.';
PRINT '===============================================';
GO
