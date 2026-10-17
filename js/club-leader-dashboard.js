/**
 * Club Leader Dashboard Module
 * Manages assigned club applications, applicant eligibility inspection,
 * approval/rejection within capacity limits, and club event creation.
 */

const ClubLeaderDashboard = {
  assignedClubId: null,

  init() {
    this.bindEvents();
  },

  bindEvents() {
    // Event creation form submit
    const eventForm = document.getElementById("leaderCreateEventForm");
    if (eventForm) {
      eventForm.addEventListener("submit", (e) => this.handleCreateEvent(e));
    }
  },

  async loadDashboard() {
    const user = API.getCurrentUser();
    if (!user || user.role !== "CLUB_LEADER") {
      showToast("Access denied: Club Leader account required.", "error");
      return;
    }

    const assigned = user.assigned_clubs || [];
    this.assignedClubId = assigned[0] || "coding-club";

    // Set Header
    const leaderName = document.getElementById("leaderWelcomeName");
    if (leaderName) leaderName.innerText = user.full_name;

    const assignedBadge = document.getElementById("leaderAssignedClubBadge");
    if (assignedBadge) assignedBadge.innerText = `Assigned Club: ${this.assignedClubId}`;

    await Promise.all([
      this.loadClubStats(),
      this.loadPendingApplications(),
      this.loadClubMembers()
    ]);
  },

  async loadClubStats() {
    try {
      const res = await API.get(`/clubs/${this.assignedClubId}`);
      const club = res.club;
      if (!club) return;

      const titleElem = document.getElementById("leaderClubTitle");
      if (titleElem) titleElem.innerText = club.name;

      const capElem = document.getElementById("leaderClubCapacity");
      if (capElem) {
        capElem.innerText = `${club.current_members_count} / ${club.capacity} Members (${club.capacity - club.current_members_count} Seats Remaining)`;
      }

      // Pre-fill create event club selector
      const eventClubInput = document.getElementById("leaderEventClubId");
      if (eventClubInput) {
        eventClubInput.value = this.assignedClubId;
      }
    } catch (err) {
      console.error("Failed to load club stats:", err);
    }
  },

  async loadPendingApplications() {
    const tbody = document.getElementById("leaderApplicationsTableBody");
    if (!tbody) return;

    try {
      tbody.innerHTML = `<tr><td colspan="6" class="text-center py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading applicant pool...</td></tr>`;
      const res = await API.get("/applications", { club_id: this.assignedClubId });
      const apps = res.applications || [];

      if (apps.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted py-5">No applications submitted for this club yet.</td></tr>`;
        return;
      }

      tbody.innerHTML = apps
        .map((app) => {
          const badge = Eligibility.getStatusBadge(app.status);
          const isPending = app.status === "PENDING_APPROVAL";

          return `
            <tr>
              <td>
                <div class="fw-bold">${app.student_name}</div>
                <small class="text-muted"><code>${app.register_number}</code></small>
              </td>
              <td>${app.student_department} (Yr ${app.academic_year || 1})</td>
              <td><span class="badge bg-secondary-subtle text-secondary border">Rule ${app.rule_version}</span></td>
              <td>${badge}</td>
              <td class="text-muted" style="font-size: 0.8rem;">${new Date(app.applied_at).toLocaleString()}</td>
              <td class="text-end">
                <button class="btn btn-sm btn-outline-info me-1" onclick="ClubLeaderDashboard.inspectApplication('${app.application_id}')" title="Inspect Automated Evaluation">
                  <i class="bi bi-search"></i> Inspect
                </button>
                ${
                  isPending
                    ? `
                      <button class="btn btn-sm btn-portal-success me-1" onclick="ClubLeaderDashboard.reviewApp('${app.application_id}', 'APPROVED')">
                        <i class="bi bi-check-lg"></i> Approve
                      </button>
                      <button class="btn btn-sm btn-portal-danger" onclick="ClubLeaderDashboard.reviewApp('${app.application_id}', 'REJECTED')">
                        <i class="bi bi-x-lg"></i> Reject
                      </button>
                    `
                    : `<span class="badge bg-light text-muted border">Completed</span>`
                }
              </td>
            </tr>
          `;
        })
        .join("");
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="6" class="text-danger py-4">Failed to load applications: ${err.message}</td></tr>`;
    }
  },

  async inspectApplication(appId) {
    try {
      const res = await API.get("/applications", { club_id: this.assignedClubId });
      const target = (res.applications || []).find((a) => a.application_id === appId);
      if (!target) {
        showToast("Application not found.", "error");
        return;
      }

      const modal = document.getElementById("eligibilityModal");
      const modalBody = document.getElementById("eligibilityModalBody");
      const title = document.getElementById("eligibilityModalTitle");
      const applyBtn = document.getElementById("eligibilityApplyBtn");

      if (title) title.innerText = `Applicant Inspection: ${target.student_name} (${target.register_number})`;
      if (applyBtn) applyBtn.style.display = "none";

      const rows = Object.entries(target.criteria_results || {})
        .map(([k, v]) => `
          <tr>
            <td class="fw-semibold">${k}</td>
            <td><code>${v.actual}</code></td>
            <td class="text-end">
              ${v.passed ? '<span class="badge bg-success"><i class="bi bi-check-lg"></i> PASSED</span>' : '<span class="badge bg-danger"><i class="bi bi-x-lg"></i> FAILED</span>'}
            </td>
          </tr>
        `)
        .join("");

      modalBody.innerHTML = `
        <div class="alert alert-info py-2 px-3 mb-3 d-flex justify-content-between align-items-center">
          <div>
            <strong>Rule Version Snapshot:</strong> ${target.rule_version}
          </div>
          <div>
            <strong>Status:</strong> ${target.status}
          </div>
        </div>
        <div class="card border rounded-3 mb-3">
          <div class="card-header bg-light py-2 px-3 fw-bold" style="font-size: 0.82rem;">
            Criteria Evaluation Snapshot (Calculated by AWS Lambda)
          </div>
          <table class="criteria-table mb-0">
            <thead>
              <tr>
                <th>Criterion Evaluated</th>
                <th>Applicant's Official Value</th>
                <th class="text-end">Result</th>
              </tr>
            </thead>
            <tbody>
              ${rows}
            </tbody>
          </table>
        </div>
        <div class="p-3 bg-light rounded-3" style="font-size: 0.82rem;">
          <div><strong>Application ID:</strong> <code>${target.application_id}</code></div>
          <div><strong>Submission Timestamp:</strong> ${target.applied_at}</div>
          <div><strong>Review Remarks:</strong> ${target.review_remarks || "None"}</div>
        </div>
      `;

      modal.classList.add("active");
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async reviewApp(appId, newStatus) {
    let remarks = "";
    if (newStatus === "REJECTED") {
      remarks = prompt("Please provide a reason for rejecting this application (optional):", "Criteria or capacity constraints.");
      if (remarks === null) return; // User cancelled
    } else {
      if (!confirm(`Are you sure you want to APPROVE this applicant into ${this.assignedClubId}?`)) return;
      remarks = "Eligibility criteria confirmed and applicant accepted.";
    }

    try {
      const res = await API.post(`/applications/${appId}/review`, {
        status: newStatus,
        remarks: remarks
      });
      showToast(res.message || `Application ${newStatus.toLowerCase()} successfully!`, "success");
      this.loadPendingApplications();
      this.loadClubStats();
      this.loadClubMembers();
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async loadClubMembers() {
    const listElem = document.getElementById("leaderClubMembersList");
    if (!listElem) return;

    try {
      const res = await API.get("/applications", { club_id: this.assignedClubId });
      const approved = (res.applications || []).filter((a) => a.status === "APPROVED");

      if (approved.length === 0) {
        listElem.innerHTML = `<li class="list-group-item text-center text-muted py-3">No members enrolled yet.</li>`;
        return;
      }

      listElem.innerHTML = approved
        .map(
          (m) => `
        <li class="list-group-item d-flex justify-content-between align-items-center">
          <div>
            <div class="fw-bold">${m.student_name}</div>
            <small class="text-muted"><code>${m.register_number}</code> - ${m.student_department}</small>
          </div>
          <span class="badge bg-success-subtle text-success border border-success-subtle">Active Member</span>
        </li>
      `
        )
        .join("");
    } catch (err) {
      console.error("Failed to load members:", err);
    }
  },

  async handleCreateEvent(e) {
    e.preventDefault();
    const title = document.getElementById("leaderEventTitle").value.trim();
    const cat = document.getElementById("leaderEventCategory").value;
    const desc = document.getElementById("leaderEventDesc").value.trim();
    const date = document.getElementById("leaderEventDate").value;
    const time = document.getElementById("leaderEventTime").value;
    const venue = document.getElementById("leaderEventVenue").value.trim();
    const deadline = document.getElementById("leaderEventDeadline").value;
    const maxPart = parseInt(document.getElementById("leaderEventMaxParticipants").value);

    try {
      const res = await API.post("/events", {
        club_id: this.assignedClubId,
        title,
        category: cat,
        description: desc,
        event_date: date,
        start_time: time,
        venue,
        registration_deadline: `${deadline}T23:59:59Z`,
        max_participants: maxPart
      });

      showToast(res.message || "Event published successfully!", "success");
      document.getElementById("leaderCreateEventForm").reset();
    } catch (err) {
      showToast(err.message, "error");
    }
  }
};
