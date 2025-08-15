import os
from flask import Flask, render_template, request,session
from routes.user_routes import user_bp
from routes.diagnostic_routes import diagnostic_bp
from dbconn import get_conn
from jinja2 import Environment
from markupsafe import escape
import json
from utils import init_mail

def escapejs_filter(value):
    # Basic escapejs implementation
    return json.dumps(value)[1:-1]  # crude but works for simple cases


app = Flask(__name__)
app.jinja_env.filters['escapejs'] = escapejs_filter
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
init_mail(app)


app.register_blueprint(user_bp)
app.register_blueprint(diagnostic_bp)


@app.route('/')
def home():
    session.clear()
    return render_template('home.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/universal_login')
def universal_login():
    return render_template('universal_login.html')
@app.route('/universal_signup')
def universal_signup():
    return render_template('universal_signup.html')
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, ssl_context='adhoc')
