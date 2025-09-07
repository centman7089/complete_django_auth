// main.js

// ===================== Config =====================
const API_BASE = "https://api-test-291i.onrender.com/api/";

// ===================== Token Helpers =====================
function getToken() {
    return localStorage.getItem("access_token");
}

function setTokens(refresh, access) {
    localStorage.setItem("refresh_token", refresh);
    localStorage.setItem("access_token", access);
}

function authHeaders(contentType = "application/json") {
    const headers = {
        "Authorization": `Bearer ${getToken()}`,
    };
    if (contentType) headers["Content-Type"] = contentType;
    return headers;
}

// ===================== UI Helper =====================
function showMessage(elementId, message, isError = false) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.textContent = message;
    el.style.color = isError ? "red" : "green";
}

// ===================== Register =====================
async function registerUser(event) {
    event.preventDefault();

    const data = {
        firstName: document.getElementById("firstName").value,
        lastName: document.getElementById("lastName").value,
        email: document.getElementById("email").value,
        password: document.getElementById("password").value,
        confirm_password: document.getElementById("confirm_password").value,
        phone: document.getElementById("phone").value,
        state: document.getElementById("state").value,
        city: document.getElementById("city").value,
        streetAddress: document.getElementById("streetAddress").value,
        zipCode: document.getElementById("zipCode").value,
        dateOfBirth: document.getElementById("dateOfBirth").value,
        country: document.getElementById("country").value,
    };

    try {
        const res = await fetch(`${API_BASE}register/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        const result = await res.json();
        if (res.ok) showMessage("registerMsg", "Registered successfully! OTP sent to email.");
        else showMessage("registerMsg", JSON.stringify(result), true);
    } catch (error) {
        showMessage("registerMsg", error, true);
    }
}

// ===================== Login =====================
async function loginUser(event) {
    event.preventDefault();

    const data = {
        email: document.getElementById("loginEmail").value,
        password: document.getElementById("loginPassword").value,
    };

    try {
        const res = await fetch(`${API_BASE}login/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        const result = await res.json();
        if (res.ok) {
            setTokens(result.tokens.refresh, result.tokens.access);
            localStorage.setItem("user", JSON.stringify(result.user));
            showMessage("loginMsg", "Login successful!");
            window.location.href = "/profile/"; // redirect after login
        } else {
            showMessage("loginMsg", JSON.stringify(result), true);
        }
    } catch (error) {
        showMessage("loginMsg", error, true);
    }
}

// ===================== Get Profile =====================
async function getMyProfile() {
    try {
        const res = await fetch(`${API_BASE}users/me/`, {
            method: "GET",
            headers: authHeaders(),
        });
        const data = await res.json();
        if (res.ok) {
            document.getElementById("profileName").textContent = `${data.firstName} ${data.lastName}`;
            document.getElementById("profileEmail").textContent = data.email || "";
        } else console.error(data);
    } catch (error) {
        console.error(error);
    }
}

// ===================== Update Profile =====================
async function updateProfile(event) {
    event.preventDefault();

    const data = {
        firstName: document.getElementById("profileFirstName").value,
        lastName: document.getElementById("profileLastName").value,
        phone: document.getElementById("profilePhone").value,
        state: document.getElementById("profileState").value,
        city: document.getElementById("profileCity").value,
        streetAddress: document.getElementById("profileStreetAddress").value,
        zipCode: document.getElementById("profileZipCode").value,
        dateOfBirth: document.getElementById("profileDOB").value,
        country: document.getElementById("profileCountry").value,
    };

    try {
        const res = await fetch(`${API_BASE}users/me/update/`, {
            method: "PUT",
            headers: authHeaders(),
            body: JSON.stringify(data),
        });
        const result = await res.json();
        if (res.ok) showMessage("updateProfileMsg", "Profile updated successfully!");
        else showMessage("updateProfileMsg", JSON.stringify(result), true);
    } catch (error) {
        showMessage("updateProfileMsg", error, true);
    }
}

// ===================== Upload Profile Photo =====================
async function uploadProfilePhoto(event) {
    event.preventDefault();
    const fileInput = document.getElementById("profilePhoto");
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("profilePhoto", file);

    try {
        const res = await fetch(`${API_BASE}profile/photo/`, {
            method: "PUT",
            headers: authHeaders(null), // don't set content-type
            body: formData,
        });
        const result = await res.json();
        if (res.ok) showMessage("profilePhotoMsg", "Profile photo updated!");
        else showMessage("profilePhotoMsg", JSON.stringify(result), true);
    } catch (error) {
        showMessage("profilePhotoMsg", error, true);
    }
}

// ===================== Logout =====================
async function logout() {
    try {
        const refreshToken = localStorage.getItem("refresh_token");

        if (!refreshToken) {
            window.location.href = "/login/";
            return;
        }

        const response = await fetch(`${API_BASE}logout/`, {
            method: "POST",
            headers: authHeaders(),
            body: JSON.stringify({ refresh: refreshToken })
        });

        const data = await response.json();

        if (response.ok) {
            localStorage.clear();
            alert(data.detail || "Logged out successfully!");
            window.location.href = "/login/";
        } else {
            alert(data.detail || "Logout failed.");
        }
    } catch (error) {
        console.error("Logout error:", error);
        alert("Something went wrong. Check console.");
    }
}

// ===================== Event Listeners =====================
document.addEventListener("DOMContentLoaded", () => {
    const registerForm = document.getElementById("registerForm");
    if (registerForm) registerForm.addEventListener("submit", registerUser);

    const loginForm = document.getElementById("loginForm");
    if (loginForm) loginForm.addEventListener("submit", loginUser);

    const updateProfileForm = document.getElementById("updateProfileForm");
    if (updateProfileForm) updateProfileForm.addEventListener("submit", updateProfile);

    const uploadPhotoForm = document.getElementById("uploadPhotoForm");
    if (uploadPhotoForm) uploadPhotoForm.addEventListener("submit", uploadProfilePhoto);

    const logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) logoutBtn.addEventListener("click", logout);

    getMyProfile(); // Load profile info on page load
});
