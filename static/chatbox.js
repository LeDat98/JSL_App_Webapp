

socket.emit('join-roomchat', {room_id: myRoomID});
socket.on('message', data => {
// Tạo div cha
const msgDiv = document.createElement("div");
msgDiv.className = data['sender'] === myName ? "message-box sender" : "message-box";
// Tạo div con
const subMsgDiv = document.createElement("div");
const subAvatar = document.createElement("div");
const subAvatarimg = document.createElement("img");
const AIimg = document.createElement("img");
const mess_input = document.getElementById("message-input"); 
console.log(data['sender'])
if (data['type']==='OS'){
    console.log('from System')
    msgDiv.className = 'message-box';
    subAvatarimg.className = 'sub-avatar-img';
    subAvatarimg.src = "/static/images/bot.png";
    subMsgDiv.className = "sub-message-box";
    subMsgDiv.textContent = data['message'];
    msgDiv.appendChild(subAvatarimg);
    msgDiv.appendChild(subMsgDiv);
    // Thêm div cha vào phần tử có id là "messages"
    const messagesDiv = document.getElementById("messages");
    messagesDiv.appendChild(msgDiv);
    // Cuộn đến phần cuối của messagesDiv
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
else if(data['type']==='human'){
    subAvatar.className = data['sender'] === myName ? "sub-avatar sender" : "sub-avatar";
    // Lấy chữ cái đầu tiên của data['sender']
    const firstLetter = data['sender'].charAt(0).toUpperCase();
    // Gán chữ cái đầu tiên vào subAvatar.textContent
    subAvatar.textContent = firstLetter;

    subMsgDiv.className = data['sender'] === myName ? "sub-message-box sender" : "sub-message-box";
    subMsgDiv.textContent = data['message'];
    // Nối div con với div cha
    msgDiv.appendChild(subAvatar);
    msgDiv.appendChild(subMsgDiv);
    if(data['type'] === 'AI'){
        AIimg.className = data['sender'] === myName ? "AI-img sender" : "AI-img";
        AIimg.src = "/static/images/chatbot1.png";
        msgDiv.appendChild(AIimg);
    }
    // Thêm div cha vào phần tử có id là "messages"
    const messagesDiv = document.getElementById("messages");
    messagesDiv.appendChild(msgDiv);
    // Cuộn đến phần cuối của messagesDiv
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
}
else if(data['type'] === 'AI'){
    console.log('AI');
    if(data['message'].length > 1 && data['message'] !== 'Enter' && data['message'] !== 'Delete' ){
        console.log('message: ',data['message']);
        mess_input.value += data['message']+' ';
    }
    else if(data['message'].length === 1 ){
        console.log('message: ',data['message']);
        mess_input.value += data['message'];
    }
    else if(data['message'] === 'Enter'){

    subAvatar.className = data['sender'] === myName ? "sub-avatar sender" : "sub-avatar";
    // Lấy chữ cái đầu tiên của data['sender']
    const firstLetter = data['sender'].charAt(0).toUpperCase();
    // Gán chữ cái đầu tiên vào subAvatar.textContent
    subAvatar.textContent = firstLetter;

    subMsgDiv.className = data['sender'] === myName ? "sub-message-box sender" : "sub-message-box";
    subMsgDiv.textContent = mess_input.value;
    mess_input.value = '';
    // Nối div con với div cha
    msgDiv.appendChild(subAvatar);
    msgDiv.appendChild(subMsgDiv);
    //tạo ảnh AI 
    AIimg.className = data['sender'] === myName ? "AI-img sender" : "AI-img";
    AIimg.src = "/static/images/chatbot1.png";
    msgDiv.appendChild(AIimg);

    // Thêm div cha vào phần tử có id là "messages"
    const messagesDiv = document.getElementById("messages");
    messagesDiv.appendChild(msgDiv);
    // Cuộn đến phần cuối của messagesDiv
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
    }
}
});
//hàm xử lý việc nhấp vào nút gửi tin nhắn
function sendMessage() {
    const message = document.getElementById("message-input").value;
    if(message === ''){
        return
    }
    socket.emit('send-message', {'room_id': myRoomID, 'message': message, 'sender': myName});
    document.getElementById("message-input").value = '';
    // Cuộn đến phần cuối của messagesDiv
    const messagesDiv = document.getElementById("messages");
    messagesDiv.scrollTop = messagesDiv.scrollHeight;
    
}
const input= document.getElementById("message-input");
input.addEventListener("keydown", function(e) {
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
var manager_task = document.getElementById('manager-task');
var chatinputcontainer = document.getElementById('chat-input-container'); 
var toggle_button = document.getElementById('toggle-button');

if (chatWindow.style.width === '1%') {
    chatWindow.style.width = '20%'; // Đặt lại giá trị ban đầu cho chatWindow
    videoGrid.style.maxWidth = '100%'; // Đặt lại giá trị ban đầu cho videoGrid
    messagesDiv.style.visibility = 'visible'; // Hiển thị messagesDiv 
    chatinputcontainer.style.visibility = 'visible';// Hiển thị chatinputcontainer
    manager_task.style.visibility = 'visible';
    toggle_button.style.color = 'white';
    document.getElementById("toggle-button").innerHTML = '<span class="material-icons">arrow_forward_ios</span>';
} else {
    chatWindow.style.width = '1%'; // Thu nhỏ chatWindow xuống 1.5%
    videoGrid.style.maxWidth = '100%'; // Mở rộng videoGrid lên 98.5%
    messagesDiv.style.visibility = 'hidden';// Ẩn messagesDiv
    chatinputcontainer.style.visibility = 'hidden'; // Ẩn chatinputcontainer
    manager_task.style.visibility = 'hidden';
    toggle_button.style.color = 'black';
    document.getElementById("toggle-button").innerHTML = '<span class="material-icons">arrow_back_ios</span>';
}
}