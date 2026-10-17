/**
 * Main Application Orchestrator & Router
 * Controls Single-Page Navigation, Role-based Sidebar Rendering, and Modal Dialogs.
 */

const App = {
  currentView: "landingView",

  init() {
    Auth.init();
    StudentDashboard.init();
    ClubLeaderDashboard.init();
    AdminDashboard.init();

    this.bindGlobalEvents();
    this.checkInitialSession();
  },

  bindGlobalEvents() {
    // Navigation link clicks (data-view attributes)
    document.addEventListener("click", (e) => {
      const target = e.target.closest("[data-view]");
      if (target) {
        e.preventDefault();
        const viewName = target.getAttribute("data-view");
        this.showView(viewName);
      }
    });

    // Close Modals on click outside or close button
    document.querySelectorAll(".modal-overlay").forEach((modal) => {
      modal.addEventListener("click", (e) => {
        if (e.target === modal || e.target.closest(".modal-close-btn")) {
          modal.classList.remove("active");
        }
      });
    });

    // Mobile Sidebar Toggle
    const toggleSidebarBtn = document.getElementById("toggleSidebarBtn");
    if (toggleSidebarBtn) {
      toggleSidebarBtn.addEventListener("click", () => {
        const sidebar = document.querySelector(".sidebar");
        if (sidebar) sidebar.classList.toggle("show");
      });
    }

    // Header Quick Persona Switcher
    const personaSelector = document.getElementById("quickPersonaSelect");
    if (personaSelector) {
      personaSelector.addEventListener("change", async (e) => {
        const val = e.target.value;
        if (!val) return;
        const creds = CONFIG.DEMO_USERS[val];
        if (creds) {
          try {
            const resp = await API.post("/auth/login", {
              register_number: creds.register_number,
              password: creds.password
            });
            API.setToken(resp.token);
            API.setCurrentUser(resp.user);
            showToast(`Switched account to: ${creds.name}`, "info");
            this.handlePostLoginRedirect(resp.user);
          } catch (err) {
            showToast(err.message, "error");
          }
        }
      });
    }
  },

  checkInitialSession() {
    const user = API.getCurrentUser();
    const token = API.getToken();

    if (user && token) {
      this.handlePostLoginRedirect(user);
    } else {
      this.showView("loginView");
    }
  },

  handlePostLoginRedirect(user) {
    this.updateNavbarUser(user);
    this.renderSidebarForRole(user.role);

    if (user.role === "STUDENT") {
      this.showView("studentDashboardView");
    } else if (user.role === "CLUB_LEADER") {
      this.showView("clubLeaderDashboardView");
    } else if (user.role === "ADMINISTRATOR") {
      this.showView("adminDashboardView");
    } else {
      this.showView("exploreClubsView");
    }
  },

  updateNavbarUser(user) {
    const nameElem = document.getElementById("navUserName");
    const roleElem = document.getElementById("navUserRole");
    const avatarElem = document.getElementById("navUserAvatar");

    if (nameElem && user) nameElem.innerText = user.full_name || user.register_number;
    if (roleElem && user) roleElem.innerText = user.role.replace("_", " ");
    if (avatarElem && user) avatarElem.innerText = (user.full_name || user.register_number).charAt(0).toUpperCase();

    const authSection = document.getElementById("navUserBadgeContainer");
    const loginBtn = document.getElementById("navLoginBtn");

    if (user) {
      if (authSection) authSection.style.display = "flex";
      if (loginBtn) loginBtn.style.display = "none";
    } else {
      if (authSection) authSection.style.display = "none";
      if (loginBtn) loginBtn.style.display = "block";
    }
  },

  renderSidebarForRole(role) {
    const sidebarMenu = document.getElementById("sidebarNavigationMenu");
    if (!sidebarMenu) return;

    if (role === "STUDENT") {
      sidebarMenu.innerHTML = `
        <div class="menu-section-label">Student Portal</div>
        <a class="nav-item-link" data-view="studentDashboardView">
          <i class="bi bi-speedometer2"></i> Dashboard
        </a>
        <a class="nav-item-link" data-view="exploreClubsView">
          <i class="bi bi-compass"></i> Explore Clubs
        </a>
        <a class="nav-item-link" data-view="myApplicationsView">
          <i class="bi bi-file-earmark-text"></i> My Applications
        </a>
        <a class="nav-item-link" data-view="myClubsView">
          <i class="bi bi-award"></i> My Clubs
        </a>
        <a class="nav-item-link" data-view="eventsView">
          <i class="bi bi-calendar-event"></i> Campus Events
        </a>
        <a class="nav-item-link" data-view="studentProfileView">
          <i class="bi bi-person-badge"></i> My Official Profile
        </a>
        
        <div class="menu-section-label mt-3">Account</div>
        <a class="nav-item-link text-danger" onclick="Auth.logout()">
          <i class="bi bi-box-arrow-left"></i> Logout
        </a>
      `;
    } else if (role === "CLUB_LEADER") {
      sidebarMenu.innerHTML = `
        <div class="menu-section-label">Club Leadership</div>
        <a class="nav-item-link" data-view="clubLeaderDashboardView">
          <i class="bi bi-shield-check"></i> Club Management
        </a>
        <a class="nav-item-link" data-view="exploreClubsView">
          <i class="bi bi-compass"></i> All Campus Clubs
        </a>
        <a class="nav-item-link" data-view="eventsView">
          <i class="bi bi-calendar-event"></i> Campus Events
        </a>

        <div class="menu-section-label mt-3">Account</div>
        <a class="nav-item-link text-danger" onclick="Auth.logout()">
          <i class="bi bi-box-arrow-left"></i> Logout
        </a>
      `;
    } else if (role === "ADMINISTRATOR") {
      sidebarMenu.innerHTML = `
        <div class="menu-section-label">Administration</div>
        <a class="nav-item-link" data-view="adminDashboardView">
          <i class="bi bi-graph-up-arrow"></i> Campus Overview
        </a>
        <a class="nav-item-link" data-view="adminRulesView">
          <i class="bi bi-sliders"></i> Eligibility Rules Manager
        </a>
        <a class="nav-item-link" data-view="adminRegistryView">
          <i class="bi bi-people"></i> Official Student Registry
        </a>
        <a class="nav-item-link" data-view="exploreClubsView">
          <i class="bi bi-compass"></i> Campus Clubs
        </a>
        <a class="nav-item-link" data-view="eventsView">
          <i class="bi bi-calendar-event"></i> Events Manager
        </a>
        <a class="nav-item-link" data-view="adminAuditView">
          <i class="bi bi-shield-lock"></i> Security Audit Logs
        </a>

        <div class="menu-section-label mt-3">Account</div>
        <a class="nav-item-link text-danger" onclick="Auth.logout()">
          <i class="bi bi-box-arrow-left"></i> Logout
        </a>
      `;
    } else {
      sidebarMenu.innerHTML = `
        <div class="menu-section-label">Navigation</div>
        <a class="nav-item-link" data-view="landingView">
          <i class="bi bi-house"></i> Home
        </a>
        <a class="nav-item-link" data-view="exploreClubsView">
          <i class="bi bi-compass"></i> Explore Clubs
        </a>
        <a class="nav-item-link" data-view="eventsView">
          <i class="bi bi-calendar-event"></i> Campus Events
        </a>
        <a class="nav-item-link" data-view="loginView">
          <i class="bi bi-box-arrow-in-right"></i> Sign In
        </a>
      `;
    }
  },

  showView(viewId) {
    const views = document.querySelectorAll(".view-section");
    views.forEach((v) => v.classList.remove("active"));

    const target = document.getElementById(viewId);
    if (!target) {
      console.warn(`View ${viewId} not found.`);
      return;
    }

    target.classList.add("active");
    this.currentView = viewId;

    // Update active state in sidebar
    document.querySelectorAll(".nav-item-link").forEach((link) => {
      if (link.getAttribute("data-view") === viewId) {
        link.classList.add("active");
      } else {
        link.classList.remove("active");
      }
    });

    // Close mobile sidebar if open
    const sidebar = document.querySelector(".sidebar");
    if (sidebar) sidebar.classList.remove("show");

    // Dynamic data loading per view
    if (viewId === "studentDashboardView") {
      StudentDashboard.loadDashboard();
    } else if (viewId === "exploreClubsView") {
      StudentDashboard.loadExploreClubs();
    } else if (viewId === "myApplicationsView") {
      StudentDashboard.loadApplications();
    } else if (viewId === "myClubsView") {
      StudentDashboard.loadMemberships();
    } else if (viewId === "eventsView") {
      StudentDashboard.loadEvents();
    } else if (viewId === "studentProfileView") {
      StudentDashboard.loadProfile();
    } else if (viewId === "clubLeaderDashboardView") {
      ClubLeaderDashboard.loadDashboard();
    } else if (viewId === "adminDashboardView") {
      AdminDashboard.loadDashboard();
    } else if (viewId === "adminRulesView") {
      AdminDashboard.loadClubRule(AdminDashboard.selectedClubId);
    } else if (viewId === "adminRegistryView") {
      AdminDashboard.loadRegistry();
    } else if (viewId === "adminAuditView") {
      AdminDashboard.loadAuditLogs();
    }

    // Scroll to top
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
};

// Start application once DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  App.init();
});
