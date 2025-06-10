from flask import request, Blueprint , jsonify , json,request, session,render_template
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash,check_password_hash
from connector import db,conn
from functools import wraps
from decorator import authentication
import jwt
import os
from datetime import datetime,timedelta
import smtplib
from email.mime.text import MIMEText
import random
import uuid
from werkzeug.utils import secure_filename

load_dotenv()

fee_bp = Blueprint('fee',__name__)

############################################ FEE API #############################################
@fee_bp.route('/POSTfee', methods=['POST'])
@authentication
def POSTfee(current_user_id=None):
    message = ""
    res_data = {}
    status = "fail"
    code = 500

    try:
        data = request.json
        _id = str(uuid.uuid4()) 
        fee_type = data.get('fee_type')
        amount = data.get('amount')
        description = data.get('description')
        class_name = data.get('class')
        section = data.get('section')
        academic_year = data.get('academic_year')
        
        created_by = current_user_id 
        if not fee_type or amount is None or not academic_year:
            message = "fee_type, amount, and academic_year are required."
            code = 400
        else:
            query = """
                INSERT INTO fee_master 
                (_id, fee_type, amount, description, class, section, academic_year, created_by, created_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (
                _id,
                fee_type,
                amount,
                description,
                class_name,
                section,
                academic_year,
                created_by,
                datetime.now()
            )
            db.execute(query, params)
            conn.commit()

            status = "success"
            code = 200
            message = "Fee structure created successfully."
            res_data = {
                "_id": _id,
                "fee_type": fee_type,
                "amount": amount,
                "description": description,
                "class": class_name,
                "section": section,
                "academic_year": academic_year,
                "created_by": created_by,
            }

    except Exception as ex:
        message = f"Error in POSTfee: {str(ex)}"
        code = 500

    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})

@fee_bp.route('/assign_fee_to_student', methods=['POST'])
@authentication
def assign_fee_to_student(current_user_id=None):
    message = ""
    res_data = {}
    status = "fail"
    code = 500

    try:
        data = request.json
        application_id = data.get("application_id")
        fee_id = data.get("fee_id")
        amount = data.get("amount")
        due_date = data.get("due_date")
        created_date = datetime.now()

        if not application_id or not fee_id or not amount or not due_date:
            message = "All fields (application_id, fee_id, amount, due_date) are required."
            code = 400
        else:
            query = """INSERT INTO student_fee_assignment
                       (application_id, fee_id, amount, due_date, created_by,created_date)
                       VALUES (%s, %s, %s, %s, %s,%s)"""
            values = (application_id, fee_id, amount, due_date, current_user_id,created_date)
            db.execute(query, values)
            db.commit()

            status = "success"
            code = 200
            message = "Fee assigned to student successfully."

    except Exception as e:
        message = f"Error in assigning fee: {str(e)}"
        code = 500

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@fee_bp.route('/record_payment', methods=['POST'])
@authentication
def record_payment(current_user_id=None):
    message = ""
    res_data = {}
    status = "fail"
    code = 500

    try:
        data = request.json
        student_id = data.get("student_id")
        amount_paid = data.get("amount_paid")
        payment_mode = data.get("payment_mode")
        receipt_number = data.get("receipt_number")
        created_date = datetime.now

        if not all([student_id, amount_paid, payment_mode, receipt_number]):
            message = "All fields are required."
            code = 400
        else:
            query = """
                INSERT INTO payment (student_id, amount_paid, payment_date, payment_mode, receipt_number,created_by,created_date)
                VALUES (%s, %s, NOW(), %s, %s,%s,%s)
            """
            db.execute(query, (student_id, amount_paid, payment_mode, receipt_number,current_user_id,created_date))
            code = 201
            status = "success"
            message = "Payment recorded successfully."

    except Exception as ex:
        message = f"Error in record_payment: {str(ex)}"
        code = 500

    return jsonify({"status": status, "code": code, "message": message, "res_data": res_data})
