from flask import Blueprint, current_app, flash, get_flashed_messages, jsonify, render_template,request,redirect, session,url_for
from itsdangerous import URLSafeSerializer
from werkzeug.security import generate_password_hash, check_password_hash
from dbconn import get_conn
import psycopg2.extras
from utils import login_required
from flask import send_file
from io import BytesIO
import qrcode
from itsdangerous import URLSafeSerializer

user_bp = Blueprint('user_bp', __name__)
@user_bp.route('/user/login',methods = ['GET','POST'])
def user_login():
    if request.method == 'POST':
        aadhaar = request.form['aadhaar_number']
        pswd = request.form['password']
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE aadhaar_number = %s", (aadhaar,))
        res = cur.fetchone()
        cur.close()
        conn.close()
        if not res:
            return render_template('user_login.html',error = "User doesn't exist",aadhaar = aadhaar) 
        actual_pswd = res['password_hash']
        if check_password_hash(actual_pswd,pswd):
            session.clear()
            session['role'] = 'user'
            session['aadhaar'] = aadhaar
            return redirect('/user/dashboard')
        else:
            return render_template('user_login.html',error = 'Invalid credentials' ,aadhaar = aadhaar)
    return render_template('user_login.html')
@user_bp.route('/user/signup',methods = ['GET','POST'])
def user_signup():
    if request.method == 'POST':
        fullname = request.form['name']
        mobile = request.form['mobile']
        aadhaar = request.form['aadhaar']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password!=confirm_password:
            error = "Passwords do not match"
            return render_template(
                'user_signup.html',
                error=error,
                name=fullname,
                mobile=mobile,
                aadhaar=aadhaar
            )
        #create connection
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM users WHERE aadhaar_number = %s", (aadhaar,))
        existing_user = cur.fetchone()
        #if duplicate User
        if existing_user:
            cur.close()
            conn.close()
            error = "Aadhaar already exists"
            return render_template(
                'user_signup.html',
                error=error,
                name=fullname,
                mobile=mobile,
                aadhaar=aadhaar,
            )
        # ADD details to DB
        hashed_password = generate_password_hash(password) 
        insert_query = """ 
                        INSERT INTO users (
                        full_name,
                        phone_number,
                        aadhaar_number,
                        password_hash
                    ) VALUES (%s, %s, %s, %s);
                    """
        cur.execute(insert_query,(fullname,mobile,aadhaar,hashed_password))
        conn.commit()
        cur.close()
        conn.close()
        #print(fullname,mobile,aadhaar,password,confirm_password)
        # Here you would save data to DB
        session.clear()
        session['role'] = 'user'
        session['aadhaar'] = aadhaar
        return redirect('/user/dashboard')
    return render_template('user_signup.html')

@user_bp.route('/user/dashboard', methods=['GET', 'POST'])
@login_required('user')
def user_dashboard():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "SELECT * FROM users WHERE aadhaar_number = %s;"
    cur.execute(query, (session['aadhaar'],))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    # get flashed messages
    flashed_messages = get_flashed_messages(with_categories=True)
    # convert flashed messages into flags for template
    personal_success = None
    personal_error = None
    for category, message in flashed_messages:
        if category == 'success':
            personal_success = message
        elif category == 'error':
            personal_error = message

    return render_template('user_dashboard.html', user=user_data,
                           personal_success=personal_success,
                           personal_error=personal_error)

@user_bp.route('/user/update_personal', methods=['GET', 'POST'])
@login_required('user')
def update_personal():
    if request.method == 'POST':
        aadhaar = session['aadhaar']
        mobile = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        conn = get_conn()
        cur = conn.cursor()
        update_query = """
                        UPDATE users
                        SET phone_number = %s,
                            email = %s,
                            address = %s
                        WHERE aadhaar_number = %s;
                        """
        try:
            cur.execute(update_query, (mobile, email, address, aadhaar))
            if cur.rowcount == 0:
                flash("Failed to update personal details. Try again.", "error")
            else:
                conn.commit()
                flash("Personal details updated successfully!", "success")
        except Exception as e:
            print(e)
            conn.rollback()
            flash("Failed to update personal details.", "error")
        finally:
            cur.close()
            conn.close()

        return redirect('/user/dashboard')
