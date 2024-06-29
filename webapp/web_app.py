from flask import Flask, render_template, request, redirect, url_for, flash, make_response
from datetime import timedelta
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from flask_bcrypt import Bcrypt
import os
import mysql.connector
import pyotp
import logging
from logging.handlers import RotatingFileHandler
from flask_limiter import Limiter  # Importing the Limiter class
from flask_limiter.util import get_remote_address

# Logging configuration
log_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(status_code)s - %(message)s')
log_file = 'webapp.log'
my_handler = RotatingFileHandler(log_file, mode='a', maxBytes=5*1024*1024, backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_logger = logging.getLogger('root')
app_logger.setLevel(logging.INFO)
app_logger.addHandler(my_handler)

def log_message(level, message, status_code=200):
    user_info = f"[User: {current_user.get_id()}]" if current_user.is_authenticated else "[Unauthenticated]"
    message = f"{user_info} - {message}"
    extra = {'status_code': status_code}
    if level == "info":
        app_logger.info(message, extra=extra)
    elif level == "error":
        app_logger.error(message, extra=extra)

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
app.config['SESSION_COOKIE_NAME'] = 'COOKIEMONSTER'
app.secret_key = os.urandom(24)
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

class User:
    def __init__(self, id, role):
        self.id = id
        self.role = role

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def has_role(self, role):
        return self.role == role

@app.errorhandler(429)
def ratelimit_error(e):
    return "Je hebt teveel requests gestuurd", 429

conn = mysql.connector.connect(
    host="172.20.2.100",
    user="beheer",
    password="Geheim123!",
    database="db"
)
cursor = conn.cursor()

@login_manager.user_loader
def load_user(user_id):
    cursor.execute("SELECT id, role FROM users WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    if user_data:
        user_id, role = user_data
        return User(user_id, role)
    return None

@app.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(url_for('portal'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    log_message('info', 'has logged in')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT id, password, secret_key, role FROM users WHERE username = %s", (username,))
        user_data = cursor.fetchone()
        if user_data:
            user_id, stored_password, secret_key, role = user_data
            if stored_password and bcrypt.check_password_hash(stored_password, password):
                if 'mfa_code' in request.form:
                    mfa_code = request.form['mfa_code']
                    totp = pyotp.TOTP(secret_key)
                    if totp.verify(mfa_code):
                        if totp.verify(mfa_code, valid_window=1):
                            user = User(user_id, role)
                            login_user(user)
                            return redirect(url_for('portal'))
                        else:
                            flash('Ongeldige gebruikersnaam, wachtwoord of MFA-code.')
                            log_message("error", f"Failed login attempt for user {username}")  
                            return render_template('login.html', error='Ongeldige gebruikersnaam, wachtwoord of MFA-code.')
                flash('Ongeldige gebruikersnaam, wachtwoord of MFA-code.')
                return render_template('login.html', error='Voer de MFA-code in om door te gaan.')
            else:
                flash('Ongeldige gebruikersnaam, wachtwoord of MFA-code.')
                return render_template('login.html', error='Ongeldige gebruikersnaam, wachtwoord of MFA-code.')
        else:
            flash('Ongeldige gebruikersnaam, wachtwoord of MFA-code.')
            return render_template('login.html', error='Ongeldige gebruikersnaam, wachtwoord of MFA-code.')
    else:
        return render_template('login.html')

def get_latest_log_events(num=15):
    """Function to get the latest num log events."""
    with open(log_file, 'r') as f:
        return list(reversed(f.readlines()[-num:]))

@login_required
@app.route('/portal', methods=['GET', 'POST'])
def portal():
    log_message('info', 'User has accessed the portal')
    if current_user.is_authenticated:
        if request.method == 'POST':
            if 'light' in request.form:
                light = float(request.form['light'])
                log_message('info', 'changed the lights')
                cursor.execute("UPDATE light SET status = %s", (light,))
            elif 'locking' in request.form:
                locking = float(request.form['locking'])
                log_message('info', 'changed the locks')
                cursor.execute("UPDATE locking SET status = %s", (locking,))
            elif 'fire' in request.form:
                fire = float(request.form['fire'])
                log_message('info', 'changed the fire alarm')
                cursor.execute("UPDATE fire SET status = %s", (fire,))
            elif 'camera' in request.form:
                camera = float(request.form['camera'])
                log_message('info', 'changed the camera feed')
                cursor.execute("UPDATE camera SET status = %s", (camera,))
            conn.commit()
            return redirect(url_for('portal'))
        else:
            cursor.execute("SELECT status FROM light WHERE id = 1")
            light_on = cursor.fetchone()[0] == 5.0
            cursor.execute("SELECT status FROM locking WHERE id = 1")
            locking_on = cursor.fetchone()[0] == 5.0
            cursor.execute("SELECT status FROM fire WHERE id = 1")
            fire_on = cursor.fetchone()[0] == 5.0
            cursor.execute("SELECT status FROM camera WHERE id = 1")
            camera_on = cursor.fetchone()[0] == 5.0
            latest_logs = get_latest_log_events(num=10)  # Fetch the latest logs
            return render_template('portal.html', light_on=light_on, locking_on=locking_on, fire_on=fire_on, camera_on=camera_on, logs=latest_logs)
    else:
        return redirect(url_for('login'))

@app.route('/logout', methods=['POST'])
def logout():
    logout_user()
    response = make_response(redirect(url_for('login')))
    response.delete_cookie(app.config['SESSION_COOKIE_NAME'])
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, ssl_context=('cert.pem', 'key.pem'))
