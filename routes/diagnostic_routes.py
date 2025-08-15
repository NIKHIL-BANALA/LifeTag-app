from datetime import datetime,date
from flask import Blueprint, render_template,request,redirect,url_for,session
from werkzeug.security import generate_password_hash, check_password_hash
from dbconn import get_conn
import psycopg2.extras
from utils import login_required
from utils import send_otp_email


diagnostic_bp = Blueprint('diagnostic_bp', __name__)
@diagnostic_bp.route('/diagnostic/login',methods = ['GET','POST'])
def diagnostic_login():
    if request.method == 'POST':
        centre_id = request.form['centre_id']
        pswd = request.form['password']
        conn = get_conn()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM diagnostic_centres WHERE centre_id = %s", (centre_id,))
        res = cur.fetchone()
        cur.close()
        conn.close()
        if not res:
            return render_template('diagnostic_login.html',error = "Centre doesn't exist",centre_id = centre_id) 
        actual_pswd = res['password_hash']
        if check_password_hash(actual_pswd,pswd):
            session.clear()
            session['role'] = 'diagnostic'
            session['centre_id'] = centre_id
            return redirect('/diagnostic/dashboard')
        else:
            return render_template('diagnostic_login.html',error = 'Invalid credentials' , centre_id = centre_id)
    return render_template('diagnostic_login.html')
@diagnostic_bp.route('/diagnostic/signup',methods = ['GET','POST'])
def diagnostic_signup():
    if request.method == 'POST':
        centre_id = request.form['centre_id']
        name = request.form['centre_name']
        email = request.form['email']
        mobile = request.form['contact_number']
        address = request.form['centre_address']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password!=confirm_password:
            error = "Passwords do not match"
            return render_template(
                'diagnostic_signup.html',
                error=error,
                centre_id = centre_id,
                name=name,
                email = email,
                mobile=mobile,
                address = address
            )
        #create connection
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM diagnostic_centres WHERE centre_id = %s", (centre_id,))
        existing_user = cur.fetchone()
        #if duplicate User
        if existing_user:
            cur.close()
            conn.close()
            error = "Centre already exists"
            return render_template(
                'diagnostic_signup.html',
                error=error,
                centre_id = centre_id,
                name=name,
                email = email,
                mobile=mobile,
                address = address
            )
        # ADD details to DB
        hashed_password = generate_password_hash(password) 
         
        conn.commit()
        cur.close()
        conn.close()

        #print(fullname,mobile,aadhaar,password,confirm_password)
        # Here you would save data to DB
        session.clear()
        session['role'] = 'diagnostic'
        session['centre_id'] = centre_id
        return redirect('/diagnostic/dashboard') 
    return render_template('diagnostic_signup.html')



@diagnostic_bp.route('/diagnostic/dashboard',methods = ['GET','POST'])
@login_required('diagnostic')
def diagnostic_dashboard():
    centre_id = session['centre_id']
    session.pop('user_aadhaar', None)
    session.pop('user_email', None)
    session.pop('otp', None)
    session.pop('otp_expiry', None)
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM diagnostic_centres WHERE centre_id = %s", (centre_id,))
    res = cur.fetchone()
    return render_template('diagnostic_dashboard.html',data = res)

@diagnostic_bp.route('/diagnostic/logout',methods = ['GET','POST'])
@login_required('diagnostic')
def diagnostic_logout():
    session.clear()
    return redirect('/')

@diagnostic_bp.route('/diagnostic/step1', methods=['GET', 'POST'])
@login_required('diagnostic')
def diagnostic_step1():
    centre_id = session['centre_id']
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM diagnostic_centres WHERE centre_id = %s", (centre_id,))
    centre_data = cur.fetchone()

    if request.method == "POST":
        aadhaar = request.form['aadhaar']

        cur.execute("SELECT * FROM users WHERE aadhaar_number = %s", (aadhaar,))
        user = cur.fetchone()
        cur.close()
        conn.close()

        if not user:
            return render_template('step1.html', error="User not found!", data=centre_data)

        if not user['email']:
            return render_template('step1.html', error="Email not found in records", data=centre_data)

        # Store Aadhaar + Email in session for Step 2
        session['user_aadhaar'] = aadhaar
        session['user_email'] = user['email']
        session.pop('otp', None)  # Reset OTP if redoing step1
        session.pop('otp_expiry', None)

        return redirect(url_for('diagnostic_bp.diagnostic_step2'))

    cur.close()
    conn.close()
    return render_template('step1.html', data=centre_data)


# STEP 2: OTP Send + Verification


@diagnostic_bp.route('/diagnostic/step2', methods=['GET', 'POST'])
@login_required('diagnostic')
def diagnostic_step2():
    centre_id = session['centre_id']
    recipient_email = session.get('user_email')
    aadhaar = session.get('user_aadhaar')

    if not recipient_email or not aadhaar:
        return redirect(url_for('diagnostic_bp.diagnostic_step1'))  # Safety check

    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM diagnostic_centres WHERE centre_id = %s", (centre_id,))
    centre_data = cur.fetchone()
    cur.close()
    conn.close()

    hide_email = lambda e: (lambda p: p[0][0] + '*' * max(1, len(p[0]) - 2) +
                            (p[0][-1] if len(p[0]) > 1 else '') + '@' + p[1])(e.split('@', 1))

    error = ""

    # Send OTP only if none exists or resend requested
    if not session.get('otp') or request.args.get('resend') == '1':
        otp, expiry = send_otp_email(recipient_email)
        session['otp'] = otp
        session['otp_expiry'] = expiry.timestamp()
        if request.args.get('resend') == '1':
            error = "A new OTP has been sent."

    if request.method == "POST":
        otp_entered = request.form['otp']
        stored_otp = session.get('otp')
        otp_expiry = session.get('otp_expiry')

        if not stored_otp or not otp_expiry or datetime.now().timestamp() > otp_expiry:
            error = "OTP expired. Please request a new one."
        elif otp_entered != stored_otp:
            error = "Incorrect OTP."
        else:
            # OTP verified — clear session OTP and proceed
            session.pop('otp', None)
            session.pop('otp_expiry', None)
            return redirect('/diagnostic/update_form')
            

    return render_template(
        'step2.html',
        data=centre_data,
        error=error,
        email=hide_email(recipient_email),
        aadhaar=aadhaar
    )

@diagnostic_bp.route('/diagnostic/update_form', methods=['GET', 'POST'])
@login_required('diagnostic')
def diagnostic_update_form():
    error = ''
    centre_id = session['centre_id']
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM diagnostic_centres WHERE centre_id = %s", (centre_id,))
    centre_data = cur.fetchone()
    aadhaar = session.get('user_aadhaar')
    cur.execute("SELECT * FROM users WHERE aadhaar_number = %s",(aadhaar,))
    user_data = cur.fetchone()
    if request.method == "POST":
        blood_group = request.form['blood_group']
        allergies = request.form['allergies']
        chronic_conditions = request.form['chronic_conditions']
        disabilities = request.form['disabilities']
        emergency_note = request.form['emergency_note']
        query = """
            UPDATE users
            SET blood_group = %s,
                allergies = %s,
                chronic_conditions = %s,
                disabilities = %s,
                emergency_note = %s,
                last_medical_update = %s
            WHERE aadhaar_number = %s
        """
        try:
            cur.execute(query,(blood_group,allergies,chronic_conditions,disabilities,emergency_note,datetime.now(),aadhaar,))
            if cur.rowcount == 0:
                error = "Failed to update user medical info!"
            else:
                #Update Success
                conn.commit()
                #ADD LOG into diagnostic records
                cur.execute(
                        "INSERT INTO diagnostic_records (full_name, aadhaar, email, updated_at) VALUES (%s, %s, %s, %s)",
                        (user_data['full_name'], user_data['aadhaar_number'], user_data['email'], datetime.now())
                    )
                conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
            error = "Failed to update user medical info!"
        finally:
            cur.close()
            conn.close()
        return redirect(url_for("diagnostic_bp.confirm_update", error= error))
    cur.close()
    conn.close()
    print(user_data)
    return render_template("update_form.html",data = centre_data,user_data = user_data)
@diagnostic_bp.route('/diagnostic/confirm_update', methods=['GET', 'POST'])
@login_required('diagnostic')
def confirm_update():
    centre_id = session['centre_id']
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM diagnostic_centres WHERE centre_id = %s", (centre_id,))
    centre_data = cur.fetchone()
    aadhaar = session.get('user_aadhaar')
    cur.execute("SELECT * FROM users WHERE aadhaar_number = %s",(aadhaar,))
    user_data = cur.fetchone()
    error = request.args.get("error")
    cur.close()
    conn.close()
    return render_template('confirm_update.html',data = centre_data, user_data = user_data,error = error)
@diagnostic_bp.route('/diagnostic/records', methods=['GET', 'POST'])
@login_required('diagnostic')
def diagnostic_records():
    centre_id = session['centre_id']
    conn = get_conn()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM diagnostic_centres WHERE centre_id = %s", (centre_id,))
    centre_data = cur.fetchone()
    cur.execute("SELECT * FROM diagnostic_records")
    logs = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('diagnostic_records.html',data = centre_data,logs = logs)