CREATE TABLE admission_master (
    admission_form_no INT AUTO_INCREMENT PRIMARY KEY,  -- 4-digit auto increment ID
    _id VARCHAR(36) NOT NULL UNIQUE,                   -- UUID
    first_name VARCHAR(100),
    middle_name VARCHAR(100),
    last_name VARCHAR(100),
    email VARCHAR(100),
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
    earning_parent_income VARCHAR(50),
    earning_parent_pan VARCHAR(20),
    admission_category VARCHAR(100),
    caste_category VARCHAR(100),
    caste_subcaste VARCHAR(100),
    caste_validity_no VARCHAR(50),
    eligibility_no VARCHAR(50),
    general_reg_no VARCHAR(50),
    bank_name VARCHAR(100),
    branch VARCHAR(100),
    account_no VARCHAR(50),
    ifsc_code VARCHAR(20),
    micr_code VARCHAR(20),
    last_institute_name VARCHAR(150),
    upisc_code VARCHAR(20),
    migration_cert_no VARCHAR(50),
    lc_tc_no VARCHAR(50),
    exam VARCHAR(50),
    exam_body VARCHAR(100),
    passing_month_year VARCHAR(20),
    obtained_marks DECIMAL(10,2),
    out_of_marks DECIMAL(10,2),
    percentage DECIMAL(5,2),
    photo_data LONGBLOB,
    signature_data LONGBLOB,
    status VARCHAR(20) DEFAULT 'Pending',
    current_address TEXT,
    permanent_address TEXT,
    created_by VARCHAR(36),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP

) AUTO_INCREMENT = 1000;



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
    user_id CHAR(36) NOT NULL,
    student_id CHAR(36) NOT NULL,
    occupation VARCHAR(100),
    relation VARCHAR(50),
    address TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_by CHAR(36),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,

	FOREIGN KEY (user_id) REFERENCES user_master(_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

	FOREIGN KEY (student_id) REFERENCES student_master(_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    FOREIGN KEY (created_by) REFERENCES user_master(_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);



CREATE TABLE student_master (
    _id CHAR(36) PRIMARY KEY,
    admission_id CHAR(36),
    user_id CHAR(36),
    class_id VARCHAR(50),
    roll_number VARCHAR(20),
    academic_year VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_by CHAR(36),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_admission FOREIGN KEY (admission_id) REFERENCES admission_master(_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES user_master(_id)
        ON DELETE CASCADE ON UPDATE CASCADE,

    CONSTRAINT fk_creator FOREIGN KEY (created_by) REFERENCES user_master(_id)
        ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE role_master (
    _id CHAR(36) PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,     -- e.g., 'teacher', 'admin'
    role VARCHAR(100) NOT NULL,                -- Display name, e.g., 'Teacher', 'Admin'
    description TEXT,                          -- Optional role description
    type VARCHAR(20) NOT NULL,                 -- 'teaching' or 'non-teaching'
    status VARCHAR(20) DEFAULT 'active',       -- 'active' or 'inactive'
    user_id CHAR(36),                          -- Created by user (foreign key to user_master)
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    modified_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE file_uploads (
    _id CHAR(36) PRIMARY KEY,  -- UUID
    file_name VARCHAR(255),
    file_type VARCHAR(100),
    file_data LONGBLOB,           -- To store binary file data
    uploaded_by CHAR(36),      -- Foreign key to users table (optional, depends on your schema)
    created_date DATETIME
);

CREATE TABLE subject_master (
    _id VARCHAR(36) PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    subject_code VARCHAR(50) NOT NULL,
    description TEXT,
    class_id VARCHAR(36) NOT NULL,
    created_by VARCHAR(36),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
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

CREATE TABLE class_teacher_master (
    _id VARCHAR(50) PRIMARY KEY,
    class_id VARCHAR(50) NOT NULL,
    teacher_id VARCHAR(50) NOT NULL,
    created_by VARCHAR(50),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    modified_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES class_master(_id),
    FOREIGN KEY (teacher_id) REFERENCES staff_master(_id),
    FOREIGN KEY (created_by) REFERENCES user_master(_id)
);
CREATE TABLE Subject_Assigned_Master (
    _id VARCHAR(50) PRIMARY KEY,
    teacher_id VARCHAR(50) NOT NULL,
    class_id VARCHAR(50) NOT NULL,
    subject_id VARCHAR(50) NOT NULL,
    created_by VARCHAR(50),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES staff_master(_id),
    FOREIGN KEY (class_id) REFERENCES class_master(_id),
    FOREIGN KEY (subject_id) REFERENCES subject_master(_id),
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

########################### STORE MODULE ############################
CREATE TABLE ItemCategory (
    _id CHAR(36) PRIMARY KEY,
    name VARCHAR(50),
    description TEXT
);

CREATE TABLE Item (
    _id CHAR(36) PRIMARY KEY,
    name VARCHAR(100),
    category_id CHAR(36),
    quantity INT,
    unit VARCHAR(20),
    min_stock_alert INT,
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES ItemCategory(_id)
);

CREATE TABLE StockTransaction (
    _id CHAR(36) PRIMARY KEY,
    item_id CHAR(36),
    transaction_date DATE,
    transaction_type ENUM('ISSUE', 'RETURN'),
    quantity INT,
    issued_to VARCHAR(50),
    returned_by VARCHAR(50),
    remarks TEXT,
    FOREIGN KEY (item_id) REFERENCES Item(_id)
);


