import pyrebase

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
email = ''
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

