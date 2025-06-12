from flask import request, jsonify, Blueprint
from decorator import authentication
from connector import db, conn
import uuid

leave_bp = Blueprint('Leave', __name__)

################################### LEAVE API #####################################
# POST: Submit leave application
@leave_bp.route('/PostLeave', methods=['POST'])
@authentication
def PostLeave(current_user_id):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        data = request.json

        from_date = data.get('from_date')
        to_date = data.get('to_date')
        leave_type = data.get('leave_type')  # Optional
        coverage_partner = data.get('coverage_partner')  # Optional
        reason = data.get('reason')
        leave_id = str(uuid.uuid4())

        if not all([from_date, to_date, leave_type, coverage_partner, reason]):
            return jsonify({
                "status": status,
                "code": 400,
                "message": "_id, from date, to date, leave type, coverage partner and reason are required.",
                "res_data": res_data
            })

        query = '''
            INSERT INTO leave_master (_id, from_date, to_date, leave_type, coverage_partner, reason)
            VALUES (%s, %s, %s, %s, %s, %s)
        '''
        db.execute(query, (leave_id, from_date, to_date, leave_type, coverage_partner, reason))


        status = "success"
        code = 200
        message = "Leave request submitted successfully."
        res_data = {
            "from_date": from_date,
            "to_date": to_date,
            "leave_type": leave_type,
            "coverage_partner": coverage_partner,
            "reason": reason,
            "leave_id": leave_id
        }

    except Exception as ex:
        message = f"PostLeave: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })



# GET: Fetch leave applications for the current user
@leave_bp.route('/GETLeave', methods=['GET'])
@authentication
def GETLeave(current_user_id):
    status = "fail"
    code = 500
    message = ""
    res_data = {}
    try:
        query = '''
            SELECT _id, from_date, to_date, leave_type, coverage_partner, reason, created_at
            FROM leave_master
            WHERE _id = %s
            ORDER BY created_at DESC
        '''
        db.execute(query, (current_user_id,))
        rows = db.fetchall()

        leaves = []
        for r in rows:
            leaves.append({
                "leave_id": r.get("leave_id"),
                "from_date": r.get("from_date"),
                "to_date": r.get("to_date"),
                "leave_type": r.get("leave_type"),
                "coverage_partner": r.get("coverage_partner"),
                "reason": r.get("reason"),
                "created_at": r.get("created_at"),
            })

        return jsonify({
            "status": "success",
            "code": 200,
            "message": "Leave records fetched successfully.",
            "res_data": {"leaves": leaves}
        })

    except Exception as ex:
        message = f"GETLeave:{ex}"
    return jsonify({
            "status": status,
            "code": code,
            "message": message,
            "res_data": res_data
})
