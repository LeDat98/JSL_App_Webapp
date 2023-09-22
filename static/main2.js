
import {
  HandLandmarker,
  PoseLandmarker,
  FilesetResolver
} from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.0";
import Stats from 'https://cdnjs.cloudflare.com/ajax/libs/stats.js/r17/Stats.min.js';

let isRunning = false;
let requestID;
const startLandmarking = async () => {
    if (isRunning) return; // Ngăn chặn việc khởi chạy nhiều lần
    isRunning = true;
// const socket = io();
const POSE_CONNECTIONS = [
    [0, 1], [1, 2], [2, 3], [3, 7], [0, 4], [4, 5],
    [5, 6], [6, 8], [9, 10], [11, 12], [11, 13],
    [13, 15], [15, 17], [15, 19], [15, 21], [17, 19],
    [12, 14], [14, 16], [16, 18], [16, 20], [16, 22],
    [18, 20], [11, 23], [12, 24], [23, 24], [23, 25],
    [24, 26], [25, 27], [26, 28], [27, 29], [28, 30],
    [29, 31], [30, 32], [27, 31], [28, 32]
  ];
const init = async () => {
    const stats = new Stats();
    document.body.appendChild(stats.dom);
    const signal_container = document.getElementById("signal_container");
    const video = document.getElementById("input_video");
    const canvasElement = document.getElementById("output_canvas");
    const canvasmask = document.getElementById("mask_canvas");
    const local_vid = document.getElementById("local_vid");
    const canvasCtx = canvasElement.getContext("2d");
    canvasElement.style.display = 'block';
    canvasmask.style.display = 'block';
    local_vid.style.display = 'none';
    signal_container.style.display = 'block';
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
        }
    );
    const poseLandmarker = await PoseLandmarker.createFromOptions(
        vision,
        {
            baseOptions: {
                modelAssetPath: "static/pose_landmarker_full.task",
                delegate: "CPU"
            },
            numPoses: 1
        }
    );
    await handLandmarker.setOptions({ runningMode: "video" });
    await poseLandmarker.setOptions({ runningMode: "video" });
    let lastVideoTime = -1;
    const renderLoop = () => {
        stats.begin(); // Bắt đầu thu thập thông tin
        if (!isRunning) return;
        canvasElement.width = video.videoWidth/1.5;
        canvasElement.height = video.videoHeight/1.5;
        let startTimeMs = performance.now();
        if (video.currentTime > 0 && video.currentTime !== lastVideoTime) {
            const results = handLandmarker.detectForVideo(video, startTimeMs);
            const poseLandmarkerResult = poseLandmarker.detectForVideo(video, startTimeMs);
            lastVideoTime = video.currentTime;
            canvasCtx.save();
            canvasCtx.clearRect(0, 0, canvasElement.width, canvasElement.height);
            canvasCtx.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);
            if (results.landmarks) {
                for (const landmarks of results.landmarks) {
                    drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, {
                        color: "#ffffff",
                        lineWidth: 2
                    });
                    drawLandmarks(canvasCtx, landmarks, { color: "#00d9ff", lineWidth: 1 });}}
            if (poseLandmarkerResult.landmarks) {
                for (const landmarks of poseLandmarkerResult.landmarks) {
                    drawConnectors(canvasCtx, landmarks, POSE_CONNECTIONS, {
                        color: "#ffffff",
                        lineWidth: 2
                    });
                    drawLandmarks(canvasCtx, landmarks, { color: "#00d9ff", lineWidth: 1 });}}
            let combinedResults = {
                handLandmarks: results ? results : [],
                poseLandmarks: poseLandmarkerResult.landmarks ? poseLandmarkerResult.landmarks : []
            };
            try {
                fetch('https://27.81.58.107:5000/combined_landmark_endpoint', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        ...combinedResults,
                        sid: socket.id,
                    }),
                })
                .then(response => response.json())
                    .then(data => console.log(data))
                    .catch(error => console.error('Error:', error));

            } catch (error) {
                console.error('Error:', error);
            }
            canvasCtx.restore();
        }
        stats.end();
        if (isRunning) {
            requestID = requestAnimationFrame(renderLoop);
        }
    };
    renderLoop();
    };
    init();
};
const stopLandmarking = () => {
    isRunning = false;
    cancelAnimationFrame(requestID); // Hủy requestAnimationFrame
    // Dừng stream camera nếu cần
    const video = document.getElementById("input_video");
    const canvas = document.getElementById("output_canvas");
    const canvasmask = document.getElementById("mask_canvas");
    const local_vid = document.getElementById("local_vid");
    const signal_container = document.getElementById("signal_container");
    canvas.style.display = 'none';
    canvasmask.style.display = 'none';
    local_vid.style.display = 'block';
    signal_container.style.display = 'none';
    const stream = video.srcObject;
    const tracks = stream.getTracks();
    tracks.forEach(track => track.stop());
  };
  
  // Tìm nút bằng ID và thêm sự kiện click
  const startButton = document.getElementById('start-button');
  startButton.addEventListener('click', startLandmarking);
  
  const stopButton = document.getElementById('stop-button');
  stopButton.addEventListener('click', stopLandmarking);



  
