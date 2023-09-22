const POSE_CONNECTIONS = {
  'LEFT_EAR': 'LEFT_EYE',
  'LEFT_EYE': 'NOSE',
  'NOSE': 'RIGHT_EYE',
  'RIGHT_EYE': 'RIGHT_EAR',
  'LEFT_EAR': 'LEFT_SHOULDER',
  'LEFT_EYE': 'RIGHT_EYE',
  'RIGHT_EAR': 'RIGHT_SHOULDER',
  'LEFT_SHOULDER': 'RIGHT_SHOULDER',
  'LEFT_SHOULDER': 'LEFT_ELBOW',
  'LEFT_ELBOW': 'LEFT_WRIST',
  'LEFT_WRIST': 'LEFT_HAND',
  'LEFT_HAND': 'LEFT_PINKY',
  'RIGHT_SHOULDER': 'RIGHT_ELBOW',
  'RIGHT_ELBOW': 'RIGHT_WRIST',
  'RIGHT_WRIST': 'RIGHT_HAND',
  'RIGHT_HAND': 'RIGHT_PINKY',
  'LEFT_SHOULDER': 'LEFT_HIP',
  'LEFT_HIP': 'RIGHT_HIP',
  'RIGHT_SHOULDER': 'RIGHT_HIP',
  'LEFT_HIP': 'LEFT_KNEE',
  'LEFT_KNEE': 'LEFT_ANKLE',
  'LEFT_ANKLE': 'LEFT_HEEL',
  'LEFT_HEEL': 'LEFT_FOOT_INDEX',
  'RIGHT_HIP': 'RIGHT_KNEE',
  'RIGHT_KNEE': 'RIGHT_ANKLE',
  'RIGHT_ANKLE': 'RIGHT_HEEL',
  'RIGHT_HEEL': 'RIGHT_FOOT_INDEX',
};

import {
  HandLandmarker,
  PoseLandmarker,
  FilesetResolver
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0";

import Stats  from 'https://cdnjs.cloudflare.com/ajax/libs/stats.js/r17/Stats.min.js';

const init = async () =>{
  const stats = new Stats();
  document.body.appendChild(stats.dom);
  
  const video = document.getElementById("input_video");
  const canvasElement = document.getElementById("output_canvas"); 
  const canvasCtx = canvasElement.getContext("2d");

  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices
      .getUserMedia({ video: true })
      .then(function (stream) {
        video.srcObject = stream;
        video.play();
      })
      .catch(function (error) {
        console.error("Error accessing the camera: ", error);
      });
  } else {
    alert("Sorry, your browser does not support the camera API.");
  }
  
  const vision = await FilesetResolver.forVisionTasks(
    // path/to/wasm/root
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
  );

  const handLandmarker = await HandLandmarker.createFromOptions(
      vision,
      {
        baseOptions: {
          modelAssetPath: "static/hand_landmarker.task",
          delegate: "CPU"
        },
        numHands: 2
      });

  // Create pose landmarker
  const poseLandmarker = await PoseLandmarker.createFromOptions(
      vision,
      {
        baseOptions: {
          modelAssetPath: "static/pose_landmarker_full.task",
          delegate: "CPU"
        },
        numPoses: 1
      });

  await handLandmarker.setOptions({ runningMode: "video" });
  await poseLandmarker.setOptions({ runningMode: "video" });

  let lastVideoTime = -1;
  // Lưu ý: Bạn có thể cần thay đổi địa chỉ URL tùy thuộc vào cài đặt của bạn.
  const socket = io('https://27.81.58.107:5000/');
  // const socket = io('http://127.0.0.1:6868/');
  const renderLoop = () => {
    canvasElement.width = video.videoWidth;
    canvasElement.height = video.videoHeight;
    let startTimeMs = performance.now();
    if (video.currentTime > 0 && video.currentTime !== lastVideoTime) {
      const results = handLandmarker.detectForVideo(video,startTimeMs);

      // Add PoseLandmarker detect
      const poseLandmarkerResult = poseLandmarker.detectForVideo(video,startTimeMs);

      lastVideoTime = video.currentTime;
      
      canvasCtx.save();
      canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
      canvasCtx.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);

      // Process hand landmarks
      if (results.landmarks) {
        for (const landmarks of results.landmarks) {
          drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {
            color: "#00FF00",
            lineWidth: 5
          });
          drawLandmarks(canvasCtx, landmarks, { color: "#FF0000", lineWidth: 2 });

          // fetch('http://127.0.0.1:6868/landmark_endpoint', {
          //   method: 'POST',
          //   headers: {
          //     'Content-Type': 'application/json'
          //   },
          //   body: JSON.stringify(results)
          // });
        }
      }

      // Process pose landmarks
      // You might need to adjust the drawing methods depending on how the PoseLandmarks are structured
      if (poseLandmarkerResult.landmarks) {
        for (const landmarks of poseLandmarkerResult.landmarks) {
          // Adjust the methods below to fit the structure of PoseLandmarks
          drawConnectors(canvasCtx, landmarks, POSE_CONNECTIONS, {
            color: "#00FF00",
            lineWidth: 5
          });
          drawLandmarks(canvasCtx, landmarks, { color: "#FF0000", lineWidth: 2 });

          // fetch('http://127.0.0.1:6868/pose_landmark_endpoint', {
          //   method: 'POST',
          //   headers: {
          //     'Content-Type': 'application/json'
          //   },
          //   body: JSON.stringify(poseLandmarkerResult.landmarks)
          // });
        }
      }
      // // Combine the hand and pose landmark results and send them as a single POST request
      // let combinedResults = {
      //   handLandmarks: results ? results : [],
      //   poseLandmarks: poseLandmarkerResult.landmarks ? poseLandmarkerResult.landmarks : []
      // };

      // fetch('http://127.0.0.1:6868/combined_landmark_endpoint', {
      //   method: 'POST',
      //   headers: {
      //       'Content-Type': 'application/json'
      //   },
      //   body: JSON.stringify(combinedResults)
      // });
      

      let combinedResults = {
        handLandmarks: results ? results : [],
        poseLandmarks: poseLandmarkerResult.landmarks ? poseLandmarkerResult.landmarks : []
    };
    
    socket.emit('combined_landmark_event', combinedResults);
    canvasCtx.restore();
    }
    requestAnimationFrame(() => {
      stats.begin();
      renderLoop();
      stats.end();
    });
}
// Handle data received from the server
socket.on('landmark_response', function(msg) {
  // Handle the received data...
  console.log(msg.data);
});
renderLoop();
}
init();
