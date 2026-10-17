/**
 * Authentication Module
 * Handles Register Number + Password Login, Registration, Password Reset, and Session Lifecycle.
 */

const Auth = {
  init() {
    this.bindEvents();
    this.renderPersonaChips();
  },

  bindEvents() {
    // Auth Tabs Switching (Login vs Create Password)
    const loginTabBtn = document.getElementById("loginTabBtn");
    const createPassTabBtn = document.getElementById("createPassTabBtn");
    const loginFormContainer = document.getElementById("loginFormContainer");
    const createPassFormContainer = document.getElementById("createPassFormContainer");

    if (loginTabBtn && createPassTabBtn) {
      loginTabBtn.addEventListener("click", () => {
        loginTabBtn.classList.add("active");
        createPassTabBtn.classList.remove("active");
        if (loginFormContainer) loginFormContainer.style.display = "block";
        if (createPassFormContainer) createPassFormContainer.style.display = "none";
      });

      createPassTabBtn.addEventListener("click", () => {
        createPassTabBtn.classList.add("active");
        loginTabBtn.classList.remove("active");
        if (loginFormContainer) loginFormContainer.style.display = "none";
        if (createPassFormContainer) createPassFormContainer.style.display = "block";
      });
    }

    // Login Form Submit
    const loginForm = document.getElementById("loginForm");
    if (loginForm) {
      loginForm.addEventListener("submit", (e) => this.handleLogin(e));
    }

    // Create Password Form Submit
    const createPassForm = document.getElementById("createPasswordForm");
    if (createPassForm) {
      createPassForm.addEventListener("submit", (e) => this.handleCreatePassword(e));
    }

    // Toggle Login Password Visibility
    const togglePassBtn = document.getElementById("togglePasswordBtn");
    if (togglePassBtn) {
      togglePassBtn.addEventListener("click", () => {
        const passInput = document.getElementById("loginPassword");
        const icon = togglePassBtn.querySelector("i");
        if (passInput.type === "password") {
          passInput.type = "text";
          icon.className = "bi bi-eye-slash";
        } else {
          passInput.type = "password";
          icon.className = "bi bi-eye";
        }
      });
    }

    // Toggle Create Password Visibility
    const toggleCreatePassBtn = document.getElementById("toggleCreatePassBtn");
    if (toggleCreatePassBtn) {
      toggleCreatePassBtn.addEventListener("click", () => {
        const passInput = document.getElementById("createPassPassword");
        const icon = toggleCreatePassBtn.querySelector("i");
        if (passInput.type === "password") {
          passInput.type = "text";
          icon.className = "bi bi-eye-slash";
        } else {
          passInput.type = "password";
          icon.className = "bi bi-eye";
        }
      });
    }

    // Registration Form Submit
    const registerForm = document.getElementById("registerForm");
    if (registerForm) {
      registerForm.addEventListener("submit", (e) => this.handleRegister(e));
    }

    // Forgot Password Form Submit
    const forgotForm = document.getElementById("forgotPasswordForm");
    if (forgotForm) {
      forgotForm.addEventListener("submit", (e) => this.handleForgotPassword(e));
    }

    // Reset Password Form Submit
    const resetForm = document.getElementById("resetPasswordForm");
    if (resetForm) {
      resetForm.addEventListener("submit", (e) => this.handleResetPassword(e));
    }

    // Global auth expiration listener
    window.addEventListener("portal:auth-expired", () => {
      showToast("Your session has expired. Please log in again.", "warning");
      App.showView("loginView");
    });
  },

  renderPersonaChips() {
    const container = document.getElementById("demoPersonasContainer");
    if (!container) return;

    container.innerHTML = `
      <div style="font-size: 0.78rem; font-weight: 600; color: #64748b; margin-bottom: 0.5rem;">
        <i class="bi bi-lightning-charge-fill text-warning"></i> Quick Demo Login Personas:
      </div>
      <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
        <button type="button" class="quick-persona-chip text-white fw-bold" style="background: #4f46e5; border-color: #4338ca;" data-reg="44111327" data-pass="2006" title="Official SIST Register Number: 44111327, Password: 2006">
          <i class="bi bi-mortarboard-fill me-1"></i> 44111327 (Pass: 2006)
        </button>
        <button type="button" class="quick-persona-chip" data-reg="123456789012" data-pass="Student@123" title="High CGPA (8.2), Aptitude 75, Prog 80">
          <strong>Arjun</strong> (Eligible Student)
        </button>
        <button type="button" class="quick-persona-chip" data-reg="123456789013" data-pass="Student@123" title="Aptitude 55 (<70), Prog 50 (<60)">
          <strong>Priya</strong> (Ineligible Student)
        </button>
        <button type="button" class="quick-persona-chip" data-reg="123456789014" data-pass="Student@123" title="Awaiting official registrar verification">
          <strong>Rahul</strong> (Pending Verification)
        </button>
        <button type="button" class="quick-persona-chip" data-reg="leader_coding" data-pass="Leader@123" title="Coding Club Leader">
          <strong>Leader</strong> (Coding Club)
        </button>
        <button type="button" class="quick-persona-chip" data-reg="admin_portal" data-pass="Admin@123" title="Chief Admin / Dean">
          <strong>Admin</strong> (Dean / Full Access)
        </button>
      </div>
    `;

    container.querySelectorAll(".quick-persona-chip").forEach((btn) => {
      btn.addEventListener("click", () => {
        const reg = btn.getAttribute("data-reg");
        const pass = btn.getAttribute("data-pass");
        const regInput = document.getElementById("loginRegisterNumber");
        const passInput = document.getElementById("loginPassword");
        if (regInput && passInput) {
          regInput.value = reg;
          passInput.value = pass;
          showToast(`Filled credentials: Reg No ${reg} | Password ${pass}`, "info", 2000);
        }
      });
    });
  },

  async handleLogin(e) {
    e.preventDefault();
    const regNum = document.getElementById("loginRegisterNumber").value.trim();
    const pass = document.getElementById("loginPassword").value;
    const submitBtn = document.getElementById("loginSubmitBtn");

    if (!regNum || !pass) {
      showToast("Please enter your Register Number and Password.", "warning");
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Authenticating with Cognito...`;

      const response = await API.post("/auth/login", {
        register_number: regNum,
        password: pass
      });

      API.setToken(response.token);
      API.setCurrentUser(response.user);

      showToast(`Welcome back, ${response.user.full_name}!`, "success");

      // Route by role
      App.handlePostLoginRedirect(response.user);
    } catch (err) {
      showToast(err.message || "Invalid Register Number or Password.", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i class="bi bi-box-arrow-in-right"></i> Sign In to Portal`;
    }
  },

  async handleCreatePassword(e) {
    e.preventDefault();
    const regNum = document.getElementById("createPassRegNum").value.trim();
    const pass = document.getElementById("createPassPassword").value;
    const confirmPass = document.getElementById("createPassConfirmPassword").value;
    const submitBtn = document.getElementById("createPassSubmitBtn");

    if (!regNum || !pass || !confirmPass) {
      showToast("Please fill in your Register Number and choose a password.", "warning");
      return;
    }

    if (pass.length < 4) {
      showToast("Password must be at least 4 characters.", "warning");
      return;
    }

    if (pass !== confirmPass) {
      showToast("Password and Confirm Password do not match.", "error");
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Verifying Sathyabama Registry & Setting Password...`;

      const response = await API.post("/auth/create-password", {
        register_number: regNum,
        password: pass,
        confirm_password: confirmPass
      });

      showToast(response.message || "Password created successfully!", "success", 6000);

      // Auto-fill login form and switch to Login tab
      const loginReg = document.getElementById("loginRegisterNumber");
      const loginPass = document.getElementById("loginPassword");
      if (loginReg) loginReg.value = regNum;
      if (loginPass) loginPass.value = pass;

      const loginTabBtn = document.getElementById("loginTabBtn");
      if (loginTabBtn) loginTabBtn.click();

      // Clear create form
      document.getElementById("createPasswordForm").reset();
    } catch (err) {
      showToast(err.message || "Failed to create password.", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i class="bi bi-key-fill"></i> Save & Activate Password`;
    }
  },

  async handleRegister(e) {
    e.preventDefault();
    const fullName = document.getElementById("regFullName").value.trim();
    const regNum = document.getElementById("regRegisterNumber").value.trim();
    const email = document.getElementById("regEmail").value.trim();
    const dept = document.getElementById("regDepartment").value;
    const year = document.getElementById("regAcademicYear").value;
    const pass = document.getElementById("regPassword").value;
    const confirmPass = document.getElementById("regConfirmPassword").value;
    const submitBtn = document.getElementById("registerSubmitBtn");

    if (pass !== confirmPass) {
      showToast("Password and Confirm Password do not match.", "error");
      return;
    }

    try {
      submitBtn.disabled = true;
      submitBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Verifying official registry...`;

      const response = await API.post("/auth/register", {
        full_name: fullName,
        register_number: regNum,
        email: email,
        department: dept,
        academic_year: parseInt(year),
        password: pass,
        confirm_password: confirmPass
      });

      showToast(response.message || "Account registered successfully!", "success", 5000);
      App.showView("loginView");

      // Auto-fill login register number
      const loginReg = document.getElementById("loginRegisterNumber");
      if (loginReg) loginReg.value = regNum;
    } catch (err) {
      showToast(err.message || "Registration failed.", "error");
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i class="bi bi-person-check-fill"></i> Complete Registration`;
    }
  },

  async handleForgotPassword(e) {
    e.preventDefault();
    const regNum = document.getElementById("forgotRegisterNumber").value.trim();
    if (!regNum) {
      showToast("Please enter your Register Number.", "warning");
      return;
    }

    try {
      const resp = await API.post("/auth/forgot-password", { register_number: regNum });
      showToast(resp.message, "info", 6000);
      document.getElementById("forgotStep1").style.display = "none";
      document.getElementById("forgotStep2").style.display = "block";
      document.getElementById("resetRegisterNumber").value = regNum;
      if (resp.demo_reset_token) {
        document.getElementById("resetOtpCode").value = resp.demo_reset_token;
      }
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async handleResetPassword(e) {
    e.preventDefault();
    const regNum = document.getElementById("resetRegisterNumber").value.trim();
    const otp = document.getElementById("resetOtpCode").value.trim();
    const newPass = document.getElementById("newPassword").value;

    try {
      const resp = await API.post("/auth/reset-password", {
        register_number: regNum,
        otp_code: otp,
        new_password: newPass
      });
      showToast(resp.message, "success");
      App.showView("loginView");
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  logout() {
    API.clearSession();
    showToast("You have been signed out safely.", "info");
    App.showView("loginView");
  }
};
