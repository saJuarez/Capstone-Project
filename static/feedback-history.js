document.addEventListener('DOMContentLoaded', function () {
    /**
     * Sidebar functionality
     */
    const sidebarIcon = document.getElementById('sidebar-icon');
    const sideMenu = document.getElementById('side-menu');
    const closeMenu = document.getElementById('close-menu');

    if (sidebarIcon) {
        sidebarIcon.addEventListener('click', function () {
            sideMenu.classList.toggle('open');
        });
    }

    if (closeMenu) {
        closeMenu.addEventListener('click', function () {
            sideMenu.classList.remove('open');
        });
    }

    window.addEventListener('click', function (event) {
        if (!sideMenu.contains(event.target) && !sidebarIcon.contains(event.target)) {
            sideMenu.classList.remove('open');
        }
    });

    /**
     * Helper functions for Base64 encoding/decoding that handle Unicode characters
     */
    function encodeToBase64(str) {
        return btoa(encodeURIComponent(str).replace(/%([0-9A-F]{2})/g, (_, p1) =>
            String.fromCharCode('0x' + p1)
        ));
    }

    function decodeFromBase64(str) {
        return decodeURIComponent(atob(str).split('').map(c =>
            '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2)
        ).join(''));
    }

    // Check if the user is logged in; if not, redirect to the homepage
    fetch('/api/check-login-status')
        .then(response => response.json())
        .then(data => {
            console.log("Fetched feedback data:", data);
            if (!data.logged_in) {
                window.location.href = '/';
            }
        })
        .catch(error => console.error('Error verifying login status:', error));

    /**
     * Fetch and display feedback history
     */
    const feedbackHistoryContainer = document.getElementById('feedback-history-content');
    const feedbackModal = document.getElementById('feedback-modal');
    const feedbackModalContent = document.getElementById('feedback-modal-content');
    const closeModalButton = feedbackModal.querySelector('.close-modal');

    fetch('/api/feedback-history')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                feedbackHistoryContainer.innerHTML = `<p>${data.error}</p>`;
            } else if (data.feedbacks.length === 0) {
                feedbackHistoryContainer.innerHTML = '<p>No feedback history found yet.</p>';
            } else {
                let feedbackList = '<ul>';
                data.feedbacks.forEach(item => {
                    const feedbackJson = encodeToBase64(JSON.stringify(item.feedback)); // Safely encode JSON
                    
                    feedbackList += `
                        <li class="feedback-card">
                            <h2>Feedback from ${item.upload_date}</h2>
                            <button class="button view-feedback" data-feedback="${feedbackJson}">View Feedback</button>
                            <button class="button download-feedback" data-feedback="${feedbackJson}">Download Feedback</button>
                        </li>`;
                });
                
                feedbackList += '</ul>';
                feedbackHistoryContainer.innerHTML = feedbackList;

                // Event listener for view feedback button
                document.querySelectorAll('.view-feedback').forEach(button => {
                    button.addEventListener('click', function () {
                        try {
                            const feedbackData = decodeFromBase64(this.getAttribute('data-feedback')); // Decode JSON
                            const feedback = JSON.parse(feedbackData); // Parse JSON

                            feedbackModalContent.innerHTML = formatFeedback(feedback);
                            feedbackModal.style.display = 'flex';
                        } catch (error) {
                            console.error('Error parsing feedback data:', error);
                        }
                    });
                });

                // Event listener for download feedback button
                document.querySelectorAll('.download-feedback').forEach(button => {
                    button.addEventListener('click', function () {
                        try {
                            const feedbackData = decodeFromBase64(this.getAttribute('data-feedback')); 
                            const feedback = JSON.parse(feedbackData); // Parse JSON
                            downloadFeedback(feedback);
                        } catch (error) {
                            console.error('Error parsing feedback data:', error);
                        }
                    });
                });
            }
        })
        .catch(error => {
            console.error('Error fetching feedback history:', error);
            feedbackHistoryContainer.innerHTML = '<p>Error fetching feedback history.</p>';
        });

    // Close modal when the close button is clicked
    closeModalButton.addEventListener('click', function () {
        feedbackModal.style.display = 'none';
    });

    // Close modal when clicking outside the modal content
    window.addEventListener('click', function (event) {
        if (event.target === feedbackModal) {
            feedbackModal.style.display = 'none';
        }
    });
});

/**
 * Function to format the feedback object into a readable string
 */
function formatFeedback(feedback) {
    let formattedFeedback = `<strong>Final Grade: ${feedback.final_grade}</strong><br><br>`;
    formattedFeedback += "<strong>Grades:</strong><ul>";
    Object.keys(feedback.grades).forEach(criteria => {
        formattedFeedback += `
            <li>
                <strong>${criteria}</strong>:<br>
                <strong>Feedback:</strong> ${feedback.grades[criteria].feedback}<br>
                <strong>Score:</strong> ${feedback.grades[criteria].score}
            </li><br>
        `;
    });
    formattedFeedback += "</ul>";
    return formattedFeedback;
}

/**
 * Function to download the feedback as a PDF
 */
function downloadFeedback(feedback) {
    let feedbackContent = `Final Grade: ${feedback.final_grade}\n\nFeedback:\n`;
    Object.keys(feedback.grades).forEach(criteria => {
        feedbackContent += `\n${criteria}:\n${feedback.grades[criteria].feedback}\nScore: ${feedback.grades[criteria].score}\n`;
    });

    const { jsPDF } = window.jspdf;
    if (!jsPDF) {
        console.error('jsPDF library is not loaded');
        return;
    }
    const doc = new jsPDF();
    doc.text(feedbackContent, 10, 10);
    doc.save('resume_feedback.pdf');
}