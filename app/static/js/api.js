"use strict";

const API_BASE = "/api/v1";
const LS_ACCESS = "filenest_access_token";
const LS_REFRESH = "filenest_refresh_token";

const TokenStore = {
  get access() {
    return localStorage.getItem(LS_ACCESS);
  },
  get refresh() {
    return localStorage.getItem(LS_REFRESH);
  },
  set(pair) {
    localStorage.setItem(LS_ACCESS, pair.access_token);
    localStorage.setItem(LS_REFRESH, pair.refresh_token);
  },
  clear() {
    localStorage.removeItem(LS_ACCESS);
    localStorage.removeItem(LS_REFRESH);
  },
};

class ApiError extends Error {
  constructor(status, message, body) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }
}

let refreshInFlight = null;

async function refreshAccessToken() {
  if (!refreshInFlight) {
    refreshInFlight = fetch(`${API_BASE}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: TokenStore.refresh }),
    })
      .then((res) => (res.ok ? res.json() : null))
      .then((pair) => {
        if (pair) {
          TokenStore.set(pair);
          return true;
        }
        return false;
      })
      .catch(() => false)
      .finally(() => {
        refreshInFlight = null;
      });
  }
  return refreshInFlight;
}

function onSessionExpired() {
  TokenStore.clear();
  window.dispatchEvent(new CustomEvent("filenest:logout"));
  if (!window.location.pathname.endsWith("/login")) {
    window.location.href = "/login";
  }
}

async function apiFetch(path, { method = "GET", body = null, auth = true } = {}) {
  let headers = { "Content-Type": "application/json" };
  if (auth && TokenStore.access) {
    headers.Authorization = `Bearer ${TokenStore.access}`;
  }

  let res = await fetch(`${API_BASE}${path}`, {
    method,
    headers,
    body: body !== null ? JSON.stringify(body) : undefined,
  });

  if (res.status === 401 && auth && TokenStore.refresh) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      headers.Authorization = `Bearer ${TokenStore.access}`;
      res = await fetch(`${API_BASE}${path}`, {
        method,
        headers,
        body: body !== null ? JSON.stringify(body) : undefined,
      });
    } else {
      onSessionExpired();
      throw new ApiError(401, "Session expired", null);
    }
  }

  const data = res.status === 204 ? null : await res.json().catch(() => null);
  if (!res.ok) {
    const message =
      typeof data?.detail === "string"
        ? data.detail
        : data?.detail?.length
          ? data.detail.map((d) => d.msg).join("; ")
          : "Request failed";
    throw new ApiError(res.status, message, data);
  }
  return data;
}

async function login(email, password) {
  const pair = await apiFetch("/auth/login", {
    method: "POST",
    body: { email, password },
    auth: false,
  });
  TokenStore.set(pair);
  return pair;
}

async function register({ email, password, full_name }) {
  await apiFetch("/auth/register", {
    method: "POST",
    body: { email, password, full_name },
    auth: false,
  });
  return login(email, password);
}

async function logout() {
  const refresh = TokenStore.refresh;
  TokenStore.clear();
  if (refresh) {
    try {
      await apiFetch("/auth/logout", {
        method: "POST",
        body: { refresh_token: refresh },
        auth: false,
      });
    } catch (_) {
      // already expired or unreachable; client state is cleared regardless
    }
  }
  window.dispatchEvent(new CustomEvent("filenest:logout"));
}

async function me() {
  return apiFetch("/auth/me");
}

window.FileNestAPI = { apiFetch, login, register, logout, me, TokenStore, ApiError };