@user_bp.route('/user/update_emergency', methods=['GET', 'POST'])
@login_required('user')
#Hello
def update_emergency():
    if request.method == 'POST':
        aadhaar = session['aadhaar']
        contact_name = request.form['emergency_name']
        contact_number = request.form['emergency_number']
        relation = request.form['emergency_relation']
        address = request.form['emergency_address']
        conn = get_conn()
        cur = conn.cursor()
        update_query = """
                        UPDATE users
                        SET emergency_contact_name = %s,
                            emergency_contact_number = %s,
                            emergency_contact_relation = %s,
                            emergency_contact_address = %s
                        WHERE aadhaar_number = %s;
                        """
        try:
            cur.execute(update_query, (contact_name, contact_number, relation, address, aadhaar))
            if cur.rowcount == 0:
                flash("Failed to update emergency contact details. Try again.", "error")
            else:
                conn.commit()
                flash("Emergency contact details updated successfully!", "success")
        except Exception as e:
            print(e)
            conn.rollback()
            flash("Failed to update emergency contact details. Try again.", "error")
        finally:
            cur.close()
            conn.close()

        return redirect('/user/dashboard')
@user_bp.route('/user/logout', methods=['GET', 'POST'])
@login_required('user')
def update_logout():
    session.clear()
    return redirect('/')

@user_bp.route("/api/history/<aadhaar_number>", methods=["GET"])
@login_required('user')
def get_history(aadhaar_number):
    try:
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        query = """
            SELECT change_type, description, changed_at
            FROM profile_history
            WHERE aadhaar_number = %s
            ORDER BY changed_at DESC
        """
        cur.execute(query, (aadhaar_number,))
        records = cur.fetchall()
        results = []
        for r in records:
            results.append({
                "change_type": r["change_type"],
                "description": r["description"],
                "changed_at": r["changed_at"].strftime("%d-%m-%Y %H:%M:%S")
            })
        cur.close()
        conn.close()
        return jsonify(results)
    except Exception as e:
        print("Error fetching history:", e)
        return jsonify({"error": "Failed to fetch history"}), 500
@user_bp.route('/user/generate_qr', methods=['GET', 'POST'], endpoint='generate_qr')
@login_required('user')
def generate_qr():
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    query = "SELECT * FROM users WHERE aadhaar_number = %s;"
    cur.execute(query, (session['aadhaar'],))
    user_data = cur.fetchone()
    cur.close()
    conn.close()
    def safe_get(data, key):
        value = data.get(key, "")
        return str(value) if value is not None else ""
    public_fields = {
        'full_name': safe_get(user_data, 'full_name'),
        'address': safe_get(user_data, 'address'),
        'emergency_contact_name': safe_get(user_data, 'emergency_contact_name'),
        'emergency_contact_mobile': safe_get(user_data, 'emergency_contact_number'),
        'emergency_contact_relation': safe_get(user_data, 'emergency_contact_relation'),
        'emergency_contact_address': safe_get(user_data, 'emergency_contact_address')
    }
    private_fields = {
        'blood_group': safe_get(user_data, 'blood_group'),
        'allergies': safe_get(user_data, 'allergies'),
        'chronic_conditions': safe_get(user_data, 'chronic_conditions'),
        'disabilities': safe_get(user_data, 'disabilities'),
        'emergency_note': safe_get(user_data, 'emergency_note'),
        'last_medical_update': safe_get(user_data, 'last_medical_update')
    }
    # 2. Encrypt private fields
    s = URLSafeSerializer(current_app.secret_key)
    encrypted_private = s.dumps(private_fields)
    # 3. Combine public + encrypted private
    qr_data = {
        'public': public_fields,
        'private': encrypted_private
    }
    # 4. Generate QR
    img = qrcode.make(str(qr_data))
    buf = BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    # 5. Send image
    return send_file(buf, mimetype='image/png')
