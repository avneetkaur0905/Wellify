// Toggle mobile menu
document.addEventListener('DOMContentLoaded', () => {
    const hamburger = document.createElement('div');
    hamburger.className = 'hamburger';
    hamburger.innerHTML = '☰';
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        navbar.appendChild(hamburger);
    } else {
        console.error('Navbar not found');
    }

    hamburger.addEventListener('click', () => {
        const navMenu = document.querySelector('.nav-menu');
        if (navMenu) {
            navMenu.classList.toggle('active');
        }
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', (e) => {
        const dropdowns = document.querySelectorAll('.dropdown');
        dropdowns.forEach(dropdown => {
            const dropdownMenu = dropdown.querySelector('.dropdown-menu');
            if (dropdownMenu && !dropdown.contains(e.target)) {
                dropdownMenu.style.display = 'none';
            }
        });
    });

    // Show dropdown on hover for desktop
    const dropdowns = document.querySelectorAll('.dropdown');
    dropdowns.forEach(dropdown => {
        const dropdownMenu = dropdown.querySelector('.dropdown-menu');
        if (dropdownMenu) {
            dropdown.addEventListener('mouseenter', () => {
                if (window.innerWidth > 768) {
                    dropdownMenu.style.display = 'block';
                }
            });
            dropdown.addEventListener('mouseleave', () => {
                if (window.innerWidth > 768) {
                    dropdownMenu.style.display = 'none';
                }
            });
        }
    });

    // Signup Popup functionality
    const openPopupBtn = document.getElementById('openPopup');
    const signupPopup = document.getElementById('signupPopup');
    const closePopupBtn = document.getElementById('closePopup');
    const signupForm = document.getElementById('signupForm');

    if (openPopupBtn && signupPopup) {
        openPopupBtn.addEventListener('click', (e) => {
            e.preventDefault();
            signupPopup.style.display = 'flex';
        });
    }

    if (closePopupBtn && signupPopup) {
        closePopupBtn.addEventListener('click', () => {
            signupPopup.style.display = 'none';
        });
    }

    if (signupPopup) {
        window.addEventListener('click', (e) => {
            if (e.target === signupPopup) {
                signupPopup.style.display = 'none';
            }
        });
    }

    if (signupForm) {
        signupForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const username = document.getElementById('username')?.value || '';
            const email = document.getElementById('email')?.value || '';
            const contact = document.getElementById('contact')?.value || '';

            console.log('Signup Data:', { username, email, contact });
            alert('Signup successful! Check the console for submitted data.');
            
            signupForm.reset();
            if (signupPopup) signupPopup.style.display = 'none';
        });
    }

    // Login Popup functionality
    const openLoginBtn = document.getElementById('openLogin');
    const loginPopup = document.getElementById('loginPopup');
    const closeLoginBtn = document.getElementById('closeLogin');
    const loginForm = document.getElementById('loginForm');

    if (openLoginBtn && loginPopup) {
        openLoginBtn.addEventListener('click', (e) => {
            e.preventDefault();
            loginPopup.style.display = 'flex';
        });
    }

    if (closeLoginBtn && loginPopup) {
        closeLoginBtn.addEventListener('click', () => {
            loginPopup.style.display = 'none';
        });
    }

    if (loginPopup) {
        window.addEventListener('click', (e) => {
            if (e.target === loginPopup) {
                loginPopup.style.display = 'none';
            }
        });
    }

    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const email = document.getElementById('loginEmail')?.value || '';
            const password = document.getElementById('password')?.value || '';

            console.log('Login Data:', { email, password });
            alert('Login successful! Check the console for submitted data.');
            
            loginForm.reset();
            if (loginPopup) loginPopup.style.display = 'none';
        });
    }

    const forgotPasswordLink = document.querySelector('.forgot-password');
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener('click', (e) => {
            e.preventDefault();
            alert('Password reset instructions will be sent to your email.');
        });
    }

    // Upload Prescription popup
    const uploadPrescriptionLink = document.querySelector('a[href="#scan-prescription"]');
    const uploadPrescriptionPopup = document.getElementById('uploadPrescriptionPopup');
    const closeUploadPrescriptionBtn = document.getElementById('closeUploadPrescription');
    const uploadPrescriptionForm = document.getElementById('uploadPrescriptionForm');
    const uploadButton = document.getElementById('uploadButton');
    const uploadPrescriptionStatus = document.getElementById('uploadStatus');

    if (uploadPrescriptionLink && uploadPrescriptionPopup) {
        uploadPrescriptionLink.addEventListener('click', (e) => {
            e.preventDefault();
            uploadPrescriptionPopup.style.display = 'flex';
        });
    }

    if (closeUploadPrescriptionBtn && uploadPrescriptionPopup) {
        closeUploadPrescriptionBtn.addEventListener('click', () => {
            uploadPrescriptionPopup.style.display = 'none';
        });
    }

    if (uploadPrescriptionPopup) {
        window.addEventListener('click', (e) => {
            if (e.target === uploadPrescriptionPopup) {
                uploadPrescriptionPopup.style.display = 'none';
            }
        });
    }

    if (uploadPrescriptionForm && uploadButton && uploadPrescriptionStatus) {
        uploadPrescriptionForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const prescriptionDetails = document.getElementById('prescriptionDetails')?.value || '';
            const prescriptionFile = document.getElementById('prescriptionFile')?.files[0];

            if (prescriptionFile) {
                const allowedTypes = ['image/jpeg', 'image/png', 'application/pdf'];
                if (!allowedTypes.includes(prescriptionFile.type)) {
                    alert('Please upload a valid image (JPEG, PNG) or PDF file.');
                    return;
                }

                uploadButton.disabled = true;
                uploadPrescriptionStatus.style.display = 'block';
                uploadPrescriptionStatus.textContent = 'Uploading...';

                setTimeout(() => {
                    uploadPrescriptionStatus.textContent = 'Done!';
                    uploadButton.disabled = false;
                    uploadPrescriptionForm.reset();

                    setTimeout(() => {
                        if (uploadPrescriptionPopup) uploadPrescriptionPopup.style.display = 'none';
                        uploadPrescriptionStatus.style.display = 'none';
                    }, 2000);
                }, 2000);
            }
        });
    }

    // Upload Medical Reports popup
    const openUploadReportsLink = document.getElementById("openUploadReports");
    const uploadReportsPopup = document.getElementById("uploadReportsPopup");
    const closeUploadReportsBtn = document.getElementById("closeUploadReports");
    const uploadReportsForm = document.getElementById("uploadReportsForm");
    const uploadReportsStatus = document.getElementById("uploadStatus");

    if (openUploadReportsLink && uploadReportsPopup) {
        openUploadReportsLink.addEventListener("click", (e) => {
            e.preventDefault();
            uploadReportsPopup.style.display = "flex";
        });
    }

    if (closeUploadReportsBtn && uploadReportsPopup) {
        closeUploadReportsBtn.addEventListener("click", () => {
            uploadReportsPopup.style.display = "none";
        });
    }

    if (uploadReportsPopup) {
        window.addEventListener("click", (e) => {
            if (e.target === uploadReportsPopup) {
                uploadReportsPopup.style.display = "none";
            }
        });
    }

    if (uploadReportsForm && uploadReportsStatus) {
        uploadReportsForm.addEventListener("submit", (event) => {
            event.preventDefault();

            const reportDetails = document.getElementById("reportDetails")?.value || '';
            const filesInput = document.getElementById("medicalReports");
            if (!filesInput || !filesInput.files.length) {
                alert('Please select at least one file.');
                return;
            }

            let formData = new FormData();
            const files = filesInput.files;
            for (let i = 0; i < files.length; i++) {
                formData.append("medicalReports", files[i]);
            }
            formData.append("reportDetails", reportDetails);

            uploadReportsStatus.style.display = "block";
            uploadReportsStatus.textContent = "Uploading...";
            console.log("Uploading...");

            fetch("/upload_reports", {
                method: "POST",
                body: formData
            })
            .then(response => {
                if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
                return response.json();
            })
            .then(data => {
                uploadReportsPopup.style.display = "none";
                uploadReportsStatus.style.display = "none";
                    console.log("Files uploaded successfully!", data);
                    alert("Upload successful!");
            })
            .catch(error => {
                uploadReportsStatus.textContent = "Upload failed. Please try again.";
                console.error("Upload failed:", error);
            });
        });
    }

    // Health Trends Popup functionality
    const openHealthTrends = document.getElementById('openHealthTrends');
    const openHealthTrendsCard = document.getElementById('openHealthTrendsCard');
    const healthTrendsPopup = document.getElementById('healthTrendsPopup');
    const closeHealthTrends = document.getElementById('closeHealthTrends');
    const closeTrendsBtn = document.getElementById('closeTrendsBtn');
    const trendsTableHead = document.getElementById('trendsTableHead');
    const trendsTableBody = document.getElementById('trendsTableBody');
    const loadingMessage = document.getElementById('loadingMessage');

    const openPopup = (e) => {
        e.preventDefault();
        console.log('Opening Health Trends Popup');
        if (healthTrendsPopup) {
            healthTrendsPopup.style.display = 'flex';
            loadHealthTrends();
        }
    };

    function loadHealthTrends() {
        if (loadingMessage) loadingMessage.style.display = 'block';
        fetch('/get_health_trends', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' }
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            generateTable(data.health_data, data.years, data.trends);
            if (loadingMessage) loadingMessage.style.display = 'none';
        })
        .catch(error => {
            console.error('Error fetching health trends:', error);
            if (loadingMessage) {
                loadingMessage.textContent = 'Error loading data. Please try again.';
                loadingMessage.style.color = '#FF0000';
            }
        });
    }

    function generateTable(healthData, years, trends) {
        // Generate table header with dynamic years
        let headHtml = '<tr><th>Parameter</th>';
        years.forEach(year => headHtml += `<th>${year}</th>`);
        headHtml += '<th>Trend</th></tr>';
        trendsTableHead.innerHTML = headHtml;

        // Generate table body
        let bodyHtml = '';
        const parameters = [
            "BP Diastolic", "BP Systolic", "Fasting Glucose",
            "HDL Cholesterol", "LDL Cholesterol", "Triglycerides", "eGFR"
        ];
        parameters.forEach(param => {
            bodyHtml += `<tr><td>${param}</td>`;
            years.forEach(year => {
                bodyHtml += `<td>${healthData[param][year]}</td>`;
            });
            bodyHtml += `<td>${trends[param]}</td></tr>`;
        });
        trendsTableBody.innerHTML = bodyHtml;
    }

    if (openHealthTrends && healthTrendsPopup) openHealthTrends.addEventListener('click', openPopup);
    if (openHealthTrendsCard && healthTrendsPopup) openHealthTrendsCard.addEventListener('click', openPopup);
    if (closeHealthTrends && healthTrendsPopup) closeHealthTrends.addEventListener('click', () => healthTrendsPopup.style.display = 'none');
    if (closeTrendsBtn && healthTrendsPopup) closeTrendsBtn.addEventListener('click', () => healthTrendsPopup.style.display = 'none');
    if (healthTrendsPopup) {
        window.addEventListener('click', (e) => {
            if (e.target === healthTrendsPopup) healthTrendsPopup.style.display = 'none';
        });
    }
});