"use strict";

function escapeHTML(value) {
  return String(value).replace(/[&<>"']/g, (c) => {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
  });
}

async function renderAuthArea() {
  const area = document.querySelector("[data-auth-area]");
  if (!area) return;

  const { TokenStore } = FileNestAPI;

  if (TokenStore.access && TokenStore.refresh) {
    try {
      const user = await FileNestAPI.me();
      area.innerHTML = `
        <div class="nav-user">
          <span class="chip">${escapeHTML(user.email)}</span>
          <button class="btn btn-ghost js-logout" type="button">Log out</button>
        </div>`;
      area.querySelector(".js-logout").addEventListener("click", async () => {
        await FileNestAPI.logout();
        renderAuthArea();
        showToast("You have been logged out");
      });
      return;
    } catch (_) {
      TokenStore.clear();
    }
  }

  area.innerHTML = `
    <a class="btn btn-ghost" href="/login">Login</a>
    <a class="btn btn-primary" href="/register">Sign up</a>`;
}

function showToast(message) {
  const toast = document.getElementById("toast");
  if (!toast) return;
  toast.textContent = message;
  toast.classList.add("show");
  setTimeout(() => toast.classList.remove("show"), 2500);
}

document.addEventListener("DOMContentLoaded", () => {
  renderAuthArea();
  window.addEventListener("filenest:logout", renderAuthArea);

  const statusEl = document.getElementById("status");
  fetch("/api/v1/health")
    .then((r) => r.json())
    .then((d) => {
      statusEl.textContent = `Status: ${d.status} — v${d.version}`;
    })
    .catch(() => {
      statusEl.textContent = "Status: unavailable";
    });
});