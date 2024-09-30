document.addEventListener('DOMContentLoaded', function () {
    /**
     * Sidebar toggle functionality.
     */
    const sidebarIcon = document.getElementById('sidebar-icon');
    const sideMenu = document.getElementById('side-menu');
    const closeMenu = document.querySelector('.close-menu');

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
        if (
            sideMenu &&
            sideMenu.classList.contains('open') &&
            event.target !== sideMenu &&
            !sideMenu.contains(event.target) &&
            event.target !== sidebarIcon &&
            !sidebarIcon.contains(event.target)
        ) {
            sideMenu.classList.remove('open');
        }
    });

    /**
     * Show Login Modal on Logout Button Click
     */
    const logoutButton = document.getElementById('logout-button');
    const loginModal = document.getElementById('login-modal');

    if (logoutButton) {
        logoutButton.addEventListener('click', function (event) {
            event.preventDefault(); 
            sideMenu.classList.remove('open'); 
            loginModal.style.display = 'block'; 
        });
    }

    /**
     * Close Login Modal
     */
    const closeLoginButton = loginModal.querySelector('.close-modal');

    if (closeLoginButton) {
        closeLoginButton.addEventListener('click', function () {
            loginModal.style.display = 'none'; 
        });
    }

    /**
     * Show Sign Up Modal on Sign Up Button Click from Login Form
     */
    const signUpButton = document.getElementById('sign-up-button');
    const signUpModal = document.getElementById('sign-up-modal');
    if (signUpButton && signUpModal) {
        signUpButton.addEventListener('click', function (event) {
            event.preventDefault(); 
            loginModal.style.display = 'none'; 
            signUpModal.style.display = 'block'; 
        });

        const closeSignUpButton = signUpModal.querySelector('.close-modal');
        if (closeSignUpButton) {
            closeSignUpButton.addEventListener('click', function () {
                signUpModal.style.display = 'none';
            });
        }
    }

    /**
     * Close Modal when clicking outside the modal content.
     */
    window.addEventListener('click', function (event) {
        if (loginModal && event.target === loginModal) {
            loginModal.style.display = 'none';
        } else if (signUpModal && event.target === signUpModal) {
            signUpModal.style.display = 'none';
        }
    });

    /**
     * Resume form submit handling.
     */
    const resumeForm = document.getElementById('resume-form');
    if (resumeForm) {
        resumeForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const formData = new FormData(this);
            const resultDiv = document.getElementById('analysis-result');

            resultDiv.innerHTML = `<div class="loading"></div>Analyzing resume...`;

            fetch('/upload', {
                method: 'POST',
                body: formData,
            })
                .then((response) => response.json())
                .then((data) => {
                    resultDiv.innerHTML = `<h2>Analysis Result:</h2><p>Grading Completed</p>`;

                    // Display the grade in the modal
                    const gradeResult = `Your final grade is: ${data.grading_result.final_grade} (${data.grading_result.percentage}%)`;
                    document.getElementById('grade-result').innerText = gradeResult;

                    // Clear previous feedback
                    const feedbackList = document.getElementById('feedback-list');
                    feedbackList.innerHTML = '';

                    // Add feedback for each criterion
                    Object.keys(data.grading_result.grades).forEach((criterion) => {
                        const feedbackItem = document.createElement('li');
                        feedbackItem.innerHTML = `<strong>${criterion}:</strong> ${data.grading_result.grades[criterion].feedback}`;
                        feedbackList.appendChild(feedbackItem);
                    });

                    // Show the modal
                    const gradeModal = document.getElementById('grade-modal');
                    if (gradeModal) {
                        gradeModal.style.display = 'block';
                    }

                    // Handle the download of feedback
                    const downloadButton = document.getElementById('download-feedback');
                    if (downloadButton) {
                        downloadButton.addEventListener('click', function () {
                            let feedbackContent = `Grade: ${data.grading_result.final_grade} (${data.grading_result.percentage}%)\n\nFeedback:\n`;

                            Object.keys(data.grading_result.grades).forEach((criterion) => {
                                feedbackContent += `\n${criterion}:\n${data.grading_result.grades[criterion].feedback}\n`;
                            });

                            // Create a blob and trigger a download
                            const blob = new Blob([feedbackContent], { type: 'text/plain' });
                            const link = document.createElement('a');
                            link.href = URL.createObjectURL(blob);
                            link.download = 'resume_feedback.txt';
                            link.click();
                        });
                    }
                })
                .catch((error) => {
                    console.error('Error:', error);
                    resultDiv.innerHTML = `<p style="color:red;">Error analyzing resume.</p>`;
                });
        });
    }
});