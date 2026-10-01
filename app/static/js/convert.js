"use strict";

function showToast(message) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 3000);
}

function showError(message) {
  const alert = document.querySelector("[data-alert]");
  if (alert) {
    alert.textContent = message;
    alert.style.display = "block";
  }
}

function clearError() {
  const alert = document.querySelector("[data-alert]");
  if (alert) alert.style.display = "none";
}

function setBusy(form, busy) {
  const btn = form.querySelector("button[type=submit]");
  if (!btn) return;
  if (busy) {
    btn.dataset.originalLabel = btn.textContent;
    btn.textContent = btn.dataset.busy || "Working…";
    btn.disabled = true;
  } else {
    btn.textContent = btn.dataset.originalLabel || btn.dataset.label || "Convert";
    btn.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("convert-form");
  const result = document.getElementById("result");
  const downloadLink = document.getElementById("download-link");
  const resultMeta = document.getElementById("result-meta");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    clearError();

    const file = form.file.files[0];
    if (!file) {
      showError("Please choose a file first.");
      return;
    }

    const toFormat = form.to_format.value;
    if (!toFormat) {
      showError("Select a target format.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("to_format", toFormat);
    if (form.from_format.value) formData.append("from_format", form.from_format.value);

    setBusy(form, true);
    result.style.display = "none";

    try {
      const res = await fetch("/api/v1/convert", { method: "POST", body: formData });
      const data = await res.json().catch(() => null);
      if (!res.ok) {
        showError((data && data.detail) || "Conversion failed");
        return;
      }
      resultMeta.textContent = `Converted to ${toFormat.toUpperCase()} — download your file:`;
      downloadLink.href = `/api/v1/convert/${data.token}`;
      result.style.display = "block";
      showToast("Conversion ready");
    } catch (err) {
      showError(err.message || "Network error");
    } finally {
      setBusy(form, false);
    }
  });
});