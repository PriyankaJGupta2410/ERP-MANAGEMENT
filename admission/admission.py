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
from datetime import datetime
import base64
import logging
from werkzeug.exceptions import BadRequest
import json


load_dotenv()
admission_bp = Blueprint('admission',__name__)

######################################### STUDENT ADMISSION API ##################################

@admission_bp.route('/POSTadmission', methods=['POST'])
@authentication
def POSTadmission(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        print("1")
        metadata = request.form.get("data")
        data = json.loads(metadata) if metadata else {}

        student_photo = request.files.get("photo")
        student_signature = request.files.get("signature")

        admission_id = str(uuid.uuid4())
        created_date = datetime.now()

        photo_data = student_photo.read() if student_photo else None
        signature_data = student_signature.read() if student_signature else None

        query = """
            INSERT INTO admission_master (
                _id, first_name, middle_name, last_name, email, mobile_number,
                gender, religion, dob, birth_place, nationality, disability,
                domicile_state, aadhar_no, mother_name, mother_tongue, locality,
                blood_group, guardian_mobile, mother_mobile, earning_parent_income,
                earning_parent_pan, admission_category, caste_category, caste_subcaste,
                caste_validity_no, eligibility_no, general_reg_no, bank_name, branch,
                account_no, ifsc_code, micr_code, last_institute_name, upisc_code,
                migration_cert_no, lc_tc_no, exam, exam_body, passing_month_year,
                obtained_marks, out_of_marks, percentage, photo_data, signature_data,
                current_address, permanent_address, created_by, created_date
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """

        values = (
            admission_id, data.get("first_name"), data.get("middle_name"),
            data.get("last_name"), data.get("email"), data.get("mobile_number"),
            data.get("gender"), data.get("religion"), data.get("dob"), data.get("birth_place"),
            data.get("nationality"), data.get("disability"), data.get("domicile_state"),
            data.get("aadhar_no"), data.get("mother_name"), data.get("mother_tongue"),
            data.get("locality"), data.get("blood_group"), data.get("guardian_mobile"),
            data.get("mother_mobile"), data.get("earning_parent_income"),
            data.get("earning_parent_pan"), data.get("admission_category"),
            data.get("caste_category"), data.get("caste_subcaste"),
            data.get("caste_validity_no"), data.get("eligibility_no"), data.get("general_reg_no"),
            data.get("bank_name"), data.get("branch"), data.get("account_no"),
            data.get("ifsc_code"), data.get("micr_code"), data.get("last_institute_name"),
            data.get("upisc_code"), data.get("migration_cert_no"), data.get("lc_tc_no"),
            data.get("exam"), data.get("exam_body"), data.get("passing_month_year"),
            data.get("obtained_marks"), data.get("out_of_marks"), data.get("percentage"),
            photo_data, signature_data, data.get("current_address"),
            data.get("permanent_address"), current_user_id, created_date
        )

        print(f"Number of placeholders: {query.count('%s')}")
        print(f"Number of values: {len(values)}")

        db.execute(query, values)
        conn.commit()

        status = "success"
        code = 200
        message = "Admission submitted successfully"
        res_data = {
            "admission_id": admission_id
        }

    except Exception as ex:
        message = f"POSTadmission Error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })


@admission_bp.route('/GETAlladmission', methods=['GET'])
@authentication
def GETAlladmission(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = []

    try:
        db.execute("SELECT _id FROM user_master WHERE _id = %s", (current_user_id,))
        user = db.fetchone()

        if not user:
            message = "Unauthorized user"
            code = 403
            return jsonify({
                "status": status,
                "code": code,
                "message": message,
                "res_data": res_data
            })
        

        # Fetch all admission fields
        db.execute("""
            SELECT 
                admission_form_no,
                _id AS admission_id,
                first_name,
                middle_name,
                last_name,
                email,
                mobile_number,
                gender,
                religion,
                dob,
                birth_place,
                nationality,
                disability,
                domicile_state,
                aadhar_no,
                mother_name,
                mother_tongue,
                locality,
                blood_group,
                guardian_mobile,
                mother_mobile,
                earning_parent_income,
                earning_parent_pan,
                admission_category,
                caste_category,
                caste_subcaste,
                caste_validity_no,
                eligibility_no,
                general_reg_no,
                bank_name,
                branch,
                account_no,
                ifsc_code,
                micr_code,
                last_institute_name,
                upisc_code,
                migration_cert_no,
                lc_tc_no,
                exam,
                exam_body,
                passing_month_year,
                obtained_marks,
                out_of_marks,
                percentage,
                current_address,
                permanent_address,
                photo_data,
                signature_data,
                created_by,
                created_date
            FROM admission_master
            ORDER BY created_date DESC
        """)
        rows = db.fetchall()
        admission_list = [dict(row) for row in rows]
        if admission_list:
            for admission in admission_list:
                # Convert binary data to base64 strings if present
                if admission.get("photo_data"):
                    admission["photo_data"] = base64.b64encode(admission["photo_data"]).decode('utf-8')
                if admission.get("signature_data"):
                    admission["signature_data"] = base64.b64encode(admission["signature_data"]).decode('utf-8')
            
            status = "success"
            code = 200
            message = "Admissions fetched successfully"
            res_data = admission_list
        else:
            status = "success"
            code = 404
            message = "No admissions found"
            res_data = []

    except Exception as ex:
        message = f"GETAlladmission Error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

