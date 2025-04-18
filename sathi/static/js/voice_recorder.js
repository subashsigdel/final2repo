let mediaRecorder;
let audioChunks = [];
let isRecording = false;

document.addEventListener("keydown", async function (e) {
    if (e.code === "Space" && !isRecording) {
        isRecording = true;
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);

        mediaRecorder.ondataavailable = (e) => {
            audioChunks.push(e.data);
        };

        mediaRecorder.onstop = async () => {
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append('audio_file', audioBlob, 'recording.wav');

            // Upload the audio file to the server
            fetch('/upload_audio/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken() // Ensure CSRF protection
                },
                body: formData
            })
            .then(res => res.json())
            .then(data => {
                console.log("Upload response:", data);

                // Check if the response contains a 'redirect' key
                if (data.redirect) {
                    // If there's a redirect URL, navigate to it
                    window.location.href = data.redirect;
                } else {
                    // Fallback to audio playback (if there's no redirect)
                    if (document.getElementById("audioPlayback")) {
                        const audioUrl = URL.createObjectURL(audioBlob);
                        document.getElementById("audioPlayback").src = audioUrl;
                    }
                }
            })
            .catch(err => console.error("Upload error:", err));

            audioChunks = [];
        };

        mediaRecorder.start();
        console.log("Recording started...");
    }
});

document.addEventListener("keyup", function (e) {
    if (e.code === "Space" && isRecording) {
        mediaRecorder.stop();
        isRecording = false;
        console.log("Recording stopped.");
    }
});

// Helper to get CSRF token
function getCSRFToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        if (cookie.trim().startsWith('csrftoken=')) {
            return cookie.trim().substring('csrftoken='.length);
        }
    }
    return '';
}
