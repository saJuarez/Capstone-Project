document.getElementById('resume-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    const resultDiv = document.getElementById('analysis-result');
    
    
    resultDiv.innerHTML = `<div class="loading"></div>Analyzing resume...`;

    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
        resultDiv.innerHTML = `<h2>Analysis Result:</h2><p>${data.analysis}</p>`;
    })
    .catch(error => {
        console.error('Error:', error);
        resultDiv.innerHTML = `<p style="color:red;">Error analyzing resume.</p>`;
    });
});

// AI Chat Box
document.getElementById('send-chat').addEventListener('click', function() {
    const input = document.getElementById('chat-input').value;
    const chatLog = document.getElementById('chat-log');
    
    if (!input.trim()) return; 
    
  
    chatLog.innerHTML += `<div><strong>You:</strong> ${input}</div>`;
    
    
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input })
    })
    .then(response => response.json())
    .then(data => {
        
        chatLog.innerHTML += `<div><strong>AI:</strong> ${data.reply}</div>`;
        document.getElementById('chat-input').value = ''; // Clear input field  
    })
    .catch(error => {
        console.error('Error:', error);
        chatLog.innerHTML += `<div style="color:red;">Error sending message.</div>`;
    });
});
