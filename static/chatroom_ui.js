var myVideo;

document.addEventListener("DOMContentLoaded", (event) => {
    myVideo = document.getElementById("local_vid");
    myVideo.onloadeddata = () => { console.log("W,H: ", myVideo.videoWidth, ", ", myVideo.videoHeight); };
    var muteBttn = document.getElementById("mute_icon");
    var muteVidBttn = document.getElementById("vid_mute_icon");
    // var callEndBttn = document.getElementById("call_end");

    muteBttn.addEventListener("click", (event)=>{
        // Nếu audio đang được kích hoạt thì tắt, và ngược lại.
        audioMuted = !audioMuted;
        setAudioMuteState(audioMuted);        
    });    
    muteVidBttn.addEventListener("click", (event)=>{
        // Nếu video đang được kích hoạt thì tắt, và ngược lại.
        videoMuted = !videoMuted;
        setVideoMuteState(videoMuted);
        // dòng này để tắt/mở video và ẩn/hiện thẻ video
        if (videoMuted) {
            myVideo.pause(); // Dừng video
            myVideo.style.display = "none"; // Ẩn thẻ video
        } else {
            myVideo.play(); // Phát video
            myVideo.style.display = "block"; // Hiển thị thẻ video
        }       
    });    
    
});

//tạo ra một phần tử video mới với element_id làm ID và tự động phát video.
function makeVideoElementCustom(element_id, display_name) {
    let vid = document.createElement("video");
    vid.id = "vid_" + element_id;
    vid.autoplay = true;
    return vid;
}
//thêm phần tử video mới vào trong khối có ID là "video_grid"
function addVideoElement(element_id, display_name) {
    document.getElementById("video_grid").appendChild(makeVideoElementCustom(element_id, display_name));
    checkVideoLayout();
}
//xoá video với element_id tương ứng 
function removeVideoElement(element_id) {
    let v = getVideoObj(element_id);
    if (v.srcObject) {
        v.srcObject.getTracks().forEach(track => track.stop());
    }
    v.removeAttribute("srcObject");
    v.removeAttribute("src");

    document.getElementById("vid_" + element_id).remove();
}

function getVideoObj(element_id) {
    return document.getElementById("vid_" + element_id);
}

function setAudioMuteState(flag) {
    let local_stream = myVideo.srcObject;
    console.log("setAudioMuteState: ", local_stream);
    local_stream.getAudioTracks().forEach((track) => { track.enabled = !flag; });
    // switch button icon
    document.getElementById("mute_icon").innerText = (flag) ? "mic_off" : "mic";
}
function setVideoMuteState(flag) {
    let local_stream = myVideo.srcObject;
    local_stream.getVideoTracks().forEach((track) => { track.enabled = !flag; });
    // switch button icon
    document.getElementById("vid_mute_icon").innerText = (flag) ? "videocam_off" : "videocam";
}
