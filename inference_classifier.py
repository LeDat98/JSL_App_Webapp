import pickle
import cv2
import mediapipe as mp
import numpy as np

model_dict = pickle.load(open('./model.p', 'rb'))
model_char = model_dict['model']

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

hands = mp_hands.Hands(static_image_mode=True, min_detection_confidence=0.3)

labels_dict = {0: 'A', 1: 'I', 2: 'U'}
while True:

    data_aux = []
    x_ = []
    y_ = []

    ret, frame = cap.read()

    H, W, _ = frame.shape

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,  # image to draw
                hand_landmarks,  # model output
                mp_hands.HAND_CONNECTIONS,  # hand connections
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())

        for hand_landmarks in results.multi_hand_landmarks:
            # 1.đưa tọa độ x và y vào hai mảng x_,y_ tạm thời để lấy giá trị nhỏ nhất cho bước 2
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y

                x_.append(x)
                y_.append(y)
            # 2.chuẩn hóa dữ liệu để tránh nhiễu tọa độ hay vị trí bàn tay trên ảnh
            for i in range(len(hand_landmarks.landmark)):
                x = hand_landmarks.landmark[i].x
                y = hand_landmarks.landmark[i].y
                data_aux.append(x - min(x_))#chuẩn hóa dữ liệu bằng cách trừ đi giá trị x bé nhất trong mảng x_ 
                data_aux.append(y - min(y_))
     
        print('DATA SHAPE:', np.array(data_aux).shape)
        print('DATA: ',data_aux)
        x1 = int(min(x_) * W) - 10
        y1 = int(min(y_) * H) - 10

        x2 = int(max(x_) * W) - 10
        y2 = int(max(y_) * H) - 10
        
        # prediction = model.predict([np.asarray(data_aux)])
        # predicted_character = labels_dict[int(prediction[0])]
        # Lấy xác suất dự đoán cho từng lớp
        proba_predictions = model_char.predict_proba([np.array(data_aux)])
        # Lấy xác suất dự đoán lớp có xác suất cao nhất
        max_proba = np.max(proba_predictions)

        # Nếu xác suất cao hơn ngưỡng, gán nhãn; nếu không, bạn có thể gán giá trị None hoặc chuỗi trống
        if max_proba > 0.5:
            predicted_label_index = np.argmax(proba_predictions)
            predicted_character = labels_dict[predicted_label_index]
        else:
            predicted_character = 'NULL'  
        labels_confidence = f'{predicted_character}:{max_proba}' 
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 0), 4)
        cv2.putText(frame, labels_confidence, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 0), 3,
                    cv2.LINE_AA)

    cv2.imshow('frame', frame)
    cv2.waitKey(1)


cap.release()
cv2.destroyAllWindows()
