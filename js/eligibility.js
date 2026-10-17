/**
 * Eligibility Verification Visualization Module
 * Renders real-time AWS Lambda eligibility evaluation results, criteria breakdowns,
 * and handles application submission workflows.
 */

const Eligibility = {
  getStatusBadge(status) {
    const s = (status || "").toUpperCase();
    if (s.includes("ELIGIBLE_TO_APPLY") || s === "ELIGIBLE TO APPLY") {
      return `<span class="badge-status badge-eligible"><i class="bi bi-check-circle-fill"></i> Eligible to Apply</span>`;
    }
    if (s.includes("NOT_ELIGIBLE") || s === "NOT ELIGIBLE") {
      return `<span class="badge-status badge-ineligible"><i class="bi bi-x-circle-fill"></i> Not Eligible</span>`;
    }
    if (s.includes("PENDING_VERIFICATION") || s === "PENDING VERIFICATION") {
      return `<span class="badge-status badge-pending"><i class="bi bi-clock-history"></i> Pending Verification</span>`;
    }
    if (s.includes("PENDING_APPROVAL") || s === "APPLICATION PENDING APPROVAL") {
      return `<span class="badge-status badge-approved"><i class="bi bi-hourglass-split"></i> Application Pending Approval</span>`;
    }
    if (s.includes("APPROVED")) {
      return `<span class="badge-status badge-eligible"><i class="bi bi-patch-check-fill"></i> Approved Member</span>`;
    }
    if (s.includes("REJECTED")) {
      return `<span class="badge-status badge-ineligible"><i class="bi bi-shield-x"></i> Application Rejected</span>`;
    }
    return `<span class="badge-status badge-pending">${status}</span>`;
  },

  async openVerificationModal(clubId) {
    const modal = document.getElementById("eligibilityModal");
    const modalBody = document.getElementById("eligibilityModalBody");
    const applyBtn = document.getElementById("eligibilityApplyBtn");

    if (!modal || !modalBody) return;

    modal.classList.add("active");
    modalBody.innerHTML = `
      <div class="text-center py-5">
        <div class="spinner-border text-primary" role="status" style="width: 3rem; height: 3rem;"></div>
        <p class="mt-3 text-muted fw-semibold">Evaluating eligibility via AWS Lambda Verification Engine...</p>
      </div>
    `;
    if (applyBtn) applyBtn.style.display = "none";

    try {
      const data = await API.get(`/student/eligibility/${clubId}`);
      this.renderEligibilityReport(data, clubId);
    } catch (err) {
      modalBody.innerHTML = `
        <div class="alert alert-danger">
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          <strong>Verification Engine Error:</strong> ${err.message}
        </div>
      `;
    }
  },

  renderEligibilityReport(data, clubId) {
    const modalBody = document.getElementById("eligibilityModalBody");
    const applyBtn = document.getElementById("eligibilityApplyBtn");
    const title = document.getElementById("eligibilityModalTitle");

    if (title) {
      title.innerText = `Eligibility Evaluation: ${data.club_name}`;
    }

    let statusAlert = "";
    if (data.status === "ELIGIBLE_TO_APPLY") {
      statusAlert = `
        <div class="p-3 mb-4 rounded-3" style="background: #ecfdf5; border: 1px solid #a7f3d0;">
          <div class="d-flex align-items-center gap-3">
            <i class="bi bi-check-circle-fill text-success fs-2"></i>
            <div>
              <h6 class="text-success fw-bold mb-1">ELIGIBLE TO APPLY</h6>
              <p class="mb-0 text-secondary" style="font-size: 0.84rem;">
                Congratulations! You satisfy all mandatory academic and skill criteria under 
                published <strong>Rule Version ${data.rule_version}</strong>.
              </p>
            </div>
          </div>
        </div>
      `;
    } else if (data.status === "PENDING_VERIFICATION") {
      statusAlert = `
        <div class="p-3 mb-4 rounded-3" style="background: #fffbeb; border: 1px solid #fde68a;">
          <div class="d-flex align-items-center gap-3">
            <i class="bi bi-clock-history text-warning fs-2"></i>
            <div>
              <h6 class="text-warning-emphasis fw-bold mb-1">PENDING OFFICIAL VERIFICATION</h6>
              <p class="mb-0 text-secondary" style="font-size: 0.84rem;">
                Your official academic scores and assessments have not yet been verified by the College Registrar.
                Please contact the Academic Administration office.
              </p>
            </div>
          </div>
        </div>
      `;
    } else {
      statusAlert = `
        <div class="p-3 mb-4 rounded-3" style="background: #fef2f2; border: 1px solid #fecaca;">
          <div class="d-flex align-items-center gap-3">
            <i class="bi bi-x-circle-fill text-danger fs-2"></i>
            <div>
              <h6 class="text-danger fw-bold mb-1">NOT ELIGIBLE TO APPLY</h6>
              <p class="mb-0 text-secondary" style="font-size: 0.84rem;">
                You do not currently satisfy one or more mandatory eligibility requirements for this club under 
                <strong>Rule Version ${data.rule_version}</strong>.
              </p>
            </div>
          </div>
        </div>
      `;
    }

    // Failure Explanations
    let failureReasonsHtml = "";
    if (data.failed_reasons && data.failed_reasons.length > 0) {
      failureReasonsHtml = `
        <div class="mb-4">
          <h6 class="fw-bold text-danger mb-2" style="font-size: 0.88rem;">
            <i class="bi bi-shield-x"></i> Failed Requirements Breakdown:
          </h6>
          <ul class="list-group list-group-flush border rounded-3 overflow-hidden">
            ${data.failed_reasons
              .map(
                (r) => `
              <li class="list-group-item list-group-item-danger d-flex align-items-center gap-2" style="font-size: 0.84rem;">
                <i class="bi bi-dash-circle text-danger"></i>
                <span>${r}</span>
              </li>
            `
              )
              .join("")}
          </ul>
        </div>
      `;
    }

    // Criteria Table Rows
    const tableRows = (data.criteria_breakdown || [])
      .map((c) => {
        const badge = c.passed
          ? `<span class="badge bg-success-subtle text-success border border-success-subtle px-2 py-1"><i class="bi bi-check-lg"></i> PASSED</span>`
          : `<span class="badge bg-danger-subtle text-danger border border-danger-subtle px-2 py-1"><i class="bi bi-x-lg"></i> FAILED</span>`;

        return `
          <tr>
            <td>
              <div class="fw-semibold text-dark">${c.criterion}</div>
              <small class="text-muted">${c.description || ""}</small>
            </td>
            <td><code>${c.required}</code></td>
            <td class="fw-semibold">${c.actual}</td>
            <td class="text-end">${badge}</td>
          </tr>
        `;
      })
      .join("");

    const criteriaTableHtml = `
      <div class="card border rounded-3 mb-4">
        <div class="card-header bg-light py-2 px-3 d-flex justify-content-between align-items-center">
          <span class="fw-bold" style="font-size: 0.82rem; text-transform: uppercase; color: #475569;">
            Automated Rules Checklist
          </span>
          <span class="badge bg-secondary">Rule Version: ${data.rule_version}</span>
        </div>
        <div class="table-responsive">
          <table class="criteria-table mb-0">
            <thead>
              <tr>
                <th>Criterion</th>
                <th>Required Benchmark</th>
                <th>Your Verified Record</th>
                <th class="text-end">Verification</th>
              </tr>
            </thead>
            <tbody>
              ${tableRows}
            </tbody>
          </table>
        </div>
      </div>
    `;

    // Club Capacity Info
    const capacityHtml = `
      <div class="d-flex justify-content-between align-items-center p-2 px-3 rounded-2 bg-light mb-3" style="font-size: 0.82rem;">
        <span class="text-muted"><i class="bi bi-people-fill me-1"></i> Membership Capacity:</span>
        <span class="fw-bold ${data.capacity_full ? 'text-danger' : 'text-primary'}">
          ${data.current_members_count} / ${data.club_capacity} filled ${data.capacity_full ? '(FULL)' : ''}
        </span>
      </div>
    `;

    modalBody.innerHTML = statusAlert + failureReasonsHtml + capacityHtml + criteriaTableHtml;

    // Apply Button State
    if (applyBtn) {
      if (data.user_application_status === "APPROVED") {
        applyBtn.style.display = "inline-flex";
        applyBtn.disabled = true;
        applyBtn.innerHTML = `<i class="bi bi-patch-check-fill"></i> You are already a Member`;
      } else if (data.user_application_status === "PENDING_APPROVAL") {
        applyBtn.style.display = "inline-flex";
        applyBtn.disabled = true;
        applyBtn.innerHTML = `<i class="bi bi-clock-history"></i> Application Already Pending Review`;
      } else if (data.status === "ELIGIBLE_TO_APPLY") {
        if (data.capacity_full) {
          applyBtn.style.display = "inline-flex";
          applyBtn.disabled = true;
          applyBtn.innerHTML = `<i class="bi bi-dash-circle"></i> Club at Maximum Capacity`;
        } else {
          applyBtn.style.display = "inline-flex";
          applyBtn.disabled = false;
          applyBtn.innerHTML = `<i class="bi bi-send-fill"></i> Submit Membership Application`;
          applyBtn.onclick = () => this.submitApplication(clubId);
        }
      } else {
        applyBtn.style.display = "none";
      }
    }
  },

  async submitApplication(clubId) {
    const applyBtn = document.getElementById("eligibilityApplyBtn");
    try {
      if (applyBtn) {
        applyBtn.disabled = true;
        applyBtn.innerHTML = `<span class="spinner-border spinner-border-sm me-2"></span>Submitting to AWS Lambda...`;
      }

      const res = await API.post("/student/apply", { club_id: clubId });
      showToast(res.message || "Application submitted successfully!", "success");

      // Close modal
      document.getElementById("eligibilityModal").classList.remove("active");

      // Refresh student dashboard or applications view
      if (typeof StudentDashboard !== "undefined") {
        StudentDashboard.loadDashboard();
      }
    } catch (err) {
      showToast(err.message || "Failed to submit application.", "error");
      if (applyBtn) {
        applyBtn.disabled = false;
        applyBtn.innerHTML = `<i class="bi bi-send-fill"></i> Submit Membership Application`;
      }
    }
  }
};
