from flask import Flask, session, render_template, request, redirect
import pyrebase

app = Flask(__name__)
config = {
    "apiKey": "",
    "authDomain": "",
    "projectId": "",
    "storageBucket": "",
    "messagingSenderId": "",
    "appId": "",
    "measurementId": "",
    'databaseURL':''
}

firebase = pyrebase.initialize_app(config=config)
auth = firebase.auth()
db = firebase.database()

app.secret_key = 'secret'

@app.route('/', methods=['POST','GET'])
def index():
    if 'user' in session:
        return 'Hi, {}'.format(session['user'])
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email,password)
            session['user'] = email
        except:
            return 'Failed to login'
    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        
        try:
            user = auth.create_user_with_email_and_password(email, password)
            user_id = user['localId']
            
            # Lưu thông tin người dùng vào Firebase Database
            data = {'name': name, 'email': email}
            db.child('users').child(user_id).push(data)
            
            return redirect('/')
        except Exception as e:
            print(e)
            return 'Failed to sign up'
    return render_template('signup.html')
  # You'll need to create this template

@app.route('/forgot_password', methods=['POST', 'GET'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        try:
            auth.send_password_reset_email(email)
            return 'Password reset email sent'
        except:
            return 'Failed to send password reset email'
    return render_template('forgot_password.html')  # You'll need to create this template

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

if __name__ == '__main__':
    app.run(port=1111, debug=True)
