CREATE TABLE admission_master (
    _id VARCHAR(36) PRIMARY KEY,
    first_name VARCHAR(100),
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(150),
    mobile_number VARCHAR(20),
    gender VARCHAR(10),
    religion VARCHAR(50),
    dob DATE,
    birth_place VARCHAR(100),
    nationality VARCHAR(50),
    disability VARCHAR(50),
    domicile_state VARCHAR(100),
    aadhar_no VARCHAR(20),
    mother_name VARCHAR(100),
    mother_tongue VARCHAR(50),
    locality VARCHAR(100),
    blood_group VARCHAR(10),
    guardian_mobile VARCHAR(20),
    mother_mobile VARCHAR(20),
    earning_parent_income VARCHAR(100),
    earning_parent_pan VARCHAR(20),
    admission_category VARCHAR(50),
    caste_category VARCHAR(50),
    caste_subcaste VARCHAR(50),
    caste_validity_no VARCHAR(50),
    eligibility_no VARCHAR(50),
    general_reg_no VARCHAR(50),
    bank_name VARCHAR(100),
    branch VARCHAR(100),
    account_no VARCHAR(30),
    ifsc_code VARCHAR(20),
    micr_code VARCHAR(20),
    last_institute_name VARCHAR(150),
    upisc_code VARCHAR(50),
    migration_cert_no VARCHAR(50),
    lc_tc_no VARCHAR(50),
    exam VARCHAR(100),
    exam_body VARCHAR(100),
    passing_month_year VARCHAR(50),
    obtained_marks VARCHAR(20),
    out_of_marks VARCHAR(20),
    percentage VARCHAR(10),
    photo_name VARCHAR(255),
    photo_data LONGBLOB,
    signature_name VARCHAR(255),
    signature_data LONGBLOB,
    extra_docs TEXT,
    current_address JSON,
    permanent_address JSON,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, 
);


CREATE TABLE user_master (
    _id CHAR(36) PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    email VARCHAR(100),
    password TEXT,
    contact VARCHAR(20),
    role TEXT,  -- multiple roles as comma-separated values e.g., 'student,parent'
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    login_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- CREATE TABLE usermaster (
--     _id CHAR(36) PRIMARY KEY,
--     username VARCHAR(100) NOT NULL,
--     email VARCHAR(100) NOT NULL UNIQUE,
--     password TEXT NOT NULL,
--     role VARCHAR(50) NOT NULL,
--     contact VARCHAR(15) NOT NULL,
--     created_date DATETIME NOT NULL
-- );

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


CREATE TABLE school_master (
    _id CHAR(36) PRIMARY KEY,
    superadmin_id CHAR(36) NOT NULL,
    about_us TEXT NOT NULL,
    infrastructure TEXT NOT NULL,
    latest_news TEXT NOT NULL,
    gallery TEXT NOT NULL,
    contact_us TEXT NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (superadmin_id) REFERENCES user_master(_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
