
let APP_ID = "d65a860821a440a59c10ce2a70ba7b61"
let token = null;
let uid = Math.floor(Math.random() * 10000000).toString();
let localStream;
let remoteStream;
let peerConnection;
let ws;

const channel = 'signalling'
const methods = {
    method: "method",
    login: 'login',
    sendOffer: 'sendOffer',
    receiveOffer: 'receiveOffer',
    userJoined: "userJoined",
    data: "data"
}
const servers = {
    iceServers: [
        {
            urls: ["stun:stun.l.google.com:19302",
                "stun:stun1.l.google.com:19302",
                "stun:stun2.l.google.com:19302",
                "stun:stun3.l.google.com:19302",
                "stun:stun4.l.google.com:19302"]
        }
    ]
}

let init = async () => {
    console.log('my id is ', uid);
    await getVideo();
    await createOffer();
    await initializeWebsocket();
    login(ws);

}
function connect(url) {
    return new Promise((resolve, reject) => {
        const ws = new WebSocket(url);
        ws.onopen = () => resolve(ws);
        ws.onerror = reject;
    });
}
const initializeWebsocket = (async () => {
    try {
        ws = await connect('ws://192.168.30.10:8765');
        console.log("WebSocket connection opened!");
        ws.onmessage = onMessage;
    } catch (error) {
        console.error("WebSocket connection error:", error);
    }
});

const getVideo = async () => {
    try {
        localStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false })
        document.getElementById('user-1').srcObject = localStream;
    } catch (e) {
        console.log("Can't get video: " + e);
        var h2 = document.createElement("h2");
        h2.style = "color:white"
        h2.textContent = "Failed to access camera!";
        document.getElementById('user-1').textContent = "Failed to access camera!";
    }
}
// Handle incoming messages from the server
const onMessage = (event) => {
    console.log('Received message: ', event.data);
    let h4 = document.createElement('h4');
    h4.textContent = event.data;
    document.getElementById('messages').appendChild(h4);
    handleMessage(event.data);
    // You can process the received message here (e.g., display it or perform actions)
};

const login = async (ws) => {
    ws.send(JSON.stringify({ method: methods.login, uid: uid }));
}

let handleUserJoined = async (MemberId) => {
    console.log('A new user joined channel: ', MemberId);
}

const handleMessage = async (message) => {
    message = JSON.parse(message);
    console.log('handling message ', message, 'with', methods.userJoined)
    if (message[methods.method] === methods.userJoined) {
        let offerData = { "method": "sendOffer", "data": await peerConnection.createOffer() };
        console.log('sending message', offerData)
        sendMessage(offerData)

    } else if (message[methods.method]) {

    }
}
const sendMessage = async (data) => {
    // data["uid"] = uid;
    ws.send(data);
}
let createOffer = async () => {
    try {
        peerConnection = new RTCPeerConnection(servers);
        remoteStream = new MediaStream();
        document.getElementById('user-2').srcObject = remoteStream;
        localStream.getTracks().forEach((track) => {
            peerConnection.addTrack(track, localStream);
        });
        peerConnection.ontrack = (event) => {
            event.streams[0].getTracks().forEach((track) => {
                remoteStream.addTrack()
            })
        }
        peerConnection.onicecandidate = async (event) => {
            if (event.candidate) {
                console.log('NEW ICE candidate: ', event.candidate)
            }
        }
        let offer = await peerConnection.createOffer();
        await peerConnection.setLocalDescription(offer);
        console.log('Offer: ', offer);
    } catch (e) {
        console.error('FAILED TO CREATE OFFER');
    }
}

window.onload = () => {
    init();
}