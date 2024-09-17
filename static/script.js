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
        }

        // Close the modal when the user clicks anywhere outside of the modal
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        }

        // Handle the download of feedback
        document.getElementById('download-feedback').addEventListener('click', function() {
            let feedbackContent = `Grade: ${data.grading_result.final_grade} (${data.grading_result.percentage}%)\n\nFeedback:\n`;
            
            Object.keys(data.grading_result.grades).forEach(criterion => {
                feedbackContent += `\n${criterion}:\n${data.grading_result.grades[criterion].feedback}\n`;
            });

            // Create a blob and trigger a download
            const blob = new Blob([feedbackContent], { type: 'text/plain' });
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = 'resume_feedback.txt';
            link.click();
        });
    })
    .catch(error => {
        console.error('Error:', error);
        resultDiv.innerHTML = `<p style="color:red;">Error analyzing resume.</p>`;
    });
});
