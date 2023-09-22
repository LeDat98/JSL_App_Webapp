from flask_cors import CORS  # add this
import platform
from flask_socketio import SocketIO, emit, join_room
from flask import Flask, request, render_template, jsonify, session, redirect, url_for
import numpy as np
import time
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import tensorflow as tf
import pickle
import pyrebase
from functools import wraps
from collections import Counter


tf.config.set_visible_devices([], 'GPU')
app = Flask(__name__, static_folder='static')
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
app.config['SECRET_KEY'] = "wubba lubba dub dub"

CORS(app)  

socketio = SocketIO(app, cors_allowed_origins="*")  

users_in_room = {}
rooms_sid = {}
names_sid = {}
folder_counter = 0
request_counter = 0
is_resting = False  # Trạng thái nghỉ
start_time = None
sequence = {}
sentence = []
sentence_char = []
old_char = None
right_hand_landmarks_X_Y = []
# labels_dict = {0: 'A', 1: 'I', 2: 'U'}

labels_dict = {0: 'た', 1: 'な', 2: 'か',3:'Enter',4:'な'}
threshold = 0.9
#Load model for detect character
model_dict = pickle.load(open('./modelv2.p', 'rb'))
model_char = model_dict['model']
# Actions that we try to detect
# actions = np.array(['GOOD_EVENING','HELLO','Imsorry','THANKS'])
actions = np.array(['はじめまして', 'こんにちは', '私の名前は', 'ありがとうございます', 'と申します', 'よろしくおねがいします。'])
# actions = np.array(['NAME','TOMOUSHIMASU','YOROSHIKU'])

model = Sequential()
model.add(LSTM(64, return_sequences=True, activation='tanh', input_shape=(20,225)))
model.add(LSTM(128, return_sequences=True, activation='tanh'))
model.add(LSTM(64, return_sequences=False, activation='tanh'))
model.add(Dense(64, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(actions.shape[0], activation='softmax'))

model.load_weights('webappmodelv3.h5')
json_counter = 0


def most_frequent_element(arr):
    # Đếm số lần xuất hiện của mỗi phần tử trong mảng
    count = Counter(arr)
    # Tìm phần tử xuất hiện nhiều nhất
    most_common_element = count.most_common(1)
    # Kiểm tra xem phần tử đó có xuất hiện tối thiểu 6 lần hay không
    if most_common_element and most_common_element[0][0] == 'Enter' and most_common_element[0][1] >= 8:
        return most_common_element[0][0]
    elif most_common_element and most_common_element[0][1] >= 6 and most_common_element[0][0] != 'Enter':
        return most_common_element[0][0]
    # Nếu không thoả mãn điều kiện, làm trống mảng và trả về None
    arr.clear()
    return None
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'localId' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function
def checkHandLandmarksCoordinates(x_array,y_array):
    maxX = max(x_array) * 426 #video width
    maxY = max(y_array) * 320 #video height
    # print('maxX: ',maxX,'  maxY: ',maxY)
    return maxX <= 160 and maxY <= 160 and maxX > 0 and maxY > 0
@app.route('/', methods=['POST','GET'])
def index():

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        try:
            user = auth.sign_in_with_email_and_password(email,password)
            print(user['localId'])
            session['localId'] = user['localId']
            session['email'] = email
            return redirect('/home')
        except Exception as e:
            print(e)
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
            db.child('users').child(user_id).update(data)
            return redirect('/')
        except Exception as e:
            print(e)
            return 'Failed to sign up'
    return render_template('signup.html')  
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
    session.clear()
    return redirect('/')

@app.route('/home')
@login_required 
def home():
    if 'localId' in session:
        print(session)
        print(session['localId'])
        return render_template('home.html')
    else:
        return 'Please log in'
@app.route('/joinlink',methods=["GET"])
@login_required 
def joinlink():
    if 'localId' in session:
        print(session)
        print(session['localId'])
        return render_template('joinlink.html')
    else:
        return 'Please log in'
    
@app.route("/join", methods=["GET"])
@login_required 
def join():
    if 'localId' in session:
        user = db.child('users').child(session['localId']).get()
        display_name = user.val()['name']
    mute_audio = request.args.get('mute_audio') # 1 or 0
    mute_video = request.args.get('mute_video') # 1 or 0
    room_id = request.args.get('room_id')
    session[room_id] = {"name": display_name,
                        "mute_audio": mute_audio, "mute_video": mute_video}
    return render_template("join.html", room_id=room_id, display_name=session[room_id]["name"], mute_audio=session[room_id]["mute_audio"], mute_video=session[room_id]["mute_video"])

@app.route('/combined_landmark_endpoint', methods=['POST'])
def handle_landmark_data():
    global folder_counter, request_counter, is_resting, start_time, sequence, sentence, sentence_char
    global json_counter, right_hand_landmarks_X_Y, labels_dict, model_char, old_char
    if request.method != 'POST':
        return 'This endpoint accepts POST requests containing combined hand and pose landmark data.'

    data = request.get_json()
    handednesses = data.get('handLandmarks').get('handednesses')
    left_hand_index = None
    right_hand_index = None

    for index, handedness in enumerate(handednesses):
        if handedness[0]['categoryName'] == 'Right':
            right_hand_index = index
        elif handedness[0]['categoryName'] == 'Left':
            left_hand_index = index
    
    x_array = np.array([landmark['x'] for landmark in data.get('handLandmarks').get('landmarks')[right_hand_index]]).flatten() if right_hand_index is not None else np.zeros(21)
    x_list = x_array.tolist()
    y_array = np.array([landmark['y'] for landmark in data.get('handLandmarks').get('landmarks')[right_hand_index]]).flatten() if right_hand_index is not None else np.zeros(21)
    y_list = y_array.tolist()
    sid = data['sid']
    room_id = rooms_sid[sid]
    sender = names_sid[sid]
    # print('X_ARRAY: ',x_array)
    try:
        if checkHandLandmarksCoordinates(x_list,y_list):
            sequence[sender] = []
            json_counter = 0
            # Gửi sự kiện đến tất cả các clients trong phòng chung
            socketio.emit('sentence', {'sentence': sentence, 'counter': "文字を認識中"}, room=room_id)
            try:
                for landmark in data.get('handLandmarks').get('landmarks')[right_hand_index]:
                    x = landmark['x']
                    y = landmark['y']
                    right_hand_landmarks_X_Y.append(x - min(x_list))
                    right_hand_landmarks_X_Y.append(y - min(y_list))
                # Lấy xác suất dự đoán cho từng lớp
                proba_predictions = model_char.predict_proba([np.asarray(right_hand_landmarks_X_Y)])
                # print(proba_predictions)
                right_hand_landmarks_X_Y = []
                # Lấy xác suất dự đoán lớp có xác suất cao nhất
                max_proba = np.max(proba_predictions)
                # Nếu xác suất cao hơn ngưỡng, gán nhãn; nếu không, bạn có thể gán giá trị None hoặc chuỗi trống
                if max_proba > 0.3:
                    predicted_label_index = np.argmax(proba_predictions)
                    predicted_character = labels_dict[predicted_label_index]
                    
                    sentence_char.append(predicted_character)
                    print(sentence_char)
                    if len(sentence_char) == 8:
                        print("sentence_char10:",sentence_char)
                        result = most_frequent_element(sentence_char)
                        print("pred char :",result)
                        if result is None or result == old_char:
                            sentence_char = []
                        else:
                            # Gửi sự kiện đến tất cả các clients trong phòng chung
                            socketio.emit('message', {'message': result,'sender': sender, 'type': 'AI'}, room=room_id)
                            sentence_char = []
                            old_char = result
                else:
                    predicted_character = 'NULL'
                    print('NULL')
            except Exception as e:
                print(e)
        else:
            # Convert left_hand_landmarks to a NumPy array
            left_hand_landmarks_np = np.array([(landmark['x'], landmark['y'], landmark['z']) for landmark in data.get('handLandmarks').get('landmarks')[left_hand_index]]).flatten() if left_hand_index is not None else np.zeros(21*3)
            # Convert right_hand_landmarks to a NumPy array
            right_hand_landmarks_np = np.array([(landmark['x'], landmark['y'], landmark['z']) for landmark in data.get('handLandmarks').get('landmarks')[right_hand_index]]).flatten() if right_hand_index is not None else np.zeros(21*3)
            # Concatenate left and right hand landmark arrays
            hand_landmarks = np.concatenate([left_hand_landmarks_np, right_hand_landmarks_np])
            # Process pose landmarks
            pose_landmarks = data.get('poseLandmarks')
            # Convert pose_landmarks to a NumPy array
            pose_landmarks_np = np.array([(landmark['x'], landmark['y'], landmark['z']) for landmark in pose_landmarks[0]]).flatten() if pose_landmarks[0] else np.zeros(33*3)
            if (left_hand_landmarks_np[0] != 0) or (right_hand_landmarks_np[0] != 0):
                # Tăng biến đếm và kiểm tra nếu đạt đến 20
                json_counter += 1
                if json_counter > 20:
                    json_counter = 1
                socketio.emit('sentence', {'counter': json_counter}, room=room_id)
                # Concatenate the global variables
                detect_landmarks = np.concatenate([pose_landmarks_np, hand_landmarks])
                # print(detect_landmarks)
                # Lưu array vào file
                sequence[sender].append(detect_landmarks)
                sequence[sender] = sequence[sender][-20:]
                if len(sequence[sender]) == 20:
                    res = model.predict(np.expand_dims(sequence[sender], axis=0))[0]
                    sequence[sender] = []
                    if res[np.argmax(res)] > threshold:
                        print(actions[np.argmax(res)]) 
                        if len(sentence) > 0: 
                            if actions[np.argmax(res)] != sentence[-1]:
                                sentence.append(actions[np.argmax(res)])
                                socketio.emit('message', {'message': sentence[-1],'sender': sender, 'type': 'AI'}, room=room_id)
                        else:
                                sentence.append(actions[np.argmax(res)])
                                socketio.emit('message', {'message': sentence[-1],'sender': sender, 'type': 'AI'}, room=room_id)
                    if len(sentence) > 5: 
                        sentence = sentence[-5:]
                        print("LIST: ",sentence) 
                    # Gửi sự kiện đến tất cả các clients trong phòng chung
                    socketio.emit('sentence', {'sentence': sentence}, room=room_id)
                    # Gửi sự kiện đến tất cả các clients trong phòng chung


            elif (left_hand_landmarks_np[0] == 0) and (right_hand_landmarks_np[0] == 0):
                # print('elif true')
                sequence[sender] = []
                json_counter = 0
                # Gửi sự kiện đến tất cả các clients trong phòng chung
                socketio.emit('sentence', {'sentence': sentence, 'counter': "手話の認識をお待ちしています。"}, room=room_id)
    except:
        print('No_poselandmark')
    return jsonify({"status": "success"}), 200

@socketio.on("connect")
def on_connect():
    sid = request.sid
    print("New socket connected ", sid)
#nhận địa chỉ phòng room_id từ client rồi trả về sid tương ứng về client 
#thông qua sự kiện user-connect
@socketio.on("join-room")
def on_join_room(data):
    sid = request.sid
    room_id = data["room_id"]
    display_name = session[room_id]["name"]
    # register sid to the room
    join_room(room_id)
    rooms_sid[sid] = room_id
    names_sid[sid] = display_name
    # broadcast to others in the room
    print("[{}] New member joined: {}<{}>".format(room_id, display_name, sid))
    emit("user-connect", {"sid": sid, "name": display_name},
         broadcast=True, include_self=False, room=room_id)
    # add to user list maintained on server
    if room_id not in users_in_room:
        users_in_room[room_id] = [sid]
        emit("user-list", {"my_id": sid})  # send own id only
    else:
        usrlist = {u_id: names_sid[u_id] for u_id in users_in_room[room_id]}
        # send list of existing users to the new member
        emit("user-list", {"list": usrlist, "my_id": sid})
        # add new member to user list maintained on server
        users_in_room[room_id].append(sid)
    print("\nusers: ", users_in_room, "\n")
# Khi người dùng kết nối vào một phòng cụ thể
@socketio.on('join-roomchat')
def handle_join_room(data):
    room = data['room_id']
    display_name = session[room]["name"]
    join_room(room)
    emit('message', {'sender': 'System', 'message': f'{display_name} has entered the room.', 'type':'OS'}, room=room)

# Khi người dùng gửi tin nhắnS
@socketio.on('send-message')
def handle_send_message(data):
    room = data['room_id']
    sender = data['sender']
    message = data['message']
    print(f'{sender} sent message: {message}')
    emit('message', {'sender': sender, 'message': message, 'type':'human'}, room=room)

@socketio.on("disconnect")
def on_disconnect():
    sid = request.sid
    room_id = rooms_sid[sid]
    display_name = names_sid[sid]
    print("[{}] Member left: {}<{}>".format(room_id, display_name, sid))
    emit("user-disconnect", {"sid": sid},
         broadcast=True, include_self=False, room=room_id)
    users_in_room[room_id].remove(sid)
    if len(users_in_room[room_id]) == 0:
        users_in_room.pop(room_id)
    rooms_sid.pop(sid)
    names_sid.pop(sid)
    print("\nusers: ", users_in_room, "\n")

@socketio.on("data")
def on_data(data):
    sender_sid = data['sender_id']
    target_sid = data['target_id']
    if sender_sid != request.sid:
        print("[Not supposed to happen!] request.sid and sender_id don't match!!!")
    if data["type"] != "new-ice-candidate":
        print('{} message from {} to {}'.format(
            data["type"], sender_sid, target_sid))
    socketio.emit('data', data, room=target_sid)


# if __name__ == "__main__":
#     socketio.run(app, debug=True,port=5000)