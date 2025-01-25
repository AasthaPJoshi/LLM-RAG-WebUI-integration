document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('messageForm');
    const messageInput = document.getElementById('message');
    const voiceInputButton = document.getElementById('voiceInputButton');
    const speakerButton = document.getElementById('speakerButton');
    let recognizing = false;
    let recognition;

    if ('webkitSpeechRecognition' in window) {
        recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = function () {
            recognizing = true;
            voiceInputButton.textContent = 'Listening...';
        };

        recognition.onend = function () {
            recognizing = false;
            voiceInputButton.textContent = 'Voice Input';
        };

        recognition.onresult = function (event) {
            messageInput.value = event.results[0][0].transcript;
        };

        voiceInputButton.addEventListener('click', function () {
            if (recognizing) {
                recognition.stop();
                return;
            }
            recognition.start();
        });
    } else {
        voiceInputButton.disabled = true;
        voiceInputButton.textContent = 'Voice Input Not Supported';
    }

    speakerButton.addEventListener('click', function () {
        const msg = new SpeechSynthesisUtterance(messageInput.value);
        window.speechSynthesis.speak(msg);
    });

    form.addEventListener('submit', function (e) {
        e.preventDefault();
        const message = messageInput.value;

        fetch('/send', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: new URLSearchParams({ message })
        })
        .then(response => response.json())
        .then(data => {
            const responseElement = document.createElement('div');
            responseElement.classList.add('message', 'llm');
            responseElement.innerHTML = `<strong>LLM:</strong> ${data.response}`;
            document.getElementById('conversation').appendChild(responseElement);
            messageInput.value = '';
        });
    });
});
