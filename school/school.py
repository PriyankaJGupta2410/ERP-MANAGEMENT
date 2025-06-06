from flask import request, Blueprint , jsonify , json,request, session,render_template
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash,check_password_hash
from connector import db,conn
from functools import wraps
from decorator import authentication
import uuid

load_dotenv()
school_bp = Blueprint('school',__name__)

####################################### School API ###############################

@school_bp.route('/GETschooldetails', methods=['GET'])
@authentication
def GETschooldetails(current_user_id=None):
    message = ""
    status = "fail"
    code = 500
    res_data = []

    try:
        db.execute("SELECT 1 FROM user_master WHERE _id = %s", (current_user_id,))
        user_exists = db.fetchone()

        if user_exists:
            db.execute("SELECT * FROM school_master WHERE superadmin_id = %s", (current_user_id,))
            rows = db.fetchall()

            if rows:
                for row in rows:
                    school = {
                        "_id": row[0],
                        "about_us": row[1],
                        "infrastructure": row[2],
                        "latest_news": row[3],
                        "gallery": row[4],
                        "contact_us": row[5],
                        "created_date": str(row[6]),
                        "superadmin_id": row[7]
                    }
                    res_data.append(school)

                message = "School details fetched successfully."
                status = "success"
                code = 200
            else:
                message = "No school records found for this user."
                code = 404
        else:
            message = "User not found."
            code = 403

    except Exception as ex:
        message = f"GETschooldetails: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

