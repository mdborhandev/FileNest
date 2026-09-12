"use strict";

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("auth-form");
  if (!form) return;

  const mode = form.dataset.mode;
  const btn = form.querySelector("button[type='submit']");
  const btnLabel = btn.dataset.label || "Continue";
  const alertBox = document.querySelector(".auth-card [data-alert]");

  const btnBusy = (busy) => {
    btn.disabled = busy;
    btn.innerHTML = busy
      ? `<span class="spinner"></span>${btn.dataset.busy || "Please wait…"}`
      : btnLabel;
  };

  const showAlert = (message) => {
    alertBox.textContent = message;
    alertBox.style.display = "block";
  };

  const clearAlert = () => {
    alertBox.style.display = "none";
  };

  const invalidate = (field) => {
    field.classList.add("invalid");
    field.closest(".field")?.classList.add("field-error");
  };
  const valid = (field) => {
    field.classList.remove("invalid");
    field.closest(".field")?.classList.remove("field-error");
  };

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearAlert();
    for (const el of form.querySelectorAll("input")) valid(el);

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value;
    let ok = true;

    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      invalidate(document.getElementById("email"));
      ok = false;
    }
    if (password.length < 8) {
      invalidate(document.getElementById("password"));
      ok = false;
    }
    if (!ok) {
      showAlert("Check the highlighted fields.");
      return;
    }

    btnBusy(true);
    try {
      if (mode === "login") {
        await FileNestAPI.login(email, password);
      } else {
        const fullName = document.getElementById("full_name").value.trim();
        await FileNestAPI.register({ email, password, full_name: fullName || null });
      }
      window.location.href = "/";
    } catch (err) {
      showAlert(err.message || "Something went wrong. Please try again.");
      btnBusy(false);
    }
  });

  form.querySelectorAll("input").forEach((el) => {
    el.addEventListener("input", () => valid(el));
  });
});