/**
 * API Wrapper & HTTP Client
 * Manages Bearer Token injection, error handling, and toast alerts.
 */

const API = {
  getToken() {
    return localStorage.getItem("portal_token");
  },

  setToken(token) {
    if (token) {
      localStorage.setItem("portal_token", token);
    } else {
      localStorage.removeItem("portal_token");
    }
  },

  getCurrentUser() {
    try {
      const u = localStorage.getItem("portal_user");
      return u ? JSON.parse(u) : null;
    } catch {
      return null;
    }
  },

  setCurrentUser(user) {
    if (user) {
      localStorage.setItem("portal_user", JSON.stringify(user));
    } else {
      localStorage.removeItem("portal_user");
    }
  },

  clearSession() {
    localStorage.removeItem("portal_token");
    localStorage.removeItem("portal_user");
  },

  async request(endpoint, options = {}) {
    const url = endpoint.startsWith("http") ? endpoint : `${CONFIG.API_BASE_URL}${endpoint}`;
    const token = this.getToken();

    const headers = {
      "Content-Type": "application/json",
      ...(options.headers || {})
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired or invalid
          this.clearSession();
          window.dispatchEvent(new CustomEvent("portal:auth-expired"));
        }
        const errorMsg = data.error || `HTTP error ${response.status}`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (err) {
      console.error(`[API Error] ${options.method || "GET"} ${endpoint}:`, err);
      throw err;
    }
  },

  get(endpoint, params = null) {
    let url = endpoint;
    if (params) {
      const qs = new URLSearchParams(params).toString();
      url += `?${qs}`;
    }
    return this.request(url, { method: "GET" });
  },

  post(endpoint, body = {}) {
    return this.request(endpoint, {
      method: "POST",
      body: JSON.stringify(body)
    });
  },

  put(endpoint, body = {}) {
    return this.request(endpoint, {
      method: "PUT",
      body: JSON.stringify(body)
    });
  }
};

/**
 * Toast Notification System
 */
function showToast(message, type = "info", duration = 4000) {
  let container = document.getElementById("toastContainer");
  if (!container) {
    container = document.createElement("div");
    container.id = "toastContainer";
    container.className = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = `portal-toast toast-${type}`;

  const iconClass =
    type === "success"
      ? "bi-check-circle-fill text-success"
      : type === "error"
      ? "bi-exclamation-triangle-fill text-danger"
      : type === "warning"
      ? "bi-exclamation-circle-fill text-warning"
      : "bi-info-circle-fill text-primary";

  toast.innerHTML = `
    <i class="bi ${iconClass} fs-5 mt-1"></i>
    <div style="flex: 1;">
      <div style="font-weight: 600; font-size: 0.88rem; margin-bottom: 2px;">
        ${type.toUpperCase()}
      </div>
      <div style="font-size: 0.82rem; color: #475569;">
        ${message}
      </div>
    </div>
    <button type="button" class="btn-close btn-close-sm" style="font-size: 0.75rem;"></button>
  `;

  const closeBtn = toast.querySelector(".btn-close");
  closeBtn.addEventListener("click", () => toast.remove());

  container.appendChild(toast);

  setTimeout(() => {
    if (toast.parentNode) {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(100%)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }
  }, duration);
}
