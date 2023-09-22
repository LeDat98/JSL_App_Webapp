

socket.emit('join-roomchat', {room_id: myRoomID});
socket.on('message', data => {
// Tạo div cha
const msgDiv = document.createElement("div");
msgDiv.className = data['sender'] === myName ? "message-box sender" : "message-box";
// Tạo div con
const subMsgDiv = document.createElement("div");
subMsgDiv.className = data['sender'] === myName ? "sub-message-box sender" : "sub-message-box";
subMsgDiv.textContent = data['sender'] + ": " + data['message'];
// Nối div con với div cha
msgDiv.appendChild(subMsgDiv);
// Thêm div cha vào phần tử có id là "messages"
const messagesDiv = document.getElementById("messages");
messagesDiv.appendChild(msgDiv);
// Cuộn đến phần cuối của messagesDiv
messagesDiv.scrollTop = messagesDiv.scrollHeight;

});
//hàm xử lý việc nhấp vào nút gửi tin nhắn
function sendMessage() {
    const message = document.getElementById("message-input").value;
    socket.emit('send-message', {'room_id': myRoomID, 'message': message, 'sender': myName});
    document.getElementById("message-input").value = '';
    // Cuộn đến phần cuối của messagesDiv
    const messagesDiv = document.getElementById("messages");
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
document.getElementById("message-input").addEventListener("keydown", function(e) {
if (e.key === "Enter" && !e.shiftKey) { // Nếu nhấn Enter mà không giữ Shift
e.preventDefault(); // Ngăn không cho phép xuống dòng
sendMessage(); // Gửi tin nhắn
}
});
// hàm xử lý việc nhấp vào nút thu cửa sổ chat và mở cửa sổ chat trở lại 
function toggleChatWindow() {
var chatWindow = document.getElementById('chat-window');
var videoGrid = document.getElementById('video_grid');
var messagesDiv = document.getElementById('messages');
var chatinputcontainer = document.getElementById('chat-input-container');   
if (chatWindow.style.width === '1%') {
    chatWindow.style.width = '25%'; // Đặt lại giá trị ban đầu cho chatWindow
    videoGrid.style.maxWidth = '75%'; // Đặt lại giá trị ban đầu cho videoGrid
    messagesDiv.style.visibility = 'visible'; // Hiển thị messagesDiv 
    chatinputcontainer.style.visibility = 'visible';// Hiển thị chatinputcontainer
    document.getElementById("toggle-button").innerHTML = '<span class="material-icons">arrow_forward_ios</span>';
} else {
    chatWindow.style.width = '1%'; // Thu nhỏ chatWindow xuống 1.5%
    videoGrid.style.maxWidth = '99%'; // Mở rộng videoGrid lên 98.5%
    messagesDiv.style.visibility = 'hidden';// Ẩn messagesDiv
    chatinputcontainer.style.visibility = 'hidden'; // Ẩn chatinputcontainer
    document.getElementById("toggle-button").innerHTML = '<span class="material-icons">arrow_back_ios</span>';
}
}