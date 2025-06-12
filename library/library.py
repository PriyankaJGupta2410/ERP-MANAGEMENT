from flask import Blueprint, request, jsonify, send_file
from connector import conn, db
from datetime import datetime, timedelta
from decorator import authentication
import io
import uuid
from fpdf import FPDF

library_bp = Blueprint('library', __name__)

###################################### LIBRARY API ########################
@library_bp.route('/POSTbook', methods=['GET', 'POST'])
@authentication
def POSTbook(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        if request.method == 'POST':
            data = request.json
            book_id = str(uuid.uuid4())
            book_name = data.get('book_name')
            quantity = data.get('quantity')
            barcode = data.get('barcode')
            author = data.get('author')
            price = data.get('price')
            publication = data.get('publication')

            # Validate all fields
            if not all([book_name, quantity, barcode, author, price, publication]):
                return jsonify({
                    "status": "fail",
                    "code": 400,
                    "message": "All fields are required.",
                    "res_data": {}
                })

            quantity = int(quantity)
            price = float(price)
            total_price = price * quantity

            db.execute("""
                INSERT INTO books_master(_id, name, quantity, barcode, author, price, publication, total_price, created_by, created_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (
                book_id,
                book_name,
                quantity,
                barcode,
                author,
                price,
                publication,
                total_price,
                current_user_id
            ))
            conn.commit()

            status = "success"
            code = 200
            message = "Book added successfully."
            res_data = {
                "_id": book_id,
                "book_name": book_name,
                "quantity": quantity,
                "total_price": total_price
            }

        else:  # GET request
            status = "success"
            code = 200
            message = "Add book form loaded successfully."
            res_data = {"form": "add_book"}

    except Exception as e:
        message = f"Error adding book: {str(e)}"
        conn.rollback()

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })


@library_bp.route('/Issuebook', methods=['GET', 'POST'])
@authentication
def Issuebook(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        if request.method == 'POST':
            data = request.json
            issued_id = str(uuid.uuid4())
            transaction_id = str(uuid.uuid4())
            book_id = data.get('book_id')
            user_id = data.get('user_id')
            issue_date = data.get('issue_date') or datetime.today().strftime('%Y-%m-%d')
            return_date = data.get('return_date')
            fine_per_day = data.get('fine')

            # Validation
            if not all([book_id, user_id, return_date, fine_per_day]):
                return jsonify({
                    "status": "fail",
                    "code": 400,
                    "message": "All fields are required.",
                    "res_data": {}
                })

            # Check stock
            db.execute("SELECT quantity FROM books_master WHERE _id = %s", (book_id,))
            book = db.fetchone()

            if book and book['quantity'] > 0:
                # Insert into issued_books
                db.execute("""
                    INSERT INTO issued_books 
                    (_id, book_id, user_id, issue_date, return_date, fine_per_day, created_by, created_date)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
                """, (issued_id, book_id, user_id, issue_date, return_date, fine_per_day, current_user_id))

                # Update stock
                db.execute("UPDATE books_master SET quantity = quantity - 1 WHERE _id = %s", (book_id,))

                # Insert transaction
                db.execute("""
                    INSERT INTO transactions_master 
                    (_id, book_id, user_id, action, action_date, created_by, created_date)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (transaction_id, book_id, user_id, 'issued', issue_date, current_user_id))

                conn.commit()

                status = "success"
                code = 200
                message = "Book issued successfully."
                res_data = {
                    "book_id": book_id,
                    "user_id": user_id,
                    "issue_date": issue_date,
                    "return_date": return_date
                }
            else:
                code = 400
                message = "Book is out of stock."

        else:  # GET request
            db.execute("SELECT * FROM books_master WHERE quantity > 0")
            books = db.fetchall()
            db.execute("SELECT _id, username, email FROM user_master")
            users = db.fetchall()

            status = "success"
            code = 200
            message = "Issue book form loaded successfully."
            res_data = {
                "books": [dict(book) for book in books],
                "users": [dict(user) for user in users]
            }

    except Exception as e:
        message = f"Error issuing book: {str(e)}"
        conn.rollback()

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@library_bp.route('/GETallbooks', methods=['GET'])
@authentication
def GETallbooks(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}
    try:
        query = request.args.get('q', '').strip()
        if query:
            db.execute("SELECT * FROM books_master WHERE name LIKE %s OR author LIKE %s", (f"%{query}%", f"%{query}%"))
        else:
            db.execute("SELECT * FROM books_master")
        books = db.fetchall()
        
        status = "success"
        code = 200
        message = "Books retrieved successfully."
        res_data = {
            "books": [dict(book) for book in books],
            "query": query
        }
    except Exception as e:
        message = f"Error listing books: {str(e)}"
    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@library_bp.route('/GETissuedbooks')
@authentication
def GETissuedbooks(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}
    try:
        db.execute("""SELECT ib.*, b.name as book_name, u.username as user_name 
                          FROM issued_books ib 
                          JOIN books b ON ib.book_id = b.id 
                          JOIN user_master u ON ib.user_id = u._id""")
        issued = db.fetchall()

        for record in issued:
            today = datetime.today().date()
            return_date = record['return_date']
            record['fine'] = max((today - return_date).days * record['fine_per_day'], 0) if today > return_date else 0

        status = "success"
        code = 200
        message = "Issued books retrieved successfully."
        res_data = {
            "issued_books": [dict(record) for record in issued]
        }
    except Exception as e:
        message = f"Error loading issued books: {str(e)}"
    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@library_bp.route('/Returnbook', methods=['GET', 'POST'])
@authentication
def Returnbook(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        if request.method == 'POST':
            issued_id = request.json.get('issued_id')
            return_date = datetime.today().strftime('%Y-%m-%d')
            transaction_id = str(uuid.uuid4())

            if not issued_id:
                return jsonify({
                    "status": "fail",
                    "code": 400,
                    "message": "Issued ID is required.",
                    "res_data": {}
                })

            # Fetch issued book
            db.execute("SELECT * FROM issued_books WHERE _id = %s", (issued_id,))
            issued = db.fetchone()

            if issued:
                # Increase quantity
                db.execute("UPDATE books SET quantity = quantity + 1 WHERE _id = %s", (issued['book_id'],))

                # Remove from issued_books
                db.execute("DELETE FROM issued_books WHERE _id = %s", (issued_id,))

                # Insert into transactions
                db.execute("""
                    INSERT INTO transactions (_id, book_id, user_id, action, action_date, created_by, created_date)
                    VALUES (%s, %s, %s, %s, %s, %s, NOW())
                """, (transaction_id, issued['book_id'], issued['user_id'], 'returned', return_date, current_user_id))

                conn.commit()

                status = "success"
                code = 200
                message = "Book returned successfully."
                res_data = {
                    "issued_id": issued_id,
                    "return_date": return_date
                }
            else:
                status = "fail"
                code = 404
                message = "Issued book record not found."

        else:  # GET method
            db.execute("""
                SELECT 
                    ib._id AS issued_id,
                    b.name AS book_name,
                    u.username AS user_name
                FROM issued_books ib
                JOIN books b ON ib.book_id = b._id
                JOIN user_master u ON ib.user_id = u._id
            """)
            issued = db.fetchall()

            status = "success"
            code = 200
            message = "Return book form loaded successfully."
            res_data = {
                "issued_books": [dict(record) for record in issued]
            }

    except Exception as e:
        conn.rollback()
        message = f"Error in Returnbook: {str(e)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })



@library_bp.route('/browse-books')
@authentication
def browse_books(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}
    try:
        query = request.args.get('q', '').strip()
        if query:
            db.execute("SELECT * FROM books_master WHERE name LIKE %s OR author LIKE %s", (f"%{query}%", f"%{query}%"))
        else:
            db.execute("SELECT * FROM books_master")
        books = db.fetchall()
        status = "success"
        code = 200
        message = "Books browsed successfully."
        res_data = {
            "books": [dict(book) for book in books],
            "query": query
        }
    except Exception as e:
        message = f"Error browsing books: {str(e)}"
    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@library_bp.route('/my-issued-books', methods=['GET'])
@authentication
def my_issued_books(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}
    
    try:
        db.execute("""
            SELECT ib.*, b.name AS book_name 
            FROM issued_books ib 
            JOIN books b ON ib.book_id = b._id 
            WHERE ib.user_id = %s
        """, (current_user_id,))
        issued = db.fetchall()

        for record in issued:
            # Ensure return_date is a date object
            return_date = record['return_date']
            if isinstance(return_date, str):
                return_date = datetime.strptime(return_date, '%Y-%m-%d').date()

            today = datetime.today().date()

            # Fine calculation
            overdue_days = (today - return_date).days
            record['fine'] = max(overdue_days * record['fine_per_day'], 0) if today > return_date else 0

            # Alert for due tomorrow
            record['alert'] = 'Return due tomorrow' if today == (return_date - timedelta(days=1)) else ''

        status = "success"
        code = 200
        message = "User issued books retrieved successfully."
        res_data = {
            "user_id": current_user_id,
            "issued_books": [dict(record) for record in issued]
        }
        
    except Exception as e:
        message = f"Error loading my issued books: {str(e)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@library_bp.route('/transactions', methods=['GET', 'POST'])
def view_transactions():
    message = ""
    code = 500
    status = "fail"
    res_data = {}
    try:
        query = """
            SELECT t.*, b.name as book_name, b.author, u.username as user_name 
            FROM transactions_master t 
            JOIN books_master b ON t.book_id = b.id 
            JOIN user_master u ON t.user_id = u._id """
        params = []
        from_date = request.form.get('from_date') or request.args.get('from_date')
        to_date = request.form.get('to_date') or request.args.get('to_date')
        
        if from_date and to_date:
            query += " WHERE action_date BETWEEN %s AND %s"
            params = [from_date, to_date]

        query += " ORDER BY action_date DESC"
        db.execute(query, params)
        transactions = db.fetchall()

        if request.form.get("download_pdf") == "yes" or request.args.get("download_pdf") == "yes":
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Library Transaction History", ln=True, align='C')
            pdf.ln(10)

            pdf.set_font("Arial", 'B', 10)
            headers = ["Date", "Book Name", "Author", "User", "Status"]
            widths = [35, 45, 40, 40, 30]
            for i, header in enumerate(headers):
                pdf.cell(widths[i], 10, header, 1, 0, 'C')
            pdf.ln()

            pdf.set_font("Arial", '', 10)
            for t in transactions:
                pdf.cell(widths[0], 10, str(t['action_date']), 1)
                pdf.cell(widths[1], 10, str(t['book_name']), 1)
                pdf.cell(widths[2], 10, str(t['author']), 1)
                pdf.cell(widths[3], 10, str(t['user_name']), 1)
                pdf.cell(widths[4], 10, str(t['action'].capitalize()), 1)
                pdf.ln()

            pdf_output = io.BytesIO()
            pdf_bytes = pdf.output(dest='S').encode('latin1')
            pdf_output.write(pdf_bytes)
            pdf_output.seek(0)
            return send_file(pdf_output, as_attachment=True, download_name="transaction_history.pdf", mimetype='application/pdf')

        status = "success"
        code = 200
        message = "Transactions retrieved successfully."
        res_data = {
            "transactions": [dict(transaction) for transaction in transactions],
            "from_date": from_date,
            "to_date": to_date
        }
    except Exception as e:
        message = f"Error loading transactions: {str(e)}"
    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })

@library_bp.route('/newspaper', methods=['GET', 'POST'])
@authentication
def newspaper(current_user_id=None):
    message = ""
    code = 500
    status = "fail"
    res_data = {}

    try:
        if request.method == "POST":
            data = request.json
            newspaper_id = str(uuid.uuid4())
            newspaper_type = data.get('type')
            name = data.get('name')
            date = data.get('date')
            quantity = data.get('quantity')
            frequency = data.get('frequency')
            price = data.get('price')

            if not all([newspaper_type, name, date, quantity, frequency, price]):
                return jsonify({
                    "status": "fail",
                    "code": 400,
                    "message": "All fields are required.",
                    "res_data": {}
                })

            total = int(price) * int(quantity)

            db.execute("""INSERT INTO newsmagzine 
                (_id, type, name, dates, frequency, quantity, price, total) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
                (newspaper_id, newspaper_type, name, date, frequency, quantity, price, total))
            conn.commit()

            status = "success"
            code = 200
            message = "Newspaper/Magazine entry added successfully."
            res_data = {
                "_id": newspaper_id,
                "type": newspaper_type,
                "name": name,
                "date": date,
                "total": total
            }

        else:
            from_date = request.args.get('from_date')
            to_date = request.args.get('to_date')
            download_pdf = request.args.get('download_pdf')

            query = "SELECT * FROM newsmagzine"
            params = []

            if from_date and to_date:
                query += " WHERE dates BETWEEN %s AND %s"
                params = [from_date, to_date]

            db.execute(query, params)
            newsmagzine = db.fetchall()

            if download_pdf == "yes":
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", 'B', 14)
                pdf.cell(200, 10, "Newspaper & Magazine Transactions", ln=True, align='C')
                pdf.ln(10)

                headers = ["Type", "Name", "Date", "Frequency", "Qty", "Price", "Total"]
                widths = [25, 40, 25, 30, 15, 20, 25]
                pdf.set_font("Arial", 'B', 10)
                for i, header in enumerate(headers):
                    pdf.cell(widths[i], 10, header, 1, 0, 'C')
                pdf.ln()

                pdf.set_font("Arial", '', 10)
                for row in newsmagzine:
                    pdf.cell(widths[0], 10, str(row['type']), 1)
                    pdf.cell(widths[1], 10, str(row['name']), 1)
                    pdf.cell(widths[2], 10, str(row['dates']), 1)
                    pdf.cell(widths[3], 10, str(row['frequency']), 1)
                    pdf.cell(widths[4], 10, str(row['quantity']), 1)
                    pdf.cell(widths[5], 10, str(row['price']), 1)
                    pdf.cell(widths[6], 10, str(row['total']), 1)
                    pdf.ln()

                pdf_output = io.BytesIO()
                pdf_bytes = pdf.output(dest='S').encode('latin1')
                pdf_output.write(pdf_bytes)
                pdf_output.seek(0)
                return send_file(
                    pdf_output,
                    as_attachment=True,
                    download_name="news_magazine_history.pdf",
                    mimetype='application/pdf'
                )

            status = "success"
            code = 200
            message = "Newspaper/Magazine data retrieved successfully."
            res_data = {
                "newsmagzine": [dict(row) for row in newsmagzine],
                "from_date": from_date,
                "to_date": to_date
            }

    except Exception as e:
        message = f"Error in newspaper route: {str(e)}"

    return jsonify({
        "status": status,
        "code": code,
        "message": message,
        "res_data": res_data
    })