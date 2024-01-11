import pyrebase

config = {
    "apiKey": "AIzaSyBDbJTXCtLmhkiIWX1FGn4k7QIoKthaN9I",
    "authDomain": "chatvideo-871b4.firebaseapp.com",
    "projectId": "chatvideo-871b4",
    "storageBucket": "chatvideo-871b4.appspot.com",
    "messagingSenderId": "516775972611",
    "appId": "1:516775972611:web:6373f82fb6c5aa8ab66336",
    "measurementId": "G-04E3YCCNHH",
    'databaseURL':'https://chatvideo-871b4-default-rtdb.asia-southeast1.firebasedatabase.app'
}

firebase = pyrebase.initialize_app(config=config)

auth = firebase.auth()
db = firebase.database()
email = 'leducdat231197@gmail.com'
password = ''
#signup acount
# auth.create_user_with_email_and_password(email, password)
#email verification
# auth.send_email_verification(email)
#login acount
user = auth.sign_in_with_email_and_password(email,password)
print(user['localId'])
#for_got password send reset email
# auth.send_password_reset_email(email)
# #get uid by email
# user_id = next((id for id, data in db.child("users").get().val().items() if data["email"] == "example_email@email.com"), None)
# if user_id:
#     print("User ID is:", user_id)

# user_id = '1'
# data = {'email':'leducdat123'}
# #sử dụng hàm sau để cập nhật dữ liệu và thay đổi dữ liệu với data là một từ điển 
# db.child('users').child(user_id).update(data)

# user = db.child('users').child(user_id).get()
# print(user.val())#OrderedDict([('email', 'leducdat123'), ('name', 'dat')])

# print(user.val()['name'])#dat

