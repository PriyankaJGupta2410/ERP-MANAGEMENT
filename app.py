from flask import Flask,render_template,redirect,session, url_for
from connector import db
from dotenv import load_dotenv
import os

load_dotenv()
############################### Import Blueprints ########################
from auth.auth import auth_bp
from admission.admission import admission_bp
from staff.staff import staff_bp
from school.school import school_bp
from fee.fee import fee_bp
from classbp.classbp import class_bp
from store.store import store_bp  # Import Sam store  
#############################################
app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY')

################################### Register Blueprint ##############################
app.register_blueprint(auth_bp, url_prefix = "/auth")
app.register_blueprint(admission_bp,url_prefix = "/admissions")
app.register_blueprint(staff_bp,url_prefix = '/staff')
app.register_blueprint(school_bp,url_prefix = '/school')
app.register_blueprint(fee_bp,url_prefix="/fee")
app.register_blueprint(class_bp,url_prefix="/class")
app.register_blueprint(store_bp, url_prefix="/store")  # Register store blueprint
####################################################################

@app.route("/")
def index():
    return "Hello World"

############################# DECLARE TEMPLATES ##############################
@app.route('/onboard')
def manual_onboard_form():
    return render_template('manual_onboard.html') 

@app.route('/login')
def login():
    return render_template('login.html') 

@app.route('/admission_form')
def admission_form():
    return render_template('add_admission.html') 

@app.route('/SendOtp')
def SendOtp():
    return render_template('send_otp.html')

@app.route('/VerifyOtp')
def VerifyOtp():
    return render_template('verify_otp.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/registerSuperadmin')
def registerSuperadmin():
    return render_template('register_superadmin.html')

@app.route('/registerSchool')
def registerSchool():
    return render_template('registerschool.html')

@app.route('/addSupervisor')
def addSupervisor():
    return render_template('add_supervisor.html')

@app.route('/Getstaff')
def Getstaff():
    return render_template('get_staff.html')

@app.route('/Superadmindashboard')
def Superadmindashboard():
    return render_template('superadmin_dashboard.html')

@app.route('/Supervisordashboard')
def Supervisordashboard():
    return render_template('supervisor_dashboard.html')

@app.route('/addStaff')
def addStaff():
    return render_template('add_staff.html')

@app.route('/AccountantDashboard')
def AccountantDashboard():
    return render_template('accountant_dashboard.html')

@app.route('/forgotpassword')
def forgotpassword():
    return render_template('forgot_password.html')

@app.route('/resetpassword')
def resetpassword():
    return render_template('reset_password.html')

@app.route('/forgotverifyotp')
def forgotverifyotp():
    return render_template('forgot_verify_otp.html')

# Store module template routes
# Helper function to check authentication for template routes
def check_auth():
    if 'user_id' not in session:
        return False
    return True

def get_user_school_id():
    if 'user_id' not in session:
        return None
    
    try:
        db.execute("SELECT school_id FROM user_master WHERE _id = %s", (session['user_id'],))
        user_row = db.fetchone()
        return user_row.get('school_id') if user_row else None
    except:
        return None

# Updated template routes with data

@app.route('/store_dashboard')
def store_dashboard():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('store/dashboard.html')

@app.route('/issue_item_form')
def issue_item_form():
    if not check_auth():
        return redirect(url_for('login'))
    
    school_id = get_user_school_id()
    if not school_id:
        return "Access denied", 403
    
    try:
        # Get categories
        db.execute("SELECT * FROM ItemCategory ORDER BY name")
        categories = db.fetchall()
        
        # Get items for this school
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
            WHERE i.school_id = %s AND i.quantity > 0
            ORDER BY i.name
        """, (school_id,))
        items = db.fetchall()
        
        # Get users from same school
        db.execute("SELECT _id, username, email, role FROM user_master WHERE school_id = %s ORDER BY username", (school_id,))
        users = db.fetchall()
        
        return render_template('store/issue_item.html', 
                             categories=categories, 
                             items=items, 
                             users=users)
    except Exception as e:
        return f"Error loading form data: {str(e)}", 500

@app.route('/return_item_form')
def return_item_form():
    if not check_auth():
        return redirect(url_for('login'))
    
    school_id = get_user_school_id()
    if not school_id:
        return "Access denied", 403
    
    try:
        # Get items for this school
        db.execute("""
            SELECT 
                i._id as item_id,
                i.name,
                i.quantity,
                i.unit,
                ic.name as category_name
            FROM Item i
            LEFT JOIN ItemCategory ic ON i.category_id = ic.id
            WHERE i.school_id = %s
            ORDER BY i.name
        """, (school_id,))
        items = db.fetchall()
        
        # Get users from same school
        db.execute("SELECT _id, username, email, role FROM user_master WHERE school_id = %s ORDER BY username", (school_id,))
        users = db.fetchall()
        
        return render_template('store/return_item.html', 
                             items=items, 
                             users=users)
    except Exception as e:
        return f"Error loading form data: {str(e)}", 500

@app.route('/add_item_form')
def add_item_form():
    if not check_auth():
        return redirect(url_for('login'))
    
    try:
        # Get categories
        db.execute("SELECT * FROM ItemCategory ORDER BY name")
        categories = db.fetchall()
        
        return render_template('store/add_item.html', categories=categories)
    except Exception as e:
        return f"Error loading categories: {str(e)}", 500

@app.route('/view_stock_form')
def view_stock_form():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('store/viewstock.html')

@app.route('/transactions_form')
def transactions_form():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('store/transactions.html')

@app.route('/issued_items_form')
def issued_items_form():
    if not check_auth():
        return redirect(url_for('login'))
    return render_template('store/issued_items.html')

if __name__ == '__main__':
    app.run(debug=True)
