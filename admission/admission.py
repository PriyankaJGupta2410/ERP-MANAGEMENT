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
import re
from model.model import GETuserdetails


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
        data = request.json

        admission_id = str(uuid.uuid4())
        created_date = datetime.now()


        def extract_base64(encoded):
            if not encoded:
                return None
            return base64.b64decode(re.sub('^data:image/.+;base64,', '', encoded))

        photo_data = extract_base64(data.get("photo_base64"))
        signature_data = extract_base64(data.get("signature_base64"))

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
                %s, %s, %s, %s, %s, %s, %s, %s, %s, 
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

        db.execute(query, values)
        conn.commit()

        status = "success"
        code = 200
        message = "Admission submitted successfully"
        res_data = {
            "admission_id": admission_id,
            "photo_base64": data.get("photo_base64"),
            "signature_base64": data.get("signature_base64")
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
        # Check if user exists
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

        # Fetch all admissions (no school_id filter)
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
        admission_list = []
        for row in rows:
            admission = dict(row)
            if admission.get("photo_data"):
                admission["photo_data"] = base64.b64encode(admission["photo_data"]).decode('utf-8')
            if admission.get("signature_data"):
                admission["signature_data"] = base64.b64encode(admission["signature_data"]).decode('utf-8')
            admission_list.append(admission)

        status = "success"
        code = 200
        message = "Admissions fetched successfully" if admission_list else "No admissions found"
        res_data = admission_list

    except Exception as ex:
        message = f"GETAlladmission Error: {str(ex)}"
        code = 500

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@admission_bp.route('/APPROVEadmission', methods=['POST'])
@authentication
def APPROVEadmission(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        data = request.json
        admission_id = data.get("admission_id")
        new_status = data.get("status")
        reason = data.get("reason", "").strip()

        if not admission_id or not new_status:
            return jsonify({
                "status": status,
                "code": 400,
                "message": "admission_id and status are required.",
                "res_data": res_data
            })

        if new_status not in ["Approved", "Rejected"]:
            return jsonify({
                "status": status,
                "code": 400,
                "message": "Invalid status. Use 'Approved' or 'Rejected'.",
                "res_data": res_data
            })

        if new_status == "Rejected" and not reason:
            return jsonify({
                "status": status,
                "code": 400,
                "message": "Rejection reason is required when status is 'Rejected'.",
                "res_data": res_data
            })

        # Update query
        update_query = """
            UPDATE admission_master
            SET status = %s,
                rejection_reason = %s,
                modified_date = NOW()
            WHERE _id = %s
        """
        db.execute(update_query, (
            new_status,
            reason if new_status == "Rejected" else None,
            admission_id
        ))
        conn.commit()

        status = "success"
        code = 200
        message = f"Admission {new_status.lower()} successfully."
        res_data = {
            "admission_id": admission_id,
            "status": new_status,
            "rejection_reason": reason if new_status == "Rejected" else ""
        }

    except Exception as ex:
        conn.rollback()
        message = f"Error in APPROVEadmission: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })



