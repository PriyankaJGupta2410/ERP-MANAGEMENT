from flask import request, Blueprint , jsonify , json
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash,check_password_hash
from connector import db,conn
from decorator import authentication
import json
import random
import string
import uuid


load_dotenv()
admission_bp = Blueprint('admission',__name__)

######################################### STUDENT ADMISSION API ##################################
def generate_random_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

@admission_bp.route('/admission', methods=['POST'])
def post_admission():
    message = ""
    res_data = {}
    status = "fail"
    code = 500

    try:
        if 'metadata' not in request.form or 'photo' not in request.files or 'signature' not in request.files:
            return jsonify({"status": "fail", "message": "Missing metadata or required files"}), 400

        metadata = json.loads(request.form['metadata'])

        personal_info = metadata.get("personal_info", {})
        current_address = metadata.get("current_address", {})
        permanent_address = metadata.get("permanent_address", {})
        admission_info = metadata.get("admission_info", {})
        banking_info = metadata.get("banking_info", {})
        academic_info = metadata.get("academic_info", {})
        qualifying_exam = metadata.get("qualifying_exam", {})

        photo_data = request.files['photo'].read()
        photo_name = secure_filename(request.files['photo'].filename)

        signature_data = request.files['signature'].read()
        signature_name = secure_filename(request.files['signature'].filename)

        doc_blobs = []
        if 'documents' in request.files:
            for doc in request.files.getlist('documents'):
                doc_blobs.append({
                    "filename": secure_filename(doc.filename),
                    "data": doc.read()
                })

        admission_id = str(uuid.uuid4())

        db.execute("""
            INSERT INTO admission_master (
                _id, first_name, middle_name, last_name, email, mobile_number,
                gender, religion, dob, birth_place, nationality,
                disability, domicile_state, aadhar_no, mother_name,
                mother_tongue, locality, blood_group, guardian_mobile,
                mother_mobile, earning_parent_income, earning_parent_pan,
                admission_category, caste_category, caste_subcaste,
                caste_validity_no, eligibility_no, general_reg_no,
                bank_name, branch, account_no, ifsc_code, micr_code,
                last_institute_name, upisc_code, migration_cert_no, lc_tc_no,
                exam, exam_body, passing_month_year, obtained_marks,
                out_of_marks, percentage,
                photo_name, photo_data, signature_name, signature_data,
                extra_docs,
                current_address, permanent_address
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            admission_id,
            personal_info.get("first_name"),
            personal_info.get("middle_name"),
            personal_info.get("last_name"),
            personal_info.get("email"),
            personal_info.get("mobile_number"),
            personal_info.get("gender"),
            personal_info.get("religion"),
            personal_info.get("dob"),
            personal_info.get("birth_place"),
            personal_info.get("nationality"),
            personal_info.get("disability"),
            personal_info.get("domicile_state"),
            personal_info.get("aadhar_no"),
            personal_info.get("mother_name"),
            personal_info.get("mother_tongue"),
            personal_info.get("locality"),
            personal_info.get("blood_group"),
            personal_info.get("guardian_mobile"),
            personal_info.get("mother_mobile"),
            personal_info.get("earning_parent_income"),
            personal_info.get("earning_parent_pan"),
            admission_info.get("admission_category"),
            admission_info.get("caste_category"),
            admission_info.get("caste_subcaste"),
            admission_info.get("caste_validity_no"),
            admission_info.get("eligibility_no"),
            admission_info.get("general_reg_no"),
            banking_info.get("bank_name"),
            banking_info.get("branch"),
            banking_info.get("account_no"),
            banking_info.get("ifsc_code"),
            banking_info.get("micr_code"),
            academic_info.get("last_institute_name"),
            academic_info.get("upisc_code"),
            academic_info.get("migration_cert_no"),
            academic_info.get("lc_tc_no"),
            qualifying_exam.get("exam"),
            qualifying_exam.get("exam_body"),
            qualifying_exam.get("passing_month_year"),
            qualifying_exam.get("obtained_marks"),
            qualifying_exam.get("out_of_marks"),
            qualifying_exam.get("percentage"),
            photo_name, photo_data,
            signature_name, signature_data,
            json.dumps([d["filename"] for d in doc_blobs]),
            json.dumps(current_address),
            json.dumps(permanent_address)
        ))


        conn.commit()
        status = "success"
        code = 200
        message = "Admission, parent and student records created successfully"
        res_data = {
            "admission_id": admission_id
        }

    except Exception as ex:
        conn.rollback()
        message = f"Error: {str(ex)}"
        code = 500

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@admission_bp.route('/ParentStudentOnboard', methods=['POST'])
def ParentStudentOnboard():
    message = ""
    res_data = {}
    status = "fail"
    code = 500

    try:
        data = request.json

        required_fields = [
            'parent_username', 'parent_email', 'parent_mobile', 'parent_address', 'parent_password',
            'student_username', 'student_email', 'student_mobile', 'student_dob', 'student_class', 'student_section', 'student_password'
        ]

        missing = [field for field in required_fields if field not in data]
        if missing:
            message = f"Missing fields: {', '.join(missing)}"
            code = 400
            return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

        parent_pw_hash = generate_password_hash(data['parent_password'])
        student_pw_hash = generate_password_hash(data['student_password'])

        db.execute("""
            INSERT INTO user_master (_id, role, username, email, password, contact)
            VALUES (UUID(), %s, %s, %s, %s, %s)
        """, ('parent', data['parent_username'], data['parent_email'], parent_pw_hash, data['parent_mobile']))
        conn.commit()
        db.execute("SELECT _id FROM user_master WHERE email=%s", (data['parent_email'],))
        parent_user_id = db.fetchone()[0]

        address_json = json.dumps({"full_address": data['parent_address']})
        db.execute("""
            INSERT INTO parent_master (_id, user_id, address)
            VALUES (UUID(), %s, %s)
        """, (parent_user_id, address_json))
        conn.commit()
        db.execute("SELECT _id FROM parent_master WHERE user_id=%s", (parent_user_id,))
        parent_id = db.fetchone()[0]

        db.execute("""
            INSERT INTO user_master (_id, role, username, email, password, contact)
            VALUES (UUID(), %s, %s, %s, %s, %s)
        """, ('student', data['student_username'], data['student_email'], student_pw_hash, data['student_mobile']))
        conn.commit()
        db.execute("SELECT _id FROM user_master WHERE email=%s", (data['student_email'],))
        student_user_id = db.fetchone()[0]

        db.execute("""
            INSERT INTO student_master (_id, user_id, parent_id, dob, class_name, section)
            VALUES (UUID(), %s, %s, %s, %s, %s)
        """, (
            student_user_id,
            parent_id,
            data['student_dob'],
            data['student_class'],
            data['student_section']
        ))
        conn.commit()

        status = "success"
        code = 201
        message = "Parent and student onboarded successfully"
        res_data = {
            "parent_user_id": parent_user_id,
            "parent_id": parent_id,
            "student_user_id": student_user_id
        }

    except Exception as ex:
        conn.rollback()
        message = f"Error: {str(ex)}"
        code = 500

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })