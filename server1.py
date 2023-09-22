from flask_cors import CORS  # add this
import platform
from flask_socketio import SocketIO, emit, join_room
from flask import Flask, request, render_template, jsonify,session
import numpy as np
import time
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import tensorflow as tf
import pickle
tf.config.set_visible_devices([], 'GPU')
app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = "wubba lubba dub dub"

CORS(app)  # add this

socketio = SocketIO(app, cors_allowed_origins="*")  # modify this

# ... the rest of your code ...
users_in_room = {}
rooms_sid = {}
names_sid = {}
folder_counter = 0
request_counter = 0
is_resting = False  # Trạng thái nghỉ
start_time = None
sequence = {}
sentence = []
right_hand_landmarks_X_Y = []
labels_dict = {0: 'A', 1: 'I', 2: 'U'}
threshold = 0.9
#Load model for detect character
model_dict = pickle.load(open('./model.p', 'rb'))
model_char = model_dict['model']
# Actions that we try to detect
actions = np.array(['HELLO','GOOD_EVENING','Imsorry','THANKS'])
model = Sequential()
model.add(LSTM(64, return_sequences=True, activation='tanh', input_shape=(20,225)))
model.add(LSTM(128, return_sequences=True, activation='tanh'))
model.add(LSTM(64, return_sequences=False, activation='tanh'))
model.add(Dense(64, activation='relu'))
model.add(Dense(64, activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(actions.shape[0], activation='softmax'))
#load model trained
model.load_weights('webappmodelv1.h5')
json_counter = 0
def checkHandLandmarksCoordinates(x_array,y_array):
    maxX = max(x_array) * 426 #video width
    maxY = max(y_array) * 320 #video height
    # print('maxX: ',maxX,'  maxY: ',maxY)
    return maxX <= 160 and maxY <= 160 and maxX > 0 and maxY > 0

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/join", methods=["GET"])
def join():
    display_name = request.args.get('display_name')
    mute_audio = request.args.get('mute_audio') # 1 or 0
    mute_video = request.args.get('mute_video') # 1 or 0
    room_id = request.args.get('room_id')
    session[room_id] = {"name": display_name,
                        "mute_audio": mute_audio, "mute_video": mute_video}
    return render_template("join.html", room_id=room_id, display_name=session[room_id]["name"], mute_audio=session[room_id]["mute_audio"], mute_video=session[room_id]["mute_video"])

@app.route('/combined_landmark_endpoint', methods=['POST'])
def handle_landmark_data():
    global folder_counter, request_counter, is_resting, start_time, sequence, sentence, json_counter, right_hand_landmarks_X_Y, labels_dict, model_char
    if request.method != 'POST':
        return 'This endpoint accepts POST requests containing combined hand and pose landmark data.'

    data = request.get_json()

    handednesses = data.get('handLandmarks').get('handednesses')
    left_hand_index = None
    right_hand_index = None

    for index, handedness in enumerate(handednesses):
        if handedness[0]['categoryName'] == 'Right':
            left_hand_index = index
        elif handedness[0]['categoryName'] == 'Left':
            right_hand_index = index
    
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
                print(proba_predictions)
                right_hand_landmarks_X_Y = []
                # Lấy xác suất dự đoán lớp có xác suất cao nhất
                max_proba = np.max(proba_predictions)
                # Nếu xác suất cao hơn ngưỡng, gán nhãn; nếu không, bạn có thể gán giá trị None hoặc chuỗi trống
                if max_proba > 0.3:
                    predicted_label_index = np.argmax(proba_predictions)
                    predicted_character = labels_dict[predicted_label_index]
                    print(predicted_character)
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
                        else:
                                sentence.append(actions[np.argmax(res)])
                    if len(sentence) > 5: 
                        sentence = sentence[-5:]
                        print("LIST: ",sentence) 
                    # Gửi sự kiện đến tất cả các clients trong phòng chung
                    socketio.emit('sentence', {'sentence': sentence}, room=room_id)
                    # Gửi sự kiện đến tất cả các clients trong phòng chung
                    socketio.emit('message', {'message': sentence[-1],'sender': sender}, room=room_id)

            elif (left_hand_landmarks_np[0] == 0) and (right_hand_landmarks_np[0] == 0):
                print('elif true')
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
    emit('message', {'sender': 'System', 'message': f'{display_name} has entered the room.'}, room=room)

# Khi người dùng gửi tin nhắn
@socketio.on('send-message')
def handle_send_message(data):
    room = data['room_id']
    sender = data['sender']
    message = data['message']
    print(f'{sender} sent message: {message}')
    emit('message', {'sender': sender, 'message': message}, room=room)

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