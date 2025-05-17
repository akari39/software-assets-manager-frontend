-- SQL Initialization Script

-- Step 1: 创建employees表
CREATE TABLE IF NOT EXISTS employees (
    employee_id VARCHAR NOT NULL,
    name VARCHAR NOT NULL,
    gender INTEGER DEFAULT 0,
    department VARCHAR,
    level INTEGER DEFAULT 1,
    status INTEGER DEFAULT 0,
    PRIMARY KEY (employee_id)
);
CREATE INDEX IF NOT EXISTS idx_employees_employee_id ON employees (employee_id);
CREATE INDEX IF NOT EXISTS idx_employees_name ON employees (name);
CREATE INDEX IF NOT EXISTS idx_employees_gender ON employees (gender);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees (department);
CREATE INDEX IF NOT EXISTS idx_employees_level ON employees (level);
CREATE INDEX IF NOT EXISTS idx_employees_status ON employees (status);

-- Step 2: 创建users表
CREATE TABLE IF NOT EXISTS users (
    user_id SERIAL,
    employee_id VARCHAR NOT NULL,
    permissions INTEGER DEFAULT 0,
    status INTEGER DEFAULT 0,
    hashed_password VARCHAR NOT NULL, -- Password hashing issue ignored as per request
    PRIMARY KEY (user_id),
    CONSTRAINT uq_users_employee_id UNIQUE (employee_id),
    CONSTRAINT fk_users_employee_id
        FOREIGN KEY(employee_id)
        REFERENCES employees(employee_id)
        ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_users_user_id ON users (user_id);
CREATE INDEX IF NOT EXISTS idx_users_employee_id ON users (employee_id);
CREATE INDEX IF NOT EXISTS idx_users_status ON users (status);

-- Step 3: 创建software_info 表
CREATE TABLE IF NOT EXISTS software_info (
    "SoftwareInfoID" SERIAL,
    "SoftwareInfoName" VARCHAR NOT NULL,
    "SoftwareInfoType" INTEGER DEFAULT 0,
    "SoftwareInfoMatchRule" VARCHAR,
    PRIMARY KEY ("SoftwareInfoID")
);

-- Step 4: 创建software_license 表
CREATE TABLE IF NOT EXISTS software_license (
    "LicenseID" SERIAL,
    "SoftwareInfoID" INTEGER NOT NULL,
    "LicenseType" INTEGER NOT NULL,
    "LicenseStatus" INTEGER DEFAULT 0, -- 0: available, 1: occupied, 2: expired/maintenance
    "LicenseKey" VARCHAR(500),
    "LicenseExpiredDate" TIMESTAMP WITH TIME ZONE,
    "LvLimit" INTEGER DEFAULT 0,
    "Remark" VARCHAR,
    "CreateTime" TIMESTAMP WITH TIME ZONE,
    "LastUpdateTime" TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY ("LicenseID"),
    CONSTRAINT fk_software_license_software_info_id
        FOREIGN KEY("SoftwareInfoID")
        REFERENCES software_info("SoftwareInfoID")
        ON DELETE RESTRICT
);
CREATE INDEX IF NOT EXISTS idx_software_license_software_info_id ON software_license ("SoftwareInfoID");

-- Step 5: 创建licenses_usage_record表
CREATE TABLE IF NOT EXISTS licenses_usage_record (
    "RecordID" SERIAL,
    "LicenseID" INTEGER NOT NULL,
    is_expired BOOLEAN DEFAULT FALSE,
    "UserID" INTEGER NOT NULL,
    "Checkout_time" TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "Duration_Days" INTEGER DEFAULT 0,
    "Return_Time" TIMESTAMP WITH TIME ZONE,
    "Actually_Return_Time" TIMESTAMP WITH TIME ZONE,
    PRIMARY KEY ("RecordID"),
    CONSTRAINT fk_licenses_usage_record_license_id
        FOREIGN KEY("LicenseID")
        REFERENCES software_license("LicenseID")
        ON DELETE CASCADE,
    CONSTRAINT fk_licenses_usage_record_user_id
        FOREIGN KEY("UserID")
        REFERENCES users(user_id)
        ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_licenses_usage_record_license_id ON licenses_usage_record ("LicenseID");
CREATE INDEX IF NOT EXISTS idx_licenses_usage_record_user_id ON licenses_usage_record ("UserID");


-- Step 6: 创建 employees 表数据 (test1 - test5)
INSERT INTO employees (employee_id, name, gender, department, level, status)
VALUES
    ('test1', 'Test User 1', 0, 'Development', 1, 0),
    ('test2', 'Test User 2', 2, 'Development', 2, 0),
    ('test3', 'Test User 3', 1, 'Development', 3, 0),
    ('test4', 'Test User 4', 2, 'Development', 4, 0),
    ('test5', 'Test User 5', 1, 'Development', 5, 0)
ON CONFLICT (employee_id) DO NOTHING;

-- Step 7: 创建 users 表数据 (test1 - test5)
-- As requested, password hashing is ignored here. Using a placeholder.
-- In a real scenario, these would be properly hashed.
INSERT INTO users (employee_id, hashed_password, permissions, status)
SELECT
    e.employee_id,
    'placeholder_for_hashed_password_of_' || e.employee_id AS hashed_password,
    0 AS permissions,
    0 AS status
FROM employees e
WHERE e.employee_id IN ('test1', 'test2', 'test3', 'test4', 'test5')
ON CONFLICT (employee_id) DO NOTHING;

--Step 8: 创建 software_info 表数据 (Curated list of 50)
INSERT INTO software_info ("SoftwareInfoName", "SoftwareInfoType", "SoftwareInfoMatchRule") VALUES
('Microsoft Office 365', 1, ' productivity suite subscription'),
('Adobe Photoshop CC', 3, 'image editing subscription'),
('Visual Studio Code', 2, 'source code editor'),
('Google Chrome', 0, 'web browser'),
('IntelliJ IDEA Ultimate', 2, 'Java IDE'),
('AutoCAD 2025', 3, 'CAD software'),
('Slack Standard Plan', 5, 'team collaboration'),
('Zoom Pro', 5, 'video conferencing'),
('Spotify Premium', 4, 'music streaming'),
('Trello Business Class', 5, 'project management'),
('GitHub Desktop', 2, 'Git client'),
('Docker Desktop', 2, 'containerization platform'),
('Postman Pro', 2, 'API platform'),
('Figma Professional', 3, 'collaborative interface design'),
('Notion Plus', 5, 'workspace and note-taking'),
('PyCharm Professional', 2, 'Python IDE'),
('JetBrains Rider', 2, '.NET IDE'),
('VLC Media Player', 4, 'media player'),
('Discord Nitro', 5, 'communication platform'),
('Toggl Track Premium', 5, 'time tracking'),
('Jira Software Cloud', 5, 'issue and project tracking'),
('Confluence Cloud', 5, 'team workspace'),
('Unity Pro', 3, 'game engine'),
('Blender', 3, '3D creation suite'),
('Eclipse IDE for Java Developers', 2, 'Java IDE'),
('Wireshark', 2, 'network protocol analyzer'),
('MySQL Workbench', 2, 'database design tool'),
('GIMP', 3, 'image manipulation program'),
('Inkscape', 3, 'vector graphics editor'),
('LibreOffice Suite', 1, 'office suite'),
('Audacity', 4, 'audio editor and recorder'),
('Android Studio', 2, 'Android app IDE'),
('Sublime Text 4', 2, 'text editor'),
('FileZilla Pro', 5, 'FTP client'),
('Krita', 3, 'digital painting'),
('Apache NetBeans', 2, 'IDE for Java, PHP, etc.'),
('Vim', 2, 'modal text editor'),
('Godot Engine', 3, '2D/3D game engine'),
('OBS Studio', 4, 'streaming and recording'),
('Bitwarden Premium', 5, 'password manager'),
('NordVPN Standard', 5, 'VPN service'),
('Sketch', 3, 'vector graphics editor for macOS'),
('Affinity Designer', 3, 'vector graphics editor'),
('DaVinci Resolve Studio', 4, 'video editing software'),
('Ableton Live Suite', 4, 'digital audio workstation'),
('Microsoft Teams', 1, 'collaboration platform'),
('Salesforce Sales Cloud', 5, 'CRM platform'),
('Tableau Desktop', 5, 'data visualization'),
('MATLAB', 2, 'numerical computing environment'),
('SAP S/4HANA', 5, 'ERP system')
ON CONFLICT ("SoftwareInfoName") DO NOTHING; -- Avoid duplicates if script is run multiple times

-- Step 9: 插入 software_license 数据
DO $$
DECLARE
    arr_software_info_ids INT[];
    s_info_id INT;
    lic_key_prefix TEXT := 'DEMO-LIC-';
    idx INT := 0;
    num_licenses_to_create INT := 50; -- Target number of licenses
BEGIN
    -- Fetch all SoftwareInfoIDs into an array
    SELECT array_agg("SoftwareInfoID") INTO arr_software_info_ids FROM software_info;

    IF array_length(arr_software_info_ids, 1) IS NULL OR array_length(arr_software_info_ids, 1) = 0 THEN
        RAISE NOTICE 'No software_info records found, skipping software_license insertion.';
        RETURN;
    END IF;

    FOR i IN 1..LEAST(num_licenses_to_create, array_length(arr_software_info_ids, 1) * 2) LOOP -- Create up to 2 licenses per software if needed to reach 50
        idx := idx + 1;
        -- Cycle through available SoftwareInfoIDs
        s_info_id := arr_software_info_ids[((idx-1) % array_length(arr_software_info_ids, 1)) + 1];

        INSERT INTO software_license (
            "SoftwareInfoID",
            "LicenseType",
            "LicenseStatus", -- Will be updated by usage record insertion if occupied
            "LicenseKey",
            "LicenseExpiredDate",
            "LvLimit",
            "Remark",
            "CreateTime",
            "LastUpdateTime"
        ) VALUES (
            s_info_id,
            FLOOR(RANDOM() * 3), -- 0: monthly, 1: yearly, 2: perpetual
            0, -- Default to available
            lic_key_prefix || LPAD(idx::TEXT, 4, '0') || '-' || UPPER(SUBSTRING(MD5(random()::text) FOR 8)),
            CASE
                WHEN FLOOR(RANDOM() * 3) = 2 THEN NULL -- Perpetual
                ELSE NOW() - INTERVAL '1 year' + (RANDOM() * INTERVAL '4 years') -- Expires in -1 to +3 years
            END,
            FLOOR(RANDOM() * 6), -- Lv limit between 0-5
            'Demo License ' || idx,
            NOW() - INTERVAL '1 day' * FLOOR(RANDOM() * 365), -- Created within the last year
            NOW() - INTERVAL '1 day' * FLOOR(RANDOM() * 30)   -- Updated within the last month
        );
    END LOOP;
    RAISE NOTICE '% software_license records inserted.', idx;
END $$;

-- Step 10: 插入 licenses_usage_record 数据并更新 software_license 状态
DO $$
DECLARE
    arr_user_ids INT[];
    arr_license_ids_available INT[];
    actual_user_id INT;
    actual_license_id INT;
    checkout_time TIMESTAMP;
    duration_days INT;
    expected_return_time TIMESTAMP;
    actually_ret_time TIMESTAMP;
    is_rec_expired BOOLEAN;
    employee_ids_for_users TEXT[] := ARRAY['test1', 'test2', 'test3', 'test4', 'test5'];
    num_usage_records_to_create INT := 0; -- Will be based on available licenses
    inserted_records_count INT := 0;
BEGIN
    -- Fetch actual user_ids for 'test1' through 'test5'
    SELECT array_agg(u.user_id) INTO arr_user_ids
    FROM users u
    WHERE u.employee_id = ANY(employee_ids_for_users);

    -- Fetch available LicenseIDs (status = 0)
    SELECT array_agg("LicenseID") INTO arr_license_ids_available FROM software_license WHERE "LicenseStatus" = 0;

    IF array_length(arr_user_ids, 1) IS NULL OR array_length(arr_user_ids, 1) = 0 THEN
        RAISE NOTICE 'No test users found, skipping licenses_usage_record insertion.';
        RETURN;
    END IF;

    IF array_length(arr_license_ids_available, 1) IS NULL OR array_length(arr_license_ids_available, 1) = 0 THEN
        RAISE NOTICE 'No available software_license records found, skipping licenses_usage_record insertion.';
        RETURN;
    END IF;

    num_usage_records_to_create := LEAST(30, array_length(arr_license_ids_available, 1)); -- Create up to 30 usage records

    FOR i IN 1..num_usage_records_to_create LOOP
        actual_license_id := arr_license_ids_available[i]; -- Use available license IDs sequentially
        actual_user_id := arr_user_ids[((i-1) % array_length(arr_user_ids, 1)) + 1]; -- Cycle through test users

        checkout_time := NOW() - (RANDOM() * INTERVAL '90 days'); -- Checked out in the last 90 days
        duration_days := 7 + (RANDOM() * 83)::INT; -- Duration from 7 to 90 days
        expected_return_time := checkout_time + duration_days * INTERVAL '1 day';

        IF RANDOM() < 0.3 THEN -- ~30% chance it's still actively checked out (not yet returned)
            actually_ret_time := NULL;
            is_rec_expired := (expected_return_time < NOW()); -- True if expected return time is in the past
            IF NOT is_rec_expired THEN
                UPDATE software_license SET "LicenseStatus" = 1 WHERE "LicenseID" = actual_license_id; -- Mark as occupied
            ELSE
                UPDATE software_license SET "LicenseStatus" = 2 WHERE "LicenseID" = actual_license_id; -- Mark as overdue/expired
            END IF;
        ELSE -- ~70% chance it has been returned
            -- Returned sometime before or on due date, or even a bit late
            actually_ret_time := expected_return_time - (RANDOM() * (duration_days / 2.0) - (duration_days / 4.0)) * INTERVAL '1 day';
            IF actually_ret_time > NOW() THEN -- Ensure actual return time is not in the future
                 actually_ret_time := expected_return_time;
                 IF actually_ret_time > NOW() THEN actually_ret_time := NOW() - INTERVAL '1 hour'; END IF;
            END IF;
            is_rec_expired := TRUE; -- Considered 'expired' in terms of active checkout once returned
            UPDATE software_license SET "LicenseStatus" = 0 WHERE "LicenseID" = actual_license_id; -- Mark as available
        END IF;

        -- Specific scenario from original script for the first test user if they are picked
        IF actual_user_id = arr_user_ids[1] AND (i = 1 OR i = 2) THEN -- If it's user 'test1' and first or second record we are creating for them
             IF actually_ret_time IS NULL THEN -- Only adjust if still 'checked out' in our simulation
                expected_return_time := NOW() + (RANDOM() * 7)::INT * INTERVAL '1 day'; -- Extend return time to near future
                is_rec_expired := FALSE;
                UPDATE software_license SET "LicenseStatus" = 1 WHERE "LicenseID" = actual_license_id; -- Occupied
             END IF;
        END IF;

        INSERT INTO licenses_usage_record (
            "LicenseID",
            "UserID",
            "Checkout_time",
            "Duration_Days",
            "Return_Time", -- This is the expected/planned return time
            is_expired,   -- This flag indicates if the checkout period itself is over or was manually marked
            "Actually_Return_Time"
        ) VALUES (
            actual_license_id,
            actual_user_id,
            checkout_time,
            duration_days,
            expected_return_time,
            is_rec_expired,
            actually_ret_time
        );
        inserted_records_count := inserted_records_count + 1;
    END LOOP;
    RAISE NOTICE '% licenses_usage_record records inserted.', inserted_records_count;
END $$;

COMMIT;

-- End of script