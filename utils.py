from functools import wraps
from flask import session, redirect, url_for
import os
def login_required(role):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if 'role' not in session or session['role'] != role:
                return redirect(url_for('universal_login'))
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper
#------------------------
# utils.py
import secrets
from flask_mail import Mail, Message
from datetime import datetime, timedelta

mail = Mail()
email = os.environ.get('EMAIL')
password = os.environ.get('MAIL_PASSWORD')
def init_mail(app):
    """Initialize Flask-Mail with app config."""
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USERNAME'] = email  # Replace
    app.config['MAIL_PASSWORD'] = password     # Replace
    app.config['MAIL_DEFAULT_SENDER'] = ('LifeTag OTP', email)
    mail.init_app(app)

def generate_otp(length=6):
    """Generate a numeric OTP."""
    return ''.join(secrets.choice('0123456789') for _ in range(length))

def send_otp_email(recipient_email):
    """Send OTP email and return OTP + expiry time."""
    otp = generate_otp()
    expiry = datetime.now() + timedelta(minutes=5)
    msg = Message("Your LifeTag OTP", recipients=[recipient_email])
    msg.body = f"""
    Hello,

    Your OTP for updating medical details is: {otp}

    This OTP will expire in 5 minutes.
    If you did not request this, please ignore this email.

    Regards,
    LifeTag Team
    """
    mail.send(msg)
    return otp, expiry
