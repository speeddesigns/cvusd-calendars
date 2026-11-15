/**
 * Dooley Ecosystem Feedback & Telemetry Client Widget
 * Lightweight vanilla JavaScript widget capturing user feedback + diagnostic telemetry.
 */

(function () {
  const errorLogs = [];
  const networkErrors = [];

  // 1. Capture client-side uncaught exceptions
  window.addEventListener("error", function (event) {
    errorLogs.push({
      level: "error",
      message: event.message || "Unknown script error",
      filename: event.filename,
      lineno: event.lineno,
      timestamp: new Date().toISOString()
    });
    if (errorLogs.length > 20) errorLogs.shift();
  });

  window.addEventListener("unhandledrejection", function (event) {
    errorLogs.push({
      level: "error",
      message: event.reason ? String(event.reason.message || event.reason) : "Unhandled Promise Rejection",
      timestamp: new Date().toISOString()
    });
    if (errorLogs.length > 20) errorLogs.shift();
  });

  // 2. Wrap window.fetch for network failure telemetry
  if (window.fetch) {
    const originalFetch = window.fetch;
    window.fetch = async function (...args) {
      try {
        const response = await originalFetch.apply(this, args);
        if (!response.ok) {
          networkErrors.push({
            url: String(args[0]),
            status: response.status,
            method: (args[1] && args[1].method) || "GET",
            error: response.statusText
          });
          if (networkErrors.length > 20) networkErrors.shift();
        }
        return response;
      } catch (err) {
        networkErrors.push({
          url: String(args[0]),
          status: 0,
          method: (args[1] && args[1].method) || "GET",
          error: err.message
        });
        if (networkErrors.length > 20) networkErrors.shift();
        throw err;
      }
    };
  }

  // 3. UI Widget Injection
  function initWidget() {
    const btn = document.createElement("button");
    btn.id = "dooley-feedback-btn";
    btn.innerHTML = "💬 Feedback";
    Object.assign(btn.style, {
      position: "fixed",
      bottom: "20px",
      right: "20px",
      zIndex: "99999",
      padding: "8px 16px",
      backgroundColor: "#2563eb",
      color: "#ffffff",
      border: "none",
      borderRadius: "9999px",
      boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
      cursor: "pointer",
      fontFamily: "system-ui, sans-serif",
      fontSize: "14px",
      fontWeight: "500"
    });

    const modal = document.createElement("div");
    modal.id = "dooley-feedback-modal";
    Object.assign(modal.style, {
      display: "none",
      position: "fixed",
      bottom: "70px",
      right: "20px",
      width: "320px",
      backgroundColor: "#ffffff",
      color: "#1e293b",
      boxShadow: "0 10px 15px -3px rgba(0,0,0,0.1)",
      borderRadius: "12px",
      padding: "16px",
      zIndex: "99999",
      fontFamily: "system-ui, sans-serif"
    });

    modal.innerHTML = `
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <strong style="font-size:15px;">Send Feedback</strong>
        <button id="dooley-feedback-close" style="background:none; border:none; cursor:pointer; font-size:18px;">&times;</button>
      </div>
      <select id="dooley-feedback-type" style="width:100%; margin-bottom:8px; padding:6px; border-radius:6px; border:1px solid #cbd5e1;">
        <option value="bug">Report a Bug / Issue</option>
        <option value="idea">Suggest an Improvement</option>
        <option value="question">Ask a Question</option>
      </select>
      <textarea id="dooley-feedback-desc" placeholder="What happened? Or what would you improve?" rows="3" style="width:100%; margin-bottom:8px; padding:8px; border-radius:6px; border:1px solid #cbd5e1; font-family:inherit; box-sizing:border-box;"></textarea>
      <input id="dooley-feedback-email" type="email" placeholder="Your email (optional for status updates)" style="width:100%; margin-bottom:12px; padding:6px; border-radius:6px; border:1px solid #cbd5e1; box-sizing:border-box;" />
      <button id="dooley-feedback-submit" style="width:100%; padding:8px; background-color:#2563eb; color:#fff; border:none; border-radius:6px; font-weight:600; cursor:pointer;">Submit</button>
      <div id="dooley-feedback-msg" style="margin-top:8px; font-size:12px; display:none; text-align:center;"></div>
    `;

    document.body.appendChild(btn);
    document.body.appendChild(modal);

    const msg = modal.querySelector("#dooley-feedback-msg");

    btn.addEventListener("click", () => {
      msg.style.display = 'none';
      msg.innerText = '';
      modal.style.display = modal.style.display === "none" ? "block" : "none";
    });

    modal.querySelector("#dooley-feedback-close").addEventListener("click", () => {
      modal.style.display = "none";
    });

    modal.querySelector("#dooley-feedback-submit").addEventListener("click", async () => {
      const desc = modal.querySelector("#dooley-feedback-desc").value.trim();
      const type = modal.querySelector("#dooley-feedback-type").value;
      const email = modal.querySelector("#dooley-feedback-email").value.trim();

      if (!desc) {
        msg.innerText = "Please provide a description.";
        msg.style.color = "#dc2626";
        msg.style.display = "block";
        return;
      }

      const payload = {
        submission_id: crypto.randomUUID(),
        timestamp: new Date().toISOString(),
        source_site: window.location.hostname || "local-test",
        user_description: desc,
        category_hint: type,
        reporter_email: email || undefined,
        url: window.location.href,
        viewport: { width: window.innerWidth, height: window.innerHeight },
        user_agent: navigator.userAgent,
        console_logs: [...errorLogs],
        network_errors: [...networkErrors]
      };

      const endpoint = window.DOOLEY_FEEDBACK_ENDPOINT || '/api/feedback';
      try {
        const resp = await fetch(endpoint, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });

        if (resp.ok) {
          msg.innerText = "Thank you! Feedback received.";
          msg.style.color = "#16a34a";
          msg.style.display = "block";
          setTimeout(() => {
            modal.style.display = "none";
            msg.style.display = "none";
            modal.querySelector("#dooley-feedback-desc").value = "";
          }, 2000);
        } else {
          console.error("Feedback submission failed with server error status:", resp.status, resp.statusText, await resp.text());
          msg.innerText = "Submission failed. Please try again.";
          msg.style.color = "#dc2626";
          msg.style.display = "block";
        }
      } catch (err) {
        console.error("Feedback submission error:", err);
        msg.innerText = "Submission failed. Please try again.";
        msg.style.color = "#dc2626";
        msg.style.display = "block";
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initWidget);
  } else {
    initWidget();
  }
})();
