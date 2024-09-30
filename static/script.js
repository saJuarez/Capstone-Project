let feedbackData = null; 

// Resume Upload Form
document.getElementById('resume-form').addEventListener('submit', function(event) {
    event.preventDefault();

    const formData = new FormData(this);
    const resultDiv = document.getElementById('analysis-result');
    
    // Display loading animation
    resultDiv.innerHTML = `<div class="loading"></div>Analyzing resume...`;

    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        console.log('Upload response status:', response.status); // Log response status
        return response.json();  // Parse JSON from the response
    })
    .then(data => {
        console.log('Received grading result:', data); // Log the data received from backend
        
        if (!data || !data.grading_result) {
            console.error('Invalid grading result:', data);
            resultDiv.innerHTML = `<p style="color:red;">Error in processing resume grading.</p>`;
            return;
        }

        // Store the feedback data globally for PDF generation
        feedbackData = data;

        // Clear loading and display result header
        resultDiv.innerHTML = `<h2>Analysis Result:</h2><p>Grading Completed</p>`;

        // Display the grade in the modal
        const gradeResult = `Your final grade is: ${data.grading_result.final_grade} (${data.grading_result.percentage}%)`;
        document.getElementById('grade-result').innerText = gradeResult;

        // Clear previous feedback
        const feedbackList = document.getElementById('feedback-list');
        feedbackList.innerHTML = '';

        // Add feedback for each criterion
        Object.keys(data.grading_result.grades).forEach(criterion => {
            const feedbackItem = document.createElement('li');
            feedbackItem.innerHTML = `<strong>${criterion}:</strong> ${data.grading_result.grades[criterion].feedback}`;
            feedbackList.appendChild(feedbackItem);
        });

        // Show the modal
        const modal = document.getElementById('gradeModal');
        modal.style.display = "block";

        // Close the modal when the user clicks on <span> (x)
        document.querySelector(".close").onclick = function() {
            modal.style.display = "none";
        };

        // Close the modal when the user clicks anywhere outside of the modal
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        };
    })
    .catch(error => {
        console.error('Error analyzing resume:', error);
        resultDiv.innerHTML = `<p style="color:red;">Error analyzing resume.</p>`;
    });
});

// Chat Box Send Button
document.getElementById('send-chat').addEventListener('click', function() {
    const input = document.getElementById('chat-input').value;
    const chatLog = document.getElementById('chat-log');
    
    if (!input.trim()) return;  // Prevent sending empty messages

    chatLog.innerHTML += `<div><strong>You:</strong> ${input}</div>`;
    
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input }) 
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Chat response not okay');
        }
        return response.json(); // Parse the response as JSON
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        chatLog.innerHTML += `<div><strong>AI:</strong> ${data.reply}</div>`;
        document.getElementById('chat-input').value = '';  // Clear the input
    })
    .catch(error => {
        console.error('Error:', error);
        chatLog.innerHTML += `<div style="color:red;">Error sending message: ${error.message}</div>`;
    });
});

// Download Feedback as PDF
document.getElementById('download-feedback').addEventListener('click', function() {
    if (!feedbackData) {
        console.error('No feedback data available to download.');
        return;
    }

    let feedbackContent = `Grade: ${feedbackData.grading_result.final_grade} (${feedbackData.grading_result.percentage}%)\n\nFeedback:\n`;
    
    // Collect feedback for each criterion
    Object.keys(feedbackData.grading_result.grades).forEach(criterion => {
        feedbackContent += `\n${criterion}:\n${feedbackData.grading_result.grades[criterion].feedback}\n`;
    });

    // Create a new PDF document using jsPDF
    const { jsPDF } = window.jspdf;
    const doc = new jsPDF();

    // Add content to the PDF
    doc.text(feedbackContent, 10, 10);

    // Save the PDF
    doc.save('resume_feedback.pdf');
});
