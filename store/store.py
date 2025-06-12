from flask import Blueprint, request, jsonify
from connector import db, conn
from decorator import authentication
from datetime import datetime
import uuid

store_bp = Blueprint('store', __name__)

@store_bp.route('/dashboard', methods=['GET'])
@authentication
def dashboard(current_user_id):
    message = ""
    status = "fail"
    code = 500
    res_data = {}

    try:
        # Get user's school_id for data filtering
        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
        user_row = db.fetchone()
        
        if user_row and user_row.get("school_id"):
            school_id = user_row.get("school_id")
            
            # Get dashboard summary data
            db.execute("SELECT COUNT(*) as total_items FROM Item WHERE school_id = %s", (school_id,))
            total_items = db.fetchone()['total_items']
            
            db.execute("SELECT COUNT(*) as low_stock_items FROM Item WHERE quantity <= min_stock_alert AND school_id = %s", (school_id,))
            low_stock_items = db.fetchone()['low_stock_items']
            
            db.execute("SELECT COUNT(*) as total_transactions FROM StockTransaction st JOIN Item i ON st.item_id = i.id WHERE i.school_id = %s", (school_id,))
            total_transactions = db.fetchone()['total_transactions']
            
            res_data = {
                "total_items": total_items,
                "low_stock_items": low_stock_items,
                "total_transactions": total_transactions
            }
            
            message = "Dashboard data fetched successfully"
            status = "success"
            code = 200
        else:
            message = "User not found or school_id not assigned"
            code = 403

    except Exception as ex:
        message = f"Dashboard error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@store_bp.route('/issue_item', methods=['POST'])
@authentication
def issue_item(current_user_id):
    message = ""
    status = "fail"
    code = 500
    res_data = {}

    try:
        data = request.json
        category = data.get('category')
        item_id = data.get('item_id')
        issued_to = data.get('issued_to')
        quantity = int(data.get('quantity', 0))
        issue_date = data.get('issue_date')
        return_date = data.get('return_date') if category == '2' else None
        remarks = data.get('remarks', '')

        if not all([item_id, issued_to, quantity, issue_date]):
            message = "All required fields must be provided"
            code = 400
        else:
            # Get user's school_id for data filtering
            db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
            user_row = db.fetchone()
            
            if not user_row or not user_row.get("school_id"):
                message = "User not found or school_id not assigned"
                code = 403
            else:
                school_id = user_row.get("school_id")
                
                # Check available stock
                db.execute("SELECT quantity FROM Item WHERE _id = %s AND school_id = %s", (item_id, school_id))
                item = db.fetchone()
                
                if not item:
                    message = "Item not found"
                    code = 404
                elif item['quantity'] < quantity:
                    message = "Not enough stock available to issue"
                    code = 400
                else:
                    transaction_id = str(uuid.uuid4())
                    created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Insert transaction record
                    db.execute("""
                        INSERT INTO StockTransaction 
                        (_id, item_id, transaction_date, transaction_type, quantity, issued_to, remarks, created_by, created_date) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (transaction_id, item_id, issue_date, 'ISSUE', quantity, issued_to, remarks, current_user_id, created_date))
                    
                    # Update item quantity
                    db.execute("UPDATE Item SET quantity = quantity - %s WHERE _id = %s", (quantity, item_id))
                    conn.commit()
                    
                    res_data = {
                        "transaction_id": transaction_id,
                        "item_id": item_id,
                        "quantity": quantity,
                        "issued_to": issued_to,
                        "issue_date": issue_date
                    }
                    
                    message = "Item issued successfully"
                    status = "success"
                    code = 200

    except Exception as ex:
        message = f"Issue item error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@store_bp.route('/return_item', methods=['POST'])
@authentication
def return_item(current_user_id):
    message = ""
    status = "fail"
    code = 500
    res_data = {}

    try:
        data = request.json
        item_id = data.get('item_id')
        returned_by = data.get('returned_by')
        quantity = int(data.get('quantity', 0))
        return_date = data.get('return_date')
        remarks = data.get('remarks', '')

        if not all([item_id, returned_by, quantity, return_date]):
            message = "All required fields must be provided"
            code = 400
        else:
            # Get user's school_id for data filtering
            db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
            user_row = db.fetchone()
            
            if not user_row or not user_row.get("school_id"):
                message = "User not found or school_id not assigned"
                code = 403
            else:
                school_id = user_row.get("school_id")
                
                # Check issued and already returned quantities
                db.execute("""
                    SELECT COALESCE(SUM(st.quantity), 0) AS issued_quantity
                    FROM StockTransaction st
                    JOIN Item i ON st.item_id = i._id
                    WHERE st.item_id = %s AND st.issued_to = %s AND st.transaction_type = 'ISSUE' AND i.school_id = %s
                """, (item_id, returned_by, school_id))
                issued_qty = db.fetchone()['issued_quantity']

                db.execute("""
                    SELECT COALESCE(SUM(st.quantity), 0) AS returned_quantity
                    FROM StockTransaction st
                    JOIN Item i ON st.item_id = i._id
                    WHERE st.item_id = %s AND st.returned_by = %s AND st.transaction_type = 'RETURN' AND i.school_id = %s
                """, (item_id, returned_by, school_id))
                returned_qty = db.fetchone()['returned_quantity']

                if quantity > (issued_qty - returned_qty):
                    message = "Return quantity exceeds unreturned issued items"
                    code = 400
                else:
                    transaction_id = str(uuid.uuid4())
                    created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    # Insert return transaction
                    db.execute("""
                        INSERT INTO StockTransaction 
                        (_id, item_id, transaction_date, transaction_type, quantity, returned_by, remarks, created_by, created_date) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (transaction_id, item_id, return_date, 'RETURN', quantity, returned_by, remarks, current_user_id, created_date))
                    
                    # Update item quantity
                    db.execute("UPDATE Item SET quantity = quantity + %s WHERE _id = %s", (quantity, item_id))
                    conn.commit()
                    
                    res_data = {
                        "transaction_id": transaction_id,
                        "item_id": item_id,
                        "quantity": quantity,
                        "returned_by": returned_by,
                        "return_date": return_date
                    }
                    
                    message = "Item returned successfully"
                    status = "success"
                    code = 200

    except Exception as ex:
        message = f"Return item error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@store_bp.route('/add_item', methods=['POST'])
@authentication
def add_item(current_user_id):
    message = ""
    status = "fail"
    code = 500
    res_data = {}

    try:
        data = request.json
        name = data.get('name')
        category_id = data.get('category_id')
        quantity = int(data.get('quantity', 0))
        unit = data.get('unit')
        min_stock_alert = int(data.get('min_stock_alert', 0))
        description = data.get('description', '')
        price = float(data.get('price', 0))

        if not all([name, category_id, quantity, unit, min_stock_alert, price]):
            message = "All required fields must be provided"
            code = 400
        else:
            # Get user's school_id
            db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
            user_row = db.fetchone()
            
            if not user_row or not user_row.get("school_id"):
                message = "User not found or school_id not assigned"
                code = 403
            else:
                school_id = user_row.get("school_id")
                item_id = str(uuid.uuid4())
                total_price = price * quantity
                created_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                db.execute("""
                    INSERT INTO Item 
                    (_id, name, category_id, quantity, unit, min_stock_alert, description, price, total_price, school_id, created_by, created_date) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (item_id, name, category_id, quantity, unit, min_stock_alert, description, price, total_price, school_id, current_user_id, created_date))
                conn.commit()

                res_data = {
                    "item_id": item_id,
                    "name": name,
                    "category_id": category_id,
                    "quantity": quantity,
                    "price": price,
                    "total_price": total_price
                }

                message = "Item added successfully"
                status = "success"
                code = 200

    except Exception as ex:
        message = f"Add item error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@store_bp.route('/get_stock', methods=['GET'])
@authentication
def get_stock(current_user_id):
    message = ""
    status = "fail"
    code = 500
    res_data = {}

    try:
        # Get user's school_id for data filtering
        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
        user_row = db.fetchone()
        
        if user_row and user_row.get("school_id"):
            school_id = user_row.get("school_id")
            
            db.execute("""
                SELECT 
                    i._id as item_id,
                    i.name, 
                    i.quantity, 
                    i.description, 
                    i.min_stock_alert, 
                    i.price, 
                    i.total_price,
                    i.unit,
                    ic.name as category_name
                FROM Item i
                LEFT JOIN ItemCategory ic ON i.category_id = ic.id
                WHERE i.school_id = %s
                ORDER BY i.name
            """, (school_id,))
            items = db.fetchall()
            
            low_stock_items = [item for item in items if item['quantity'] <= item['min_stock_alert']]
            
            res_data = {
                "items": items,
                "low_stock_items": low_stock_items,
                "total_items": len(items),
                "low_stock_count": len(low_stock_items)
            }
            
            message = "Stock data fetched successfully"
            status = "success"
            code = 200
        else:
            message = "User not found or school_id not assigned"
            code = 403

    except Exception as ex:
        message = f"Get stock error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@store_bp.route('/get_issued_items', methods=['GET'])
@authentication
def get_issued_items(current_user_id):
    message = ""
    status = "fail"
    code = 500
    res_data = []

    try:
        # Get user's school_id for data filtering
        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
        user_row = db.fetchone()
        
        if user_row and user_row.get("school_id"):
            school_id = user_row.get("school_id")
            
            db.execute("""
                SELECT 
                    i.name AS item_name,
                    st.transaction_date,
                    st.issued_to,
                    st.item_id,
                    u.username AS user_name,
                    SUM(st.quantity) AS issued_quantity
                FROM StockTransaction st
                JOIN Item i ON st.item_id = i._id
                JOIN user_master u ON st.issued_to = u._id
                WHERE st.transaction_type = 'ISSUE' AND i.category_id = 2 AND i.school_id = %s
                GROUP BY st.item_id, st.issued_to, st.transaction_date
                ORDER BY st.transaction_date DESC
            """, (school_id,))
            issued_records = db.fetchall()

            visible_issued_items = []
            for record in issued_records:
                db.execute("""
                    SELECT COALESCE(SUM(quantity), 0) as returned_quantity
                    FROM StockTransaction st2
                    JOIN Item i2 ON st2.item_id = i2._id
                    WHERE st2.transaction_type = 'RETURN'
                      AND st2.item_id = %s
                      AND st2.returned_by = %s
                      AND st2.transaction_date >= %s
                      AND i2.school_id = %s
                """, (record['item_id'], record['issued_to'], record['transaction_date'], school_id))
                returned = db.fetchone()
                returned_quantity = returned['returned_quantity'] or 0
                remaining_quantity = record['issued_quantity'] - returned_quantity
                
                if remaining_quantity > 0:
                    visible_issued_items.append({
                        'item_name': record['item_name'],
                        'transaction_date': record['transaction_date'],
                        'quantity': remaining_quantity,
                        'user_name': record['user_name'],
                        'item_id': record['item_id'],
                        'issued_to': record['issued_to']
                    })

            res_data = visible_issued_items
            message = "Issued items data fetched successfully"
            status = "success"
            code = 200
        else:
            message = "User not found or school_id not assigned"
            code = 403

    except Exception as ex:
        message = f"Get issued items error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@store_bp.route('/get_transactions', methods=['POST'])
@authentication
def get_transactions(current_user_id):
    message = ""
    status = "fail"
    code = 500
    res_data = []

    try:
        data = request.json
        from_date = data.get('from_date')
        to_date = data.get('to_date')
        
        # Get user's school_id for data filtering
        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
        user_row = db.fetchone()
        
        if user_row and user_row.get("school_id"):
            school_id = user_row.get("school_id")
            
            query = """
                SELECT 
                    st._id as transaction_id,
                    i.name AS item_name,
                    st.transaction_date,
                    st.transaction_type,
                    COALESCE(u1.username, u2.username, '') AS user_name,
                    st.quantity,
                    st.remarks
                FROM StockTransaction st
                JOIN Item i ON st.item_id = i._id
                LEFT JOIN user_master u1 ON st.issued_to = u1._id
                LEFT JOIN user_master u2 ON st.returned_by = u2._id
                WHERE i.school_id = %s
            """
            filters = [school_id]

            if from_date:
                query += " AND st.transaction_date >= %s"
                filters.append(from_date)
            if to_date:
                query += " AND st.transaction_date <= %s"
                filters.append(to_date)

            query += " ORDER BY st.transaction_date DESC"
            db.execute(query, filters)
            transactions = db.fetchall()
            
            res_data = transactions
            message = "Transactions data fetched successfully"
            status = "success"
            code = 200
        else:
            message = "User not found or school_id not assigned"
            code = 403

    except Exception as ex:
        message = f"Get transactions error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@store_bp.route('/get_categories', methods=['GET'])
@authentication
def get_categories(current_user_id):
    message = ""
    status = "fail"
    code = 500
    res_data = []

    try:
        db.execute("SELECT * FROM ItemCategory ORDER BY name")
        categories = db.fetchall()
        
        res_data = categories
        message = "Categories fetched successfully"
        status = "success"
        code = 200

    except Exception as ex:
        message = f"Get categories error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@store_bp.route('/get_users', methods=['GET'])
@authentication
def get_users(current_user_id):
    message = ""
    status = "fail"
    code = 500
    res_data = []

    try:
        # Get user's school_id for data filtering
        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
        user_row = db.fetchone()
        
        if user_row and user_row.get("school_id"):
            school_id = user_row.get("school_id")
            
            db.execute("SELECT _id, username, email, role FROM user_master WHERE school_id = %s ORDER BY username", (school_id,))
            users = db.fetchall()
            
            res_data = users
            message = "Users fetched successfully"
            status = "success"
            code = 200
        else:
            message = "User not found or school_id not assigned"
            code = 403

    except Exception as ex:
        message = f"Get users error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@store_bp.route('/get_items', methods=['GET'])
@authentication
def get_items(current_user_id):
    message = ""
    status = "fail"
    code = 500
    res_data = []

    try:
        # Get user's school_id for data filtering
        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (current_user_id,))
        user_row = db.fetchone()
        
        if user_row and user_row.get("school_id"):
            school_id = user_row.get("school_id")
            
            db.execute("""
                SELECT 
                    i._id as item_id,
                    i.name,
                    i.quantity,
                    i.unit,
                    i.price,
                    ic.name as category_name,
                    i.category_id
                FROM Item i
                LEFT JOIN ItemCategory ic ON i.category_id = ic.id
                WHERE i.school_id = %s
                ORDER BY i.name
            """, (school_id,))
            items = db.fetchall()
            
            res_data = items
            message = "Items fetched successfully"
            status = "success"
            code = 200
        else:
            message = "User not found or school_id not assigned"
            code = 403

    except Exception as ex:
        message = f"Get items error: {str(ex)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })