from flask import request, Blueprint , jsonify , json,request, session,render_template
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash,check_password_hash
from connector import db,conn
from functools import wraps
from decorator import authentication
import jwt
import os
from datetime import datetime,timedelta
import uuid
from werkzeug.utils import secure_filename

load_dotenv()

role_bp = Blueprint('role_bp', __name__)

################################### ROLE API ############################

@role_bp.route('/POSTrole', methods=['POST'])
@authentication
def POSTrole(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        data = request.json
        role_name = data.get("role_name")
        role = data.get("role")
        description = data.get("description", "")
        role_type = data.get("type", "non-teaching").lower()  # Default to 'non-teaching'

        if not role_name or not role:
            message = "Both role_name and role (display name) are required."
            code = 400
        elif role_type not in ["teaching", "non-teaching"]:
            message = "Invalid role type. Must be 'teaching' or 'non-teaching'."
            code = 400
        else:
            check_query = "SELECT 1 FROM role_master WHERE role_name = %s AND status = 'active'"
            db.execute(check_query, (role_name.lower().strip(),))
            if db.fetchone():
                message = "Role name already exists and is active."
                code = 409
            else:
                role_id = str(uuid.uuid4())
                created_date = datetime.now()
                insert_query = """
                    INSERT INTO role_master (_id, role_name, role, description, status, user_id, created_date, type)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                db.execute(insert_query, (
                    role_id,
                    role_name.lower().strip(),
                    role.strip(),
                    description.strip(),
                    "active",
                    current_user_id,
                    created_date,
                    role_type
                ))
                conn.commit()

                res_data = {
                    "_id": role_id,
                    "role_name": role_name.lower().strip(),
                    "role": role.strip(),
                    "type": role_type
                }
                message = "Role added successfully"
                code = 200
                status = "success"

    except Exception as e:
        message = f"Unexpected error in POSTrole: {str(e)}"

    return jsonify({
        "message": message,
        "status": status,
        "code": code,
        "res_data": res_data
    })


@role_bp.route('/GETroles', methods=['GET'])
@authentication
def GETroles(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = []

    try:
        role_type = request.args.get("type")

        base_query = """
            SELECT _id, role_name, role
            FROM role_master
            WHERE status = 'active'
              AND role_name NOT IN ('superadmin', 'principal')
        """
        params = []

        if role_type:
            base_query += " AND type = %s"
            params.append(role_type.lower().strip())

        db.execute(base_query, params)
        roles = db.fetchall()

        if roles:
            res_data = [{"_id": role["_id"], "role_name": role["role_name"], "role": role["role"]} for role in roles]
            message = "Roles fetched successfully"
            code = 200
            status = "success"
        else:
            message = "No roles found"
            code = 404

    except Exception as e:
        message = f"Unexpected error in GETroles: {str(e)}"

    return jsonify({
        "message": message,
        "status": status,
        "code": code,
        "res_data": res_data
    })


@role_bp.route('/ToggleActive', methods=['POST'])
@authentication
def ToggleActive(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        data = request.json
        role_id = data.get("role_id")
        action = data.get("action")  # 'activate' or 'deactivate'

        if not role_id or action not in ['activate', 'deactivate']:
            message = "Invalid input data."
            code = 400
            return jsonify({"message": message, "status": status, "code": code, "res_data": res_data})

        new_status = 'active' if action == 'activate' else 'inactive'
        update_query = """
            UPDATE role_master 
            SET status = %s, user_id = %s, modified_date = %s 
            WHERE _id = %s
        """
        db.execute(update_query, (new_status, current_user_id, datetime.now(), role_id))
        conn.commit()

        res_data["_id"] = role_id
        res_data["status"] = new_status
        message = f"Role {action}d successfully."
        code = 200
        status = "success"

    except Exception as e:
        message = f"Unexpected error in ToggleActive: {str(e)}"

    return jsonify({"message": message, "status": status, "code": code, "res_data": res_data})