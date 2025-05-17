-- Step 1: 创建 employees 表数据 (test1 - test5)
INSERT INTO employees (employee_id, name, department, level, status)
VALUES
    ('test1', 'Test User 1', 'Development', 1, 0),
    ('test2', 'Test User 2', 'Development', 2, 0),
    ('test3', 'Test User 3', 'Development', 3, 0),
    ('test4', 'Test User 4', 'Development', 4, 0),
    ('test5', 'Test User 5', 'Development', 5, 0)
ON CONFLICT (employee_id) DO NOTHING;

-- Step 2: 创建 users 表数据 (test1 - test5)
-- 使用明文密码 test1-test5
INSERT INTO users (employee_id, hashed_password, permissions, status)
SELECT 
    employee_id,
    'test' || substring(employee_id from 5)::text AS hashed_password, -- 明文密码
    0 AS permissions,
    0 AS status
FROM employees
WHERE employee_id IN ('test1', 'test2', 'test3', 'test4', 'test5')
ON CONFLICT (employee_id) DO NOTHING;

--Step 3: 创建 software_info 表数据
INSERT INTO software_info (SoftwareInfoName, SoftwareInfoType, SoftwareInfoMatchRule) VALUES
('Microsoft Office', 1, 'Office suite for productivity'),
('Adobe Photoshop', 3, 'Professional image editing software'),
('Visual Studio Code', 2, 'Open-source code editor'),
('Google Chrome', 0, 'Web browser developed by Google'),
('IntelliJ IDEA', 2, 'Java IDE with advanced features'),
('AutoCAD', 3, 'Computer-aided design software'),
('Slack', 5, 'Team collaboration and messaging platform'),
('Zoom', 5, 'Video conferencing tool'),
('Spotify', 4, 'Music streaming service'),
('Trello', 5, 'Project management tool'),
('GitHub Desktop', 2, 'GUI client for GitHub repositories'),
('Docker', 2, 'Containerization platform'),
('Postman', 2, 'API development and testing tool'),
('Figma', 3, 'Collaborative interface design tool'),
('Notion', 5, 'Note-taking and project management tool'),
('PyCharm', 2, 'Python-focused IDE'),
('JetBrains Rider', 2, 'Cross-platform .NET IDE'),
('VLC Media Player', 4, 'Free media player for various formats'),
('Discord', 5, 'Voice and text communication app'),
('Toggl Track', 5, 'Time tracking and project management'),
('Jira', 5, 'Issue and project tracking tool'),
('Confluence', 5, 'Collaborative documentation platform'),
('Unity Hub', 3, 'Game engine for creating interactive content'),
('Blender', 3, 'Open-source 3D computer graphics software'),
('Eclipse', 2, 'Java-based integrated development environment'),
('Wireshark', 2, 'Network protocol analyzer'),
('MySQL Workbench', 2, 'Database design and modeling tool'),
('GIMP', 3, 'GNU Image Manipulation Program'),
('Inkscape', 3, 'Vector graphics editor'),
('LibreOffice', 1, 'Open-source office suite'),
('Audacity', 4, 'Audio recording and editing software'),
('Android Studio', 2, 'Official IDE for Android app development'),
('Sublime Text', 2, 'Sophisticated text editor for code'),
('FileZilla', 5, 'FTP client for file transfers'),
('Krita', 3, 'Digital painting and animation tool'),
('Apache NetBeans', 2, 'Java IDE and platform'),
('Vim', 2, 'Highly configurable text editor'),
('GIMP', 3, 'GNU Image Manipulation Program'),
('Audacity', 4, 'Audio recording and editing software'),
('Android Studio', 2, 'Official IDE for Android app development'),
('Sublime Text', 2, 'Sophisticated text editor for code'),
('FileZilla', 5, 'FTP client for file transfers'),
('Krita', 3, 'Digital painting and animation tool'),
('Apache NetBeans', 2, 'Java IDE and platform'),
('Vim', 2, 'Highly configurable text editor'),
('Godot Engine', 3, 'Open source game engine'),
('Wireshark', 2, 'Network protocol analyzer'),
('VSFTPD', 5, 'Very Secure FTP Daemon');

-- Step 4: 插入 software_license 数据
DO $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..50 LOOP
        INSERT INTO software_license (
            SoftwareInfoID,
            LicenseType,
            LicenseStatus,
            LicenseKey,
            LicenseExpiredDate,
            LvLimit,
            Remark
        ) VALUES (
            i,
            FLOOR(RANDOM() * 3), -- 0: monthly, 1: yearly, 2: perpetual
            0, -- available
            MD5(random()::text),
            CASE WHEN FLOOR(RANDOM() * 3) = 2 THEN NULL ELSE NOW() + (RANDOM() * INTERVAL '10 years') END,
            FLOOR(RANDOM() * 6), -- Lv limit between 0-5
            'License for demo'
        );
    END LOOP;
END $$;

-- Step 5: 插入 licenses_usage_record 数据
DO $$
DECLARE
    user_id INT;
    license_id INT;
    checkout_time TIMESTAMP;
    duration_days INT;
    return_time TIMESTAMP;
BEGIN
    FOR license_id IN 1..50 LOOP
        user_id := ((license_id - 1) % 5) + 1; -- test1=1, test2=2,... test5=5
        checkout_time := NOW() - (RANDOM() * INTERVAL '30 days');
        duration_days := 7 + (RANDOM() * 30)::INT;
        return_time := checkout_time + duration_days * INTERVAL '1 day';

        IF user_id = 1 AND (license_id = 1 OR license_id = 2) THEN
            return_time := NOW() + (RANDOM() * 7)::INT * INTERVAL '1 day';
        END IF;

        INSERT INTO licenses_usage_record (
            LicenseID,
            UserID,
            Checkout_time,
            Duration_Days,
            Return_Time,
            is_expired,
            Actually_Return_Time
        ) VALUES (
            license_id,
            user_id,
            checkout_time,
            duration_days,
            return_time,
            FALSE,
            NULL
        );
    END LOOP;
END $$;