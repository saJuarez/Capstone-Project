let feedbackData = null;

document.addEventListener('DOMContentLoaded', function () {
    /**
     * Helper functions
     */
    function openModal(modal) {
        modal.style.display = 'flex';
        modal.classList.add('open');
    }

    function closeModal(modal) {
        modal.style.display = 'none';
        modal.classList.remove('open');
    }

    function closeIfClickedOutside(target, element, icon) {
        if (element && element.classList.contains('open') && target !== element && !element.contains(target) && target !== icon && (!icon || !icon.contains(target))) {
            closeModal(element);
        }
    }

    // Close modals if clicked outside
    window.addEventListener('click', function (event) {
        closeIfClickedOutside(event.target, settingsModal, settingsLink);
        closeIfClickedOutside(event.target, loginModal, null);

        if (!sideMenu.contains(event.target) && !sidebarIcon.contains(event.target)) {
            sideMenu.classList.remove('open');
        }
    });



    function handleFetchResponse(response) {
        if (!response.ok) {
            console.error(`Error: ${response.status} ${response.statusText}`);
            return response.json().then(errorData => {
                throw new Error(errorData.message || 'An unknown error occurred');
            });
        }
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

    // Sidebar toggle handling
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

    // Error Modal handling
    const errorModal = document.getElementById('error-modal');
    const errorMessage = document.getElementById('error-message');

    function showError(message) {
        errorMessage.textContent = message;
        openModal(errorModal);
    }

    window.addEventListener('click', function (event) {
        if (event.target === errorModal) {
            closeModal(errorModal);
        }
    });

    // Settings Modal
    const settingsLink = document.getElementById('settings-link');
    const settingsModal = document.getElementById('settings-modal');

    if (settingsLink) {
        settingsLink.addEventListener('click', function (event) {
            event.preventDefault();

            // Check sessionStorage instead of fetching '/settings' route if possible
            if (sessionStorage.getItem('loggedIn') === 'true') {
                openModal(settingsModal);
            } else {
                showError('You must be logged in to access settings.');
            }
        });
    }

    window.addEventListener('click', function (event) {
        if (settingsModal && event.target === settingsModal) {
            closeModal(settingsModal);
        }
    });

    // Setting tabs switching logic
    const tabLinks = document.querySelectorAll('.tab-link');
    const tabContents = document.querySelectorAll('.tab-content');

    tabLinks.forEach(link => {
        link.addEventListener('click', function () {
            // Remove active class from all tabs and tab contents
            tabLinks.forEach(tab => tab.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

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
    const changePasswordForm = document.getElementById('change-password-form');

    if (changePasswordButton) {
        changePasswordButton.addEventListener('click', function () {
            // Toggle the visibility of the password form
            passwordFields.style.display = passwordFields.style.display === 'none' ? 'block' : 'none';
        });
    }

    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const userIdElement = document.getElementById('user_id');
            if (!userIdElement) {
                console.error("User ID element is not found.");
                return;
            }

            const userId = userIdElement.value;
            const oldPassword = document.getElementById('old-password').value;
            const newPassword = document.getElementById('new-password').value;
            const confirmPassword = document.getElementById('confirm-password').value;

            if (newPassword !== confirmPassword) {
                alert('New password and confirm password do not match.');
                return;
            }

            const formData = new FormData();
            formData.append('user_id', userId);
            formData.append('old_password', oldPassword);
            formData.append('new_password', newPassword);

            fetch('/update-password', {
                method: 'POST',
                body: formData
            })
                .then(response => {
                    if (!response.ok) {
                        return response.text().then(errorText => { throw new Error(errorText); });
                    }
                    return response.json();
                })
                .then(data => {
                    if (data.message) {
                        alert(data.message); // Show alert message to re-login
                        sessionStorage.removeItem('loggedIn'); // Clear sessionStorage
                        sessionStorage.removeItem('user_id');

                        // Refresh the page to prompt the user to log in again
                        window.location.reload();
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    alert('An error occurred: ' + error.message);
                });
        });
    }

    // Show sign-up modal on click
    const signUpButton = document.getElementById('sign-up-button');
    const signUpModal = document.getElementById('sign-up-modal');

    if (signUpButton && signUpModal) {
        signUpButton.addEventListener('click', function (event) {
            event.preventDefault();
            closeModal(document.getElementById('login-modal'));
            openModal(signUpModal);
        });
    }

    // Fetch login status from backend to sync with session storage in frontend
    fetch('/api/check-login-status')
        .then(response => response.json())
        .then(data => {
            if (data.logged_in) {
                sessionStorage.setItem('loggedIn', 'true');
                closeModal(document.getElementById('login-modal')); // Close login modal if user is
            }                                                       // logged in
        })
        .catch(error => console.error('Error checking login status:', error));

    // Check if user is logged in. If not, show login modal
    const loginStatus = sessionStorage.getItem('loggedIn');
    const loginModal = document.getElementById('login-modal');

    if (loginStatus === 'true' && loginModal) {
        closeModal(loginModal);
    } else if (!loginStatus && loginModal) {
        openModal(loginModal);
    }

    // Handle form submission for login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async function (event) {
            event.preventDefault();

            const formData = new FormData(loginForm);

            try {
                const response = await fetch('/login', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();  // Wait for the response to be converted to JSON

                // Check if login was successful
                // Store logged-in status and user ID in sessionStorage after login
                if (data.success) {
                    sessionStorage.setItem('loggedIn', 'true');
                    sessionStorage.setItem('user_id', data.user_id);
                    closeModal(document.getElementById('login-modal'));
                    alert('Login successful!');

                    // Populate the user_id field in the password change form
                    const userIdField = document.getElementById('user_id');
                    if (userIdField) {
                        userIdField.value = data.user_id;
                    }
                } else {
                    alert(data.message || 'Login failed. Please check your credentials.');
                }

            } catch (error) {
                console.error('Login error:', error);
                alert('An error occurred during login.');
            }
        });
    }

    // Handle logout
    const logoutButton = document.getElementById('logout-button');
    if (logoutButton) {
        logoutButton.addEventListener('click', function (event) {
            event.preventDefault();
            fetch('/logout')
                .then(response => response.json())
                .then(data => {
                    sessionStorage.removeItem('loggedIn');  // Remove session status on logout
                    alert('You have been logged out.');

                    openModal(document.getElementById('login-modal'));
                })
                .catch(error => {
                    console.error('Logout error:', error);
                    alert('An error occurred during logout.');
                });
        });
    }

    const signUpForm = document.getElementById('sign-up-form');
    if (signUpForm) handleFormSubmit(signUpForm, '/signup', 'Signup successful!');

    // Feedback History click event handling
    const feedbackHistoryLink = document.getElementById('feedback-history-link');
    if (feedbackHistoryLink) {
        feedbackHistoryLink.addEventListener('click', function (event) {
            event.preventDefault(); // Prevent the default navigation behavior

            fetch('/api/check-login-status') // Check login status
                .then(response => response.json())
                .then(data => {
                    if (data.logged_in) {
                        // If logged in, redirect to feedback history page
                        window.location.href = '/feedback-history';
                    } else {
                        // If not logged in, show an alert
                        alert('You must be logged in to view your resume feedback history.');
                    }
                })
                .catch(error => {
                    console.error('Error checking login status:', error);
                    alert('An error occurred while checking login status.');
                });
        });
    }
    // Resume form submit handling
    const resumeForm = document.getElementById('resume-form');
    if (resumeForm) {
        resumeForm.addEventListener('submit', function (event) {
            event.preventDefault();

            const formData = new FormData(this);
            const resultDiv = document.getElementById('analysis-result');

            // Display loading message with animation
            const loadingMessage = document.createElement('p');
            loadingMessage.className = "loading-message"; 
            loadingMessage.textContent = "Analyzing Resume"; 
            resultDiv.innerHTML = ''; 
            resultDiv.appendChild(loadingMessage);

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

                    // Remove loading message and display results
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
});