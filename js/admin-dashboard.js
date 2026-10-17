/**
 * Administrator Dashboard & Eligibility Rule Management Module
 * Controls campus-wide analytics, official student registry, rule configuration & publishing,
 * audit trail inspections, and report exports.
 */

const AdminDashboard = {
  currentRegistry: [],
  selectedClubId: "coding-club",

  init() {
    this.bindEvents();
  },

  bindEvents() {
    // Club selector in rule manager
    const ruleClubSelect = document.getElementById("adminRuleClubSelect");
    if (ruleClubSelect) {
      ruleClubSelect.addEventListener("change", (e) => {
        this.selectedClubId = e.target.value;
        this.loadClubRule(this.selectedClubId);
      });
    }

    // Publish rule form submit
    const publishForm = document.getElementById("adminPublishRuleForm");
    if (publishForm) {
      publishForm.addEventListener("submit", (e) => this.handlePublishRule(e));
    }

    // Add student to registry form
    const addStudentForm = document.getElementById("adminAddStudentForm");
    if (addStudentForm) {
      addStudentForm.addEventListener("submit", (e) => this.handleAddStudent(e));
    }
  },

  async loadDashboard() {
    const user = API.getCurrentUser();
    if (!user || user.role !== "ADMINISTRATOR") {
      showToast("Access denied: Administrator account required.", "error");
      return;
    }

    await Promise.all([
      this.loadMetrics(),
      this.loadRegistry(),
      this.loadClubRule(this.selectedClubId),
      this.loadAuditLogs()
    ]);
  },

  async loadMetrics() {
    try {
      const data = await API.get("/admin/metrics");
      const m = data.metrics;

      // Top Metric Cards
      document.getElementById("adminTotalStudents").innerText = m.total_students;
      document.getElementById("adminTotalClubs").innerText = m.total_clubs;
      document.getElementById("adminVerifiedStudents").innerText = m.verified_students_count;
      document.getElementById("adminPendingVerifications").innerText = m.pending_verifications_count;
      document.getElementById("adminPendingApps").innerText = m.pending_applications_count;
      document.getElementById("adminApprovedMembers").innerText = m.approved_memberships_count;
      document.getElementById("adminRejectedApps").innerText = m.rejected_applications_count;
      document.getElementById("adminUpcomingEvents").innerText = m.total_upcoming_events;

      // Club fill stats
      const statsList = document.getElementById("adminClubFillStatsList");
      if (statsList && data.club_stats) {
        statsList.innerHTML = data.club_stats
          .map((c) => {
            return `
              <div class="mb-3">
                <div class="d-flex justify-content-between mb-1" style="font-size: 0.82rem;">
                  <span class="fw-semibold">${c.name}</span>
                  <span class="text-muted">${c.current_members_count} / ${c.capacity} (${c.fill_percentage}%)</span>
                </div>
                <div class="capacity-bar-bg">
                  <div class="capacity-bar-fill ${c.fill_percentage >= 90 ? 'bg-danger' : 'bg-primary'}" style="width: ${Math.min(100, c.fill_percentage)}%;"></div>
                </div>
              </div>
            `;
          })
          .join("");
      }
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async loadRegistry() {
    const tbody = document.getElementById("adminRegistryTableBody");
    if (!tbody) return;

    try {
      tbody.innerHTML = `<tr><td colspan="8" class="text-center py-4"><span class="spinner-border spinner-border-sm me-2"></span>Loading official registry...</td></tr>`;
      const res = await API.get("/admin/registry");
      this.currentRegistry = res.registry || [];

      tbody.innerHTML = this.currentRegistry
        .map((s) => {
          const isVerified = s.verification_status === "VERIFIED";

          return `
            <tr>
              <td><code>${s.register_number}</code></td>
              <td class="fw-bold">${s.full_name}</td>
              <td>${s.department}</td>
              <td class="text-center">${s.academic_year}</td>
              <td class="text-center fw-semibold">${s.cgpa ? s.cgpa.toFixed(2) : 'N/A'}</td>
              <td class="text-center">${s.aptitude_score || 'N/A'}</td>
              <td class="text-center">${s.programming_score || 'N/A'}</td>
              <td>
                <span class="badge ${isVerified ? 'bg-success-subtle text-success border border-success-subtle' : 'bg-warning-subtle text-warning border border-warning-subtle'}">
                  ${s.verification_status}
                </span>
              </td>
              <td class="text-end">
                <button class="btn btn-sm ${isVerified ? 'btn-outline-warning' : 'btn-outline-success'} me-1" 
                  onclick="AdminDashboard.toggleVerificationStatus('${s.register_number}', '${isVerified ? 'PENDING_VERIFICATION' : 'VERIFIED'}')">
                  <i class="bi ${isVerified ? 'bi-shield-slash' : 'bi-shield-check'}"></i> ${isVerified ? 'Revoke' : 'Verify'}
                </button>
                <button class="btn btn-sm btn-outline-primary" onclick="AdminDashboard.openEditStudentModal('${s.register_number}')">
                  <i class="bi bi-pencil"></i> Edit
                </button>
              </td>
            </tr>
          `;
        })
        .join("");
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="8" class="text-danger py-4">Failed to load registry: ${err.message}</td></tr>`;
    }
  },

  async toggleVerificationStatus(regNum, newStatus) {
    try {
      await API.put(`/admin/registry/${regNum}`, { verification_status: newStatus });
      showToast(`Student ${regNum} verification status set to ${newStatus}.`, "success");
      this.loadRegistry();
      this.loadMetrics();
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  openEditStudentModal(regNum) {
    const student = this.currentRegistry.find((s) => s.register_number === regNum);
    if (!student) return;

    const modal = document.getElementById("adminEditStudentModal");
    if (!modal) return;

    document.getElementById("editStudentRegNum").value = student.register_number;
    document.getElementById("editStudentName").value = student.full_name;
    document.getElementById("editStudentCgpa").value = student.cgpa || 0.0;
    document.getElementById("editStudentAptitude").value = student.aptitude_score || 0;
    document.getElementById("editStudentProg").value = student.programming_score || 0;
    document.getElementById("editStudentAttendance").value = student.attendance_percentage || 0.0;
    document.getElementById("editStudentStatus").value = student.verification_status;

    modal.classList.add("active");
  },

  async handleSaveEditStudent() {
    const regNum = document.getElementById("editStudentRegNum").value;
    const cgpa = parseFloat(document.getElementById("editStudentCgpa").value);
    const apt = parseInt(document.getElementById("editStudentAptitude").value);
    const prog = parseInt(document.getElementById("editStudentProg").value);
    const att = parseFloat(document.getElementById("editStudentAttendance").value);
    const status = document.getElementById("editStudentStatus").value;

    try {
      await API.put(`/admin/registry/${regNum}`, {
        cgpa,
        aptitude_score: apt,
        programming_score: prog,
        attendance_percentage: att,
        verification_status: status
      });

      showToast(`Official record for ${regNum} updated successfully!`, "success");
      document.getElementById("adminEditStudentModal").classList.remove("active");
      this.loadRegistry();
      this.loadMetrics();
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async handleAddStudent(e) {
    e.preventDefault();
    const regNum = document.getElementById("addStudentRegNum").value.trim();
    const name = document.getElementById("addStudentName").value.trim();
    const email = document.getElementById("addStudentEmail").value.trim();
    const dept = document.getElementById("addStudentDept").value;
    const year = parseInt(document.getElementById("addStudentYear").value);
    const cgpa = parseFloat(document.getElementById("addStudentCgpa").value);
    const apt = parseInt(document.getElementById("addStudentAptitude").value);
    const prog = parseInt(document.getElementById("addStudentProg").value);
    const att = parseFloat(document.getElementById("addStudentAttendance").value);

    try {
      await API.post("/admin/registry", {
        register_number: regNum,
        full_name: name,
        email,
        department: dept,
        academic_year: year,
        cgpa,
        aptitude_score: apt,
        programming_score: prog,
        attendance_percentage: att,
        completed_courses: ["CS101 - Intro to Programming"],
        certifications: [],
        skill_assessments: {},
        verification_status: "VERIFIED"
      });

      showToast(`Student ${name} (${regNum}) added to registry!`, "success");
      document.getElementById("adminAddStudentForm").reset();
      document.getElementById("adminAddStudentModal").classList.remove("active");
      this.loadRegistry();
      this.loadMetrics();
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async loadClubRule(clubId) {
    try {
      const res = await API.get(`/rules/${clubId}`);
      const active = res.active_rule || {};
      const history = res.history || [];

      // Display active rule version banner
      const badge = document.getElementById("adminActiveRuleVersionBadge");
      if (badge) badge.innerText = `Active Rule Version: ${active.version || 'v1.0'}`;

      // Populate Form
      document.getElementById("ruleMinCgpa").value = active.min_cgpa ?? "";
      document.getElementById("ruleMinAptitude").value = active.min_aptitude_score ?? "";
      document.getElementById("ruleMinProgramming").value = active.min_programming_score ?? "";
      document.getElementById("ruleMinAttendance").value = active.min_attendance_percentage ?? "";
      document.getElementById("ruleRemarks").value = `Revised requirements for ${clubId}`;

      // Render Rule History Timeline
      const historyList = document.getElementById("adminRuleHistoryList");
      if (historyList) {
        historyList.innerHTML = history
          .map((h) => {
            return `
              <div class="p-3 border rounded-3 bg-light mb-2">
                <div class="d-flex justify-content-between align-items-center mb-1">
                  <span class="badge ${h.is_active ? 'bg-primary' : 'bg-secondary'}">${h.version} ${h.is_active ? '(ACTIVE)' : '(ARCHIVED)'}</span>
                  <small class="text-muted">${new Date(h.published_at).toLocaleString()}</small>
                </div>
                <div style="font-size: 0.82rem; color: #475569;">
                  <strong>Remarks:</strong> ${h.remarks || "Standard criteria"}
                </div>
                <div class="mt-2 text-muted" style="font-size: 0.78rem;">
                  Published by: <code>${h.published_by}</code>
                </div>
              </div>
            `;
          })
          .join("");
      }
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async handlePublishRule(e) {
    e.preventDefault();
    const clubId = this.selectedClubId;
    const cgpa = document.getElementById("ruleMinCgpa").value;
    const apt = document.getElementById("ruleMinAptitude").value;
    const prog = document.getElementById("ruleMinProgramming").value;
    const att = document.getElementById("ruleMinAttendance").value;
    const remarks = document.getElementById("ruleRemarks").value.trim();

    try {
      const res = await API.post(`/rules/${clubId}/publish`, {
        min_cgpa: cgpa ? parseFloat(cgpa) : null,
        min_aptitude_score: apt ? parseInt(apt) : null,
        min_programming_score: prog ? parseInt(prog) : null,
        min_attendance_percentage: att ? parseFloat(att) : null,
        remarks: remarks || "Updated club eligibility criteria"
      });

      showToast(res.message || "New rule version published successfully!", "success");
      this.loadClubRule(clubId);
      this.loadAuditLogs();
    } catch (err) {
      showToast(err.message, "error");
    }
  },

  async loadAuditLogs() {
    const tbody = document.getElementById("adminAuditLogsTableBody");
    if (!tbody) return;

    try {
      const res = await API.get("/admin/audit-logs", { limit: 25 });
      const logs = res.audit_logs || [];

      tbody.innerHTML = logs
        .map((log) => {
          return `
            <tr>
              <td><small class="text-muted">${new Date(log.timestamp).toLocaleTimeString()}</small></td>
              <td><code>${log.actor_id}</code> <span class="badge bg-light text-dark border ms-1">${log.actor_role}</span></td>
              <td><span class="badge bg-dark-subtle text-dark">${log.action}</span></td>
              <td><code>${log.target_entity}</code></td>
              <td style="font-size: 0.82rem;">${log.details}</td>
            </tr>
          `;
        })
        .join("");
    } catch (err) {
      tbody.innerHTML = `<tr><td colspan="5" class="text-danger py-3">Failed to load audit logs: ${err.message}</td></tr>`;
    }
  },

  async exportReport() {
    try {
      const report = await API.get("/admin/export-report");
      const blob = new Blob([JSON.stringify(report, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `campus_portal_report_${new Date().toISOString().slice(0, 10)}.json`;
      a.click();
      URL.revokeObjectURL(url);
      showToast("System report exported successfully!", "success");
    } catch (err) {
      showToast(err.message, "error");
    }
  }
};
