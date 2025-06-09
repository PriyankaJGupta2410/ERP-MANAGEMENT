CREATE TABLE admission_master (
    _id CHAR(36) PRIMARY KEY,
    
    -- Personal Information
    first_name VARCHAR(100),
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(100),
    mobile_number VARCHAR(15),
    gender VARCHAR(10),
    religion VARCHAR(50),
    dob DATE,
    birth_place VARCHAR(100),
    nationality VARCHAR(50),
    disability VARCHAR(100),
    domicile_state VARCHAR(100),
    aadhar_no VARCHAR(20),
    mother_name VARCHAR(100),
    mother_tongue VARCHAR(50),
    locality VARCHAR(100),
    blood_group VARCHAR(10),
    guardian_mobile VARCHAR(15),
    mother_mobile VARCHAR(15),
    earning_parent_income VARCHAR(20),
    earning_parent_pan VARCHAR(20),

    -- Current Address
    current_line1 VARCHAR(255),
    current_city VARCHAR(100),
    current_state VARCHAR(100),
    current_zip VARCHAR(10),

    -- Permanent Address
    permanent_line1 VARCHAR(255),
    permanent_city VARCHAR(100),
    permanent_state VARCHAR(100),
    permanent_zip VARCHAR(10),

    -- Admission Info
    admission_category VARCHAR(100),
    caste_category VARCHAR(100),
    caste_subcaste VARCHAR(100),
    caste_validity_no VARCHAR(50),
    eligibility_no VARCHAR(50),
    general_reg_no VARCHAR(50),
    course VARCHAR(100),
    academic_year VARCHAR(20),

    -- Banking Info
    bank_name VARCHAR(100),
    branch VARCHAR(100),
    account_no VARCHAR(30),
    ifsc_code VARCHAR(20),
    micr_code VARCHAR(20),

    -- Academic Info
    last_institute_name VARCHAR(255),
    upisc_code VARCHAR(50),
    migration_cert_no VARCHAR(50),
    lc_tc_no VARCHAR(50),

    -- Qualifying Exam Info
    exam VARCHAR(100),
    exam_body VARCHAR(100),
    passing_month_year VARCHAR(20),
    obtained_marks VARCHAR(10),
    out_of_marks VARCHAR(10),
    percentage VARCHAR(10),

    -- File Paths (you may store paths/URLs here)
    photo_path VARCHAR(255),
    signature_path VARCHAR(255),

    -- Fees Info
    tuition_fee DECIMAL(10,2),
    admission_fee DECIMAL(10,2),
    other_fees DECIMAL(10,2),
    total_fees DECIMAL(10,2),

    -- Optional
    created_by INT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);




CREATE TABLE user_master (
    _id CHAR(36) PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(100),
    password TEXT,
    contact VARCHAR(20),
    role TEXT,  -- multiple roles as comma-separated values e.g., 'student,parent'
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    school_id CHAR(36),  -- Foreign key to school_master(_id),
    status VARCHAR(20) DEFAULT 'Active',
    profile_image LONGBLOB,
    login_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE parent_master (
	_id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    address JSON,
    FOREIGN KEY (user_id) REFERENCES user_master(_id),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
);

CREATE TABLE student_master (
    _id CHAR(36) PRIMARY KEY,
    user_id CHAR(36),
    parent_id CHAR(36),
    dob DATE,
    class_name VARCHAR(100),
    section VARCHAR(50),
    FOREIGN KEY (user_id) REFERENCES user_master(_id),
    FOREIGN KEY (parent_id) REFERENCES parent_master(_id),
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
);

CREATE TABLE staff_master (
    _id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    join_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Active',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36),
    FOREIGN KEY (user_id) REFERENCES user_master(_id),
    FOREIGN KEY (created_by) REFERENCES user_master(_id)
);


-- CREATE TABLE school_master (
--     _id CHAR(36) PRIMARY KEY,
--     superadmin_id CHAR(36) NOT NULL,
--     about_us TEXT NOT NULL,
--     infrastructure TEXT NOT NULL,
--     latest_news TEXT NOT NULL,
--     gallery TEXT NOT NULL,
--     contact_us TEXT NOT NULL,
--     created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
--     modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

--     FOREIGN KEY (superadmin_id) REFERENCES user_master(_id)
--         ON DELETE CASCADE
--         ON UPDATE CASCADE
-- );

CREATE TABLE school_master (
    _id VARCHAR(36) PRIMARY KEY,                -- UUID for school ID
    superadmin_id VARCHAR(36) NOT NULL,         -- Foreign key to user_master._id (Superadmin)
    school_name VARCHAR(255) NOT NULL,
    principal_name VARCHAR(255) NOT NULL,
    contact_email VARCHAR(255) NOT NULL,
    contact_phone VARCHAR(20) NOT NULL,
    established_year INT NOT NULL,
    vision TEXT NOT NULL,
    mission TEXT NOT NULL,
    about_us TEXT NOT NULL,
    infrastructure TEXT NOT NULL,
    latest_news TEXT NOT NULL,
    gallery LONGBLOB NOT NULL,                   -- Binary data for images
    contact_us TEXT NOT NULL,
    created_date DATETIME NOT NULL,

    CONSTRAINT fk_superadmin FOREIGN KEY (superadmin_id) REFERENCES user_master(_id)
        ON DELETE CASCADE ON UPDATE CASCADE
);


