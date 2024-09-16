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
        resultDiv.innerHTML = `<h2>Analysis Result:</h2><p>${data.grading_result.final_grade}</p>`;
        
        // Display the grade in the modal
        const gradeResult = `Your final grade is: ${data.grading_result.final_grade} (${data.grading_result.percentage}%)`;
        document.getElementById('grade-result').innerText = gradeResult;

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
    })
    .catch(error => {
        console.error('Error:', error);
        resultDiv.innerHTML = `<p style="color:red;">Error analyzing resume.</p>`;
    });
});
