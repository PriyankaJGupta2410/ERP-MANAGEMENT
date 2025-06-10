CREATE TABLE admission_master (
    _id CHAR(36) PRIMARY KEY,
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
    earning_parent_income VARCHAR(50),
    earning_parent_pan VARCHAR(20),
    admission_category VARCHAR(50),
    caste_category VARCHAR(50),
    caste_subcaste VARCHAR(100),
    caste_validity_no VARCHAR(100),
    eligibility_no VARCHAR(100),
    general_reg_no VARCHAR(100),
    bank_name VARCHAR(100),
    branch VARCHAR(100),
    account_no VARCHAR(20),
    ifsc_code VARCHAR(20),
    micr_code VARCHAR(20),
    last_institute_name VARCHAR(150),
    upisc_code VARCHAR(50),
    migration_cert_no VARCHAR(50),
    lc_tc_no VARCHAR(50),
    exam VARCHAR(50),
    exam_body VARCHAR(100),
    passing_month_year VARCHAR(20),
    obtained_marks FLOAT,
    out_of_marks FLOAT,
    percentage FLOAT,
    photo_name VARCHAR(255),
    photo_data LONGBLOB,
    signature_name VARCHAR(255),
    signature_data LONGBLOB,
    current_address TEXT,
    permanent_address TEXT,
    created_by VARCHAR(100),
    created_date DATETIME
);


CREATE TABLE fee_master (
    _id CHAR(36) NOT NULL PRIMARY KEY,
    fee_type VARCHAR(100) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    description TEXT,
    class VARCHAR(20),
    section VARCHAR(10),
    academic_year VARCHAR(20) NOT NULL,
    created_by VARCHAR(36),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE class_master (
    _id CHAR(36) PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    section VARCHAR(10) NOT NULL,
    academic_year VARCHAR(20) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_by VARCHAR(100),
    created_date DATETIME
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
    _id CHAR(36) PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    school_id CHAR(36) NOT NULL,
    salary DECIMAL(10, 2) NOT NULL,
    join_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'Active',
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by CHAR(36),
    FOREIGN KEY (user_id) REFERENCES user_master(_id),
    FOREIGN KEY (created_by) REFERENCES user_master(_id),
    FOREIGN KEY (school_id) REFERENCES school_master(_id)
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


