let feedbackData = null;

document.addEventListener('DOMContentLoaded', function () {
    /**
     * Helper functions
     */
    function openModal(modal) {
        modal.style.display = 'block';
    }

    function closeModal(modal) {
        modal.style.display = 'none';
    }

    function closeIfClickedOutside(target, element, icon) {
        if (element && element.classList.contains('open') && target !== element && !element.contains(target) && target !== icon && !icon.contains(target)) {
            element.classList.remove('open');
        }
    }

    function handleFetchResponse(response) {
        if (!response.ok) throw new Error('Network response was not ok');
        return response.json();
    }

    function handleError(error, message = 'An error occurred.') {
        console.error(error);
        alert(message);
    }

    function handleFormSubmit(form, url, successMessage) {
        form.addEventListener('submit', function (event) {
            event.preventDefault();

            const formData = new FormData(form);
            fetch(url, {
                method: 'POST',
                body: formData
            })
                .then(handleFetchResponse)
                .then(data => {
                    if (data.message === successMessage) {
                        closeModal(form.closest('.modal'));
                        alert(successMessage);
                    } else {
                        alert(data.message);
                    }
                })
                .catch(error => handleError(error, `An error occurred during ${url.split('/').pop()}.`));
        });
    }

    /**
     * Sidebar toggle handling.
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
        closeIfClickedOutside(event.target, sideMenu, sidebarIcon);
    });

    // Open settings modal
    const settingsLink = document.getElementById('settings-link');
    const settingsModal = document.getElementById('settings-modal');
    if (settingsLink && settingsModal) {
        settingsLink.addEventListener('click', function (event) {
            event.preventDefault();
            openModal(settingsModal);
        });
    }

    window.addEventListener('click', function (event) {
        if (settingsModal && event.target === settingsModal) {
            closeModal(settingsModal);
        }
    });

    // Tab switching logic
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');

    tabLinks.forEach(link => {
        link.addEventListener('click', function () {
            // Remove active class from all tabs and tab contents
            tabLinks.forEach(tab => tab.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to the clicked tab and the corresponding tab content
            const tabId = this.getAttribute('data-tab');
            document.getElementById(tabId).classList.add('active');
            this.classList.add('active');
        });
    });

    document.querySelectorAll('.close-modal').forEach(button => {
        button.addEventListener('click', function () {
            const modal = button.closest('.modal');
            closeModal(modal);
        });
    });

    // Toggle password fields when the "Change Password" button is clicked
    const changePasswordButton = document.getElementById('change-password-button');
    const passwordFields = document.getElementById('password-fields');

    document.getElementById('password-fields').addEventListener('submit', function(event) {
        event.preventDefault();
    
        const userId = document.getElementById('id').value; 
        const oldPassword = document.getElementById('old-password').value;
        const newPassword = document.getElementById('new-password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
    
        const data = new FormData();
        data.append('id', userId); 
        data.append('old-password', oldPassword);
        data.append('new-password', newPassword);
        data.append('confirm-password', confirmPassword);
    
        fetch('/update-password', {
            method: 'POST',
            body: data
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });    

    if (changePasswordButton) {
        changePasswordButton.addEventListener('click', function () {
            passwordFields.style.display = passwordFields.style.display === 'none' ? 'block' : 'none';
        });
    }

    /**
     * Show login modal when logout button is clicked.
     */
    const logoutButton = document.getElementById('logout-button');
    const loginModal = document.getElementById('login-modal');

    if (logoutButton) {
        logoutButton.addEventListener('click', function (event) {
            event.preventDefault();
            sideMenu.classList.remove('open');
            openModal(loginModal);
        });
    }

    const closeButtons = document.querySelectorAll('.close-modal');
    closeButtons.forEach(button => {
        button.addEventListener('click', function () {
            const modal = button.closest('.modal');
            closeModal(modal);
        });
    });

    /**
     * Show Sign Up Modal when sign Up button is clicked.
     */
    const signUpButton = document.getElementById('sign-up-button');
    const signUpModal = document.getElementById('sign-up-modal');
    if (signUpButton && signUpModal) {
        signUpButton.addEventListener('click', function (event) {
            event.preventDefault();
            closeModal(loginModal);
            openModal(signUpModal);
        });
    }

    window.addEventListener('click', function (event) {
        const modals = [loginModal, document.getElementById('grade-modal')];
        modals.forEach(modal => {
            if (modal && event.target === modal) {
                closeModal(modal);
            }
        });
    });

    /**
     * Form submission handling.
     */
    const loginForm = document.getElementById('login-form');
    if (loginForm) handleFormSubmit(loginForm, '/login', 'Login successful!');

    const signUpForm = document.getElementById('sign-up-form');
    if (signUpForm) handleFormSubmit(signUpForm, '/signup', 'Signup successful!');

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
                .then(handleFetchResponse)
                .then((data) => {
                    if (!data || !data.grading_result) {
                        console.error('Invalid grading result:', data);
                        resultDiv.innerHTML = `<p style="color:red;">Error in processing resume grading.</p>`;
                        return;
                    }

                    feedbackData = data;

                    resultDiv.innerHTML = `<h2>Analysis Result:</h2><p>Grading Completed</p>`;

                    const gradeResult = `Your final grade is: ${data.grading_result.final_grade} (${data.grading_result.percentage}%)`;
                    document.getElementById('grade-result').innerText = gradeResult;

                    const feedbackList = document.getElementById('feedback-list');
                    feedbackList.innerHTML = '';

                    Object.keys(data.grading_result.grades).forEach((criterion) => {
                        const feedbackItem = document.createElement('li');
                        feedbackItem.innerHTML = `<strong>${criterion}:</strong> ${data.grading_result.grades[criterion].feedback}`;
                        feedbackList.appendChild(feedbackItem);
                    });

                    const gradeModal = document.getElementById('grade-modal');
                    if (gradeModal) {
                        openModal(gradeModal);
                    }

                    const downloadButton = document.getElementById('download-feedback');
                    if (downloadButton) {
                        downloadButton.addEventListener('click', function () {
                            let feedbackContent = `Grade: ${data.grading_result.final_grade} (${data.grading_result.percentage}%)\n\nFeedback:\n`;

                            Object.keys(data.grading_result.grades).forEach((criterion) => {
                                feedbackContent += `\n${criterion}:\n${data.grading_result.grades[criterion].feedback}\n`;
                            });

                            const { jsPDF } = window.jspdf;
                            const doc = new jsPDF();
                            doc.text(feedbackContent, 10, 10);
                            doc.save('resume_feedback.pdf');
                        });
                    }
                })
                .catch((error) => {
                    handleError(error, 'Error analyzing resume.');
                    resultDiv.innerHTML = `<p style="color:red;">Error analyzing resume.</p>`;
                });
        });
    }

    /**
     * Chat Box handling.
     */
    const sendChatButton = document.getElementById('send-chat');
    if (sendChatButton) {
        sendChatButton.addEventListener('click', function () {
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
                .then(handleFetchResponse)
                .then(data => {
                    if (data.error) {
                        throw new Error(data.error);
                    }
                    chatLog.innerHTML += `<div><strong>AI:</strong> ${data.reply}</div>`;
                    document.getElementById('chat-input').value = '';
                })
                .catch(error => {
                    handleError(error, 'Error sending message.');
                    chatLog.innerHTML += `<div style="color:red;">Error sending message: ${error.message}</div>`;
                });
        });
    }
});