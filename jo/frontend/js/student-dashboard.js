/**
 * Student Dashboard & Exploration Module
 * Manages personalized student views, club discovery, application tracker, and events.
 */

const StudentDashboard = {
  currentClubs: [],

  init() {
    this.bindEvents();
  },

  bindEvents() {
    // Search input in Explore Clubs
    const searchInput = document.getElementById("clubSearchInput");
    if (searchInput) {
      searchInput.addEventListener("input", () => this.filterClubs());
    }

    // Category filter dropdown
    const catFilter = document.getElementById("clubCategoryFilter");
    if (catFilter) {
      catFilter.addEventListener("change", () => this.filterClubs());
    }
  },

  async loadDashboard() {
    try {
      const summary = await API.get("/student/dashboard");
      this.renderSummary(summary);
    } catch (err) {
      showToast(err.message || "Failed to load dashboard data.", "error");
    }
  },

  renderSummary(data) {
    const profile = data.profile;
    const metrics = data.metrics;

    // Header Greeting
    const welcomeName = document.getElementById("studentWelcomeName");
    if (welcomeName) welcomeName.innerText = profile.full_name;

    const studentMeta = document.getElementById("studentHeaderMeta");
    if (studentMeta) {
      studentMeta.innerHTML = `
        <span class="me-3"><i class="bi bi-card-text me-1 text-primary"></i> Reg No: <strong>${profile.register_number}</strong></span>
        <span class="me-3"><i class="bi bi-mortarboard me-1 text-primary"></i> ${profile.department} (Year ${profile.academic_year})</span>
        <span>${
          profile.verification_status === "VERIFIED"
            ? '<span class="badge bg-success-subtle text-success border border-success-subtle"><i class="bi bi-patch-check-fill me-1"></i> Official Record Verified</span>'
            : '<span class="badge bg-warning-subtle text-warning border border-warning-subtle"><i class="bi bi-clock-history me-1"></i> Pending Registrar Verification</span>'
        }</span>
      `;
    }

    // Stat Cards
    const cgpaElem = document.getElementById("statVerifiedCgpa");
    if (cgpaElem) cgpaElem.innerText = profile.cgpa ? `${profile.cgpa.toFixed(2)} / 10.0` : "N/A";

    const aptElem = document.getElementById("statAptitudeScore");
    if (aptElem) aptElem.innerText = profile.aptitude_score ? `${profile.aptitude_score} / 100` : "N/A";

    const progElem = document.getElementById("statProgrammingScore");
    if (progElem) progElem.innerText = profile.programming_score ? `${profile.programming_score} / 100` : "N/A";

    const eligCountElem = document.getElementById("statEligibleClubsCount");
    if (eligCountElem) eligCountElem.innerText = `${metrics.total_eligible_clubs} Clubs`;

    // Overview clubs preview table / grid
    const clubsOverviewList = document.getElementById("dashboardClubsOverview");
    if (clubsOverviewList && data.clubs_eligibility) {
      clubsOverviewList.innerHTML = data.clubs_eligibility
        .map((c) => {
          const badge = Eligibility.getStatusBadge(c.display_status);
          return `
            <div class="col-md-4 mb-3">
              <div class="p-3 border rounded-3 bg-white h-100 d-flex flex-direction-column justify-content-between">
                <div>
                  <div class="d-flex justify-content-between align-items-center mb-2">
                    <span class="badge bg-light text-secondary border">${c.category}</span>
                    <small class="text-muted">Rule ${c.rule_version}</small>
                  </div>
                  <h6 class="fw-bold mb-1">${c.club_name}</h6>
                  <div class="mb-3">${badge}</div>
                </div>
                <button class="btn btn-sm btn-outline-primary w-100" onclick="Eligibility.openVerificationModal('${c.club_id}')">
                  <i class="bi bi-eye"></i> View Criteria & Apply
                </button>
              </div>
            </div>
          `;
        })
        .join("");
    }

    // Recent Applications Table
    const recentAppsTable = document.getElementById("studentRecentApplicationsTable");
    if (recentAppsTable) {
      if (!data.recent_applications || data.recent_applications.length === 0) {
        recentAppsTable.innerHTML = `<tr><td colspan="5" class="text-center text-muted py-4">No membership applications submitted yet.</td></tr>`;
      } else {
        recentAppsTable.innerHTML = data.recent_applications
          .map((a) => {
            const badge = Eligibility.getStatusBadge(a.status);
            return `
              <tr>
                <td><code>${a.application_id}</code></td>
                <td class="fw-semibold">${a.club_name}</td>
                <td><span class="badge bg-secondary-subtle text-secondary border">${a.rule_version}</span></td>
                <td>${badge}</td>
                <td class="text-muted" style="font-size: 0.8rem;">${new Date(a.applied_at).toLocaleDateString()}</td>
              </tr>
            `;
          })
          .join("");
      }
    }
  },

  async loadExploreClubs() {
    try {
      const res = await API.get("/clubs");
      this.currentClubs = res.clubs || [];
      this.renderClubsGrid(this.currentClubs);
    } catch (err) {
      showToast(err.message || "Failed to load clubs.", "error");
    }
  },

  filterClubs() {
    const term = (document.getElementById("clubSearchInput")?.value || "").toLowerCase().trim();
    const cat = document.getElementById("clubCategoryFilter")?.value || "ALL";

    const filtered = this.currentClubs.filter((c) => {
      const matchesCat = cat === "ALL" || c.category.toLowerCase() === cat.toLowerCase();
      const matchesTerm =
        !term ||
        c.name.toLowerCase().includes(term) ||
        c.description.toLowerCase().includes(term) ||
        (c.tags || []).some((t) => t.toLowerCase().includes(term));
      return matchesCat && matchesTerm;
    });

    this.renderClubsGrid(filtered);
  },

  renderClubsGrid(clubs) {
    const grid = document.getElementById("exploreClubsGrid");
    if (!grid) return;

    if (clubs.length === 0) {
      grid.innerHTML = `
        <div class="col-12 text-center py-5">
          <i class="bi bi-search text-muted fs-1 mb-2"></i>
          <h6 class="text-muted">No clubs found matching your search criteria.</h6>
        </div>
      `;
      return;
    }

    grid.innerHTML = clubs
      .map((club) => {
        const fillPct = Math.min(100, Math.round((club.current_members_count / club.capacity) * 100));
        const isFull = club.current_members_count >= club.capacity;

        return `
          <div class="col-lg-4 col-md-6 mb-4">
            <div class="club-card">
              <div class="club-card-banner" style="background: linear-gradient(135deg, ${club.banner_color || '#4f46e5'}, #0f172a);">
                <span class="badge bg-white text-dark shadow-sm">${club.category}</span>
                <span class="badge ${isFull ? 'bg-danger' : 'bg-success'} text-white shadow-sm">
                  ${isFull ? 'CAPACITY FULL' : 'ENROLLING'}
                </span>
                <div class="club-card-avatar" style="color: ${club.banner_color || '#4f46e5'};">
                  <i class="bi ${club.icon || 'bi-people-fill'}"></i>
                </div>
              </div>
              <div class="club-card-content">
                <div class="club-card-category">${club.category}</div>
                <h5 class="club-card-title">${club.name}</h5>
                <p class="club-card-desc">${club.description}</p>

                <div class="club-meta-item">
                  <i class="bi bi-person-badge"></i>
                  <span><strong>Leader:</strong> ${club.leader_name}</span>
                </div>
                <div class="club-meta-item">
                  <i class="bi bi-mortarboard"></i>
                  <span><strong>Faculty:</strong> ${club.faculty_coordinator}</span>
                </div>

                <div class="capacity-bar-container">
                  <div class="d-flex justify-content-between mb-1" style="font-size: 0.76rem;">
                    <span class="text-muted">Membership Capacity</span>
                    <span class="fw-semibold ${isFull ? 'text-danger' : 'text-primary'}">${club.current_members_count} / ${club.capacity} members</span>
                  </div>
                  <div class="capacity-bar-bg">
                    <div class="capacity-bar-fill ${isFull ? 'bg-danger' : 'bg-primary'}" style="width: ${fillPct}%;"></div>
                  </div>
                </div>

                <div class="mt-3 pt-3 border-top d-flex gap-2">
                  <button class="btn btn-sm btn-portal-primary flex-grow-1" onclick="Eligibility.openVerificationModal('${club.club_id}')">
                    <i class="bi bi-shield-check"></i> Check Eligibility & Apply
                  </button>
                </div>
              </div>
            </div>
          </div>
        `;
      })
      .join("");
  },

  async loadApplications() {
    const tbody = document.getElementById("myApplicationsTableBody");
    if (!tbody) return;

    try {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading applications...</td></tr>`;
      const res = await API.get("/student/applications");
      const apps = res.applications || [];

      if (apps.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-5">You have not submitted any club applications yet.</td></tr>`;
        return;
      }

      tbody.innerHTML = apps
        .map((a) => {
          const badge = Eligibility.getStatusBadge(a.status);
          const canCancel = a.status === "PENDING_APPROVAL";

          return `
            <tr>
              <td><code>${a.application_id}</code></td>
              <td class="fw-bold">${a.club_name}</td>
              <td><span class="badge bg-secondary-subtle text-secondary border">Rule ${a.rule_version}</span></td>
              <td>${badge}</td>
              <td class="text-muted" style="font-size: 0.82rem;">${new Date(a.applied_at).toLocaleString()}</td>
              <td style="font-size: 0.82rem; color: #475569;">${a.review_remarks || "Awaiting review by club leadership"}</td>
              <td class="text-end">
                ${
                  canCancel
                    ? `<button class="btn btn-sm btn-outline-danger" onclick="StudentDashboard.cancelApplication('${a.application_id}')">
                        <i class="bi bi-x-circle"></i> Cancel
                      </button>`
                    : `<span class="text-muted" style="font-size: 0.78rem;">Locked</span>`
                }
              </td>
            </tr>
          `;
        })
        .join("");
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-danger py-4">Failed to load applications: ${err.message}</td></tr>`;
    }
  },

  async cancelApplication(appId) {
    if (!confirm("Are you sure you want to cancel this pending application?")) return;
    try {
      const res = await API.post(`/student/applications/${appId}/cancel`);
      showToast(res.message || "Application cancelled.", "info");
      this.loadApplications();
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async loadMemberships() {
    const container = document.getElementById("myClubsContainer");
    if (!container) return;

    try {
      container.innerHTML = `<div class="col-12 text-center py-5"><span class="spinner-border spinner-border-sm me-2"></span>Loading memberships...</div>`;
      const res = await API.get("/student/memberships");
      const mems = res.memberships || [];

      if (mems.length === 0) {
        container.innerHTML = `
          <div class="col-12 text-center py-5">
            <i class="bi bi-person-x text-muted fs-1 mb-2"></i>
            <h6 class="text-muted">You are not currently an approved member of any campus club.</h6>
            <button class="btn btn-portal-primary btn-sm mt-3" onclick="App.showView('exploreClubsView')">
              <i class="bi bi-compass"></i> Explore Clubs
            </button>
          </div>
        `;
        return;
      }

      container.innerHTML = mems
        .map((m) => {
          return `
            <div class="col-md-6 col-lg-4 mb-4">
              <div class="card-custom h-100">
                <div class="card-header-custom" style="background: linear-gradient(135deg, #1e3a8a, #0f172a); color: white;">
                  <div>
                    <h6 class="fw-bold mb-0 text-white">${m.club_name}</h6>
                    <small class="text-light opacity-75">${m.role_in_club}</small>
                  </div>
                  <span class="badge bg-success"><i class="bi bi-check-circle-fill"></i> Active</span>
                </div>
                <div class="card-body-custom">
                  <div class="mb-2" style="font-size: 0.84rem;">
                    <i class="bi bi-calendar-check me-2 text-primary"></i> Joined: <strong>${new Date(m.joined_at).toLocaleDateString()}</strong>
                  </div>
                  <div class="mb-3" style="font-size: 0.84rem;">
                    <i class="bi bi-person-badge me-2 text-primary"></i> ID: <code>${m.membership_id}</code>
                  </div>
                  <button class="btn btn-sm btn-outline-primary w-100" onclick="Eligibility.openVerificationModal('${m.club_id}')">
                    <i class="bi bi-info-circle"></i> View Club Rules & Details
                  </button>
                </div>
              </div>
            </div>
          `;
        })
        .join("");
    } catch (err) {
      container.innerHTML = `<div class="col-12 text-danger py-4">Failed to load memberships: ${err.message}</div>`;
    }
  },

  async loadEvents() {
    const grid = document.getElementById("eventsGrid");
    if (!grid) return;

    try {
      grid.innerHTML = `<div class="col-12 text-center py-5"><span class="spinner-border spinner-border-sm me-2"></span>Loading campus events...</div>`;
      const [eventsRes, myRegsRes] = await Promise.all([
        API.get("/events"),
        API.get("/events/my-registrations")
      ]);

      const events = eventsRes.events || [];
      const registeredIds = new Set((myRegsRes.registrations || []).map((r) => r.event_id));

      if (events.length === 0) {
        grid.innerHTML = `<div class="col-12 text-center text-muted py-5">No upcoming campus events scheduled at this time.</div>`;
        return;
      }

      grid.innerHTML = events
        .map((evt) => {
          const isRegistered = registeredIds.has(evt.event_id);
          const isFull = evt.registered_count >= evt.max_participants;
          const fillPct = Math.round((evt.registered_count / evt.max_participants) * 100);

          return `
            <div class="col-lg-6 mb-4">
              <div class="card-custom h-100 d-flex flex-column">
                <div class="card-header-custom">
                  <div>
                    <span class="badge bg-light text-primary border mb-1">${evt.category}</span>
                    <h5 class="fw-bold mb-0">${evt.title}</h5>
                    <small class="text-muted">Organized by: <strong>${evt.club_name}</strong></small>
                  </div>
                  <span class="badge bg-primary-subtle text-primary border">${evt.event_date}</span>
                </div>
                <div class="card-body-custom flex-grow-1">
                  <p class="text-secondary" style="font-size: 0.86rem;">${evt.description}</p>
                  <div class="row g-2 mb-3" style="font-size: 0.82rem;">
                    <div class="col-6"><i class="bi bi-clock me-1 text-primary"></i> ${evt.start_time}</div>
                    <div class="col-6"><i class="bi bi-geo-alt me-1 text-primary"></i> ${evt.venue}</div>
                  </div>

                  <div class="capacity-bar-container">
                    <div class="d-flex justify-content-between mb-1" style="font-size: 0.76rem;">
                      <span class="text-muted">Capacity</span>
                      <span class="fw-semibold">${evt.registered_count} / ${evt.max_participants} registered</span>
                    </div>
                    <div class="capacity-bar-bg">
                      <div class="capacity-bar-fill ${isFull ? 'bg-danger' : 'bg-primary'}" style="width: ${fillPct}%;"></div>
                    </div>
                  </div>
                </div>
                <div class="p-3 border-top bg-light d-flex justify-content-between align-items-center">
                  <small class="text-muted" style="font-size: 0.76rem;">Deadline: ${new Date(evt.registration_deadline).toLocaleDateString()}</small>
                  ${
                    isRegistered
                      ? `<span class="badge bg-success-subtle text-success border border-success-subtle px-3 py-2"><i class="bi bi-check-circle-fill me-1"></i> Registered</span>`
                      : `<button class="btn btn-sm btn-portal-primary" ${isFull ? 'disabled' : ''} onclick="StudentDashboard.registerForEvent('${evt.event_id}')">
                          <i class="bi bi-ticket-perforated"></i> ${isFull ? 'Registration Full' : 'Register Now'}
                        </button>`
                  }
                </div>
              </div>
            </div>
          `;
        })
        .join("");
    } catch (err) {
      grid.innerHTML = `<div class="col-12 text-danger py-4">Failed to load events: ${err.message}</div>`;
    }
  },

  async registerForEvent(eventId) {
    try {
      const res = await API.post(`/events/${eventId}/register`);
      showToast(res.message || "Registered for event successfully!", "success");
      this.loadEvents();
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async loadProfile() {
    const container = document.getElementById("studentProfileContainer");
    if (!container) return;

    try {
      container.innerHTML = `<div class="text-center py-5"><span class="spinner-border text-primary"></span></div>`;
      const res = await API.get("/student/profile");
      const p = res.profile;

      const coursesHtml = (p.completed_courses || [])
        .map((c) => `<span class="badge bg-light text-dark border p-2 me-1 mb-1"><i class="bi bi-journal-check text-success me-1"></i> ${c}</span>`)
        .join("") || `<span class="text-muted">No course transcript records recorded.</span>`;

      const certsHtml = (p.certifications || [])
        .map((cert) => `<span class="badge bg-primary-subtle text-primary border p-2 me-1 mb-1"><i class="bi bi-award-fill me-1"></i> ${cert}</span>`)
        .join("") || `<span class="text-muted">No industry certifications uploaded.</span>`;

      const skillsHtml = Object.entries(p.skill_assessments || {})
        .map(([k, v]) => `
          <div class="d-flex justify-content-between align-items-center py-2 border-bottom" style="font-size: 0.86rem;">
            <span>${k.replace("_", " ").toUpperCase()}</span>
            <span class="badge ${v === 'PASSED' ? 'bg-success' : 'bg-warning'}">${v}</span>
          </div>
        `)
        .join("") || `<span class="text-muted">No benchmark assessments completed.</span>`;

      container.innerHTML = `
        <div class="row">
          <div class="col-lg-4 mb-4">
            <div class="card-custom text-center p-4">
              <div class="user-avatar mx-auto mb-3" style="width: 72px; height: 72px; font-size: 2rem;">
                ${p.full_name ? p.full_name.charAt(0) : "S"}
              </div>
              <h5 class="fw-bold mb-1">${p.full_name}</h5>
              <p class="text-muted mb-2">${p.register_number}</p>
              <div class="mb-3">
                ${
                  p.verification_status === "VERIFIED"
                    ? `<span class="badge bg-success-subtle text-success border border-success-subtle px-3 py-2"><i class="bi bi-shield-check me-1"></i> Verified Official Record</span>`
                    : `<span class="badge bg-warning-subtle text-warning border border-warning-subtle px-3 py-2"><i class="bi bi-clock-history me-1"></i> Pending Verification</span>`
                }
              </div>
              <hr />
              <div class="text-start" style="font-size: 0.84rem;">
                <p class="mb-2"><i class="bi bi-envelope me-2 text-primary"></i> ${p.email}</p>
                <p class="mb-2"><i class="bi bi-building me-2 text-primary"></i> ${p.department}</p>
                <p class="mb-0"><i class="bi bi-calendar3 me-2 text-primary"></i> Academic Year: <strong>${p.academic_year}</strong></p>
              </div>
            </div>
          </div>

          <div class="col-lg-8">
            <div class="card-custom mb-4">
              <div class="card-header-custom">
                <h6 class="fw-bold mb-0"><i class="bi bi-lock-fill text-muted me-1"></i> Official Verified Academic & Assessment Scores</h6>
                <small class="badge bg-light text-muted border">Source: College Registry</small>
              </div>
              <div class="card-body-custom">
                <div class="row g-3">
                  <div class="col-sm-4">
                    <div class="p-3 border rounded-3 bg-light text-center">
                      <div class="text-muted" style="font-size: 0.78rem;">Cumulative GPA</div>
                      <h3 class="fw-bold text-primary mb-0">${p.cgpa ? p.cgpa.toFixed(2) : 'N/A'}</h3>
                      <small class="text-muted">Scale: 10.0</small>
                    </div>
                  </div>
                  <div class="col-sm-4">
                    <div class="p-3 border rounded-3 bg-light text-center">
                      <div class="text-muted" style="font-size: 0.78rem;">Aptitude Score</div>
                      <h3 class="fw-bold text-primary mb-0">${p.aptitude_score || 'N/A'}</h3>
                      <small class="text-muted">Max: 100</small>
                    </div>
                  </div>
                  <div class="col-sm-4">
                    <div class="p-3 border rounded-3 bg-light text-center">
                      <div class="text-muted" style="font-size: 0.78rem;">Programming Score</div>
                      <h3 class="fw-bold text-primary mb-0">${p.programming_score || 'N/A'}</h3>
                      <small class="text-muted">Max: 100</small>
                    </div>
                  </div>
                </div>

                <div class="mt-4">
                  <div class="d-flex justify-content-between mb-1" style="font-size: 0.84rem;">
                    <span>Official Attendance</span>
                    <strong>${p.attendance_percentage ? p.attendance_percentage.toFixed(1) : '0.0'}%</strong>
                  </div>
                  <div class="capacity-bar-bg">
                    <div class="capacity-bar-fill bg-success" style="width: ${p.attendance_percentage || 0}%;"></div>
                  </div>
                </div>

                <div class="alert alert-secondary mt-4 mb-0 py-2 px-3 d-flex align-items-center gap-2" style="font-size: 0.8rem;">
                  <i class="bi bi-info-circle text-primary fs-5"></i>
                  <span>Official academic and benchmark scores are locked and strictly validated against the university registrar source of truth.</span>
                </div>
              </div>
            </div>

            <div class="card-custom mb-4">
              <div class="card-header-custom">
                <h6 class="fw-bold mb-0">Completed Prerequisite Courses</h6>
              </div>
              <div class="card-body-custom">
                ${coursesHtml}
              </div>
            </div>

            <div class="card-custom mb-4">
              <div class="card-header-custom">
                <h6 class="fw-bold mb-0">Industry Certifications & Skill Assessments</h6>
              </div>
              <div class="card-body-custom">
                <div class="mb-3">
                  <div class="form-label-custom">Certifications on File:</div>
                  ${certsHtml}
                </div>
                <div>
                  <div class="form-label-custom">Technical Skill Benchmarks:</div>
                  ${skillsHtml}
                </div>
              </div>
            </div>
          </div>
        </div>
      `;
    } catch (err) {
      container.innerHTML = `<div class="text-danger py-4">Failed to load profile: ${err.message}</div>`;
    }
  }
};
