# FileNest — UI/UX Design Direction

**Version:** 0.2.0  
**Date:** 2026-09-20  
**Companion docs:** `prd.md` (what to build), `ANALYSIS.md` (why this revision), `tasks.md` (Milestone 5 = web UI)

**What changed from 0.1.0:** verified contrast numbers (one was wrong), a stronger control border (old one failed WCAG 1.4.11), explicit focus/motion rules, tool-page design (the original had none), dashboard and password-reset pages, error-code → message mapping, a cross-tab refresh lock, and a plan for carrying tokens to React.

---

## 1. Design Principles

1. **Clarity over cleverness** — every element has a clear purpose.
2. **Trust is a feature** — privacy facts (expiry time, delete button, limits) are visible in the UI, not buried in a policy.
3. **Dark by default, contrast-safe** — deep navy palette; every text/control pair verified (§2.3).
4. **Fast** — server-rendered HTML, one small JS file per concern, no framework in MVP.
5. **Accessible** — WCAG 2.2 AA, semantic HTML, keyboard-first, visible focus, live regions.
6. **Mobile-first** — the primary task (upload → run → download) must work on a 360 px phone.
7. **Consistent** — all colour/spacing/type come from tokens; no one-off values.
8. **Honest states** — always show what is happening (loading, error, empty, done) in plain language.

---

## 2. Design Tokens

### 2.1 Colour

| Token | Value | Usage |
| --- | --- | --- |
| `--bg` | `#0f172a` | Page background |
| `--bg-soft` | `#111c33` | Secondary backgrounds, zebra rows |
| `--card` | `#1e293b` | Cards, panels |
| `--card-hover` | `#243349` | Interactive card hover |
| `--accent` | `#38bdf8` | Primary actions, links, headings |
| `--accent-strong` | `#0ea5e9` | Hover/pressed backgrounds |
| `--on-accent` | `#0f172a` | **Text/icons placed on `--accent` or `--accent-strong`** (never white) |
| `--text` | `#e2e8f0` | Primary text |
| `--muted` | `#94a3b8` | Secondary text, labels |
| `--danger` | `#f87171` | Errors, destructive actions |
| `--success` | `#4ade80` | Success messages |
| `--warning` | `#fbbf24` | Non-blocking cautions (e.g. "no size saving possible") |
| `--border` | `rgba(148,163,184,0.15)` | **Decorative** dividers and card outlines only |
| `--border-strong` | `#7b8ba3` | **Form controls, dropzone, focusable outlines** (needs ≥ 3:1) |
| `--focus` | `#7dd3fc` | Focus ring colour |
| `--radius` | `0.75rem` | Cards, panels |
| `--radius-sm` | `0.5rem` | Inputs, alerts |
| `--radius-pill` | `9999px` | Buttons, toast, badges |

### 2.2 Typography

Font stack: `system-ui, -apple-system, "Segoe UI", sans-serif` (monospace for file names only: `ui-monospace, "SF Mono", Menlo, Consolas, monospace`).

| Element | Size | Weight | Line-height |
| --- | --- | --- | --- |
| Page heading (hero) | `clamp(2rem, 5vw, 3.5rem)` | 800 | 1.1 |
| Tool page heading | `clamp(1.5rem, 3.5vw, 2.25rem)` | 700 | 1.2 |
| Auth card heading | `1.5rem` | 700 | 1.25 |
| Card heading | `1rem` | 600 | 1.3 |
| Body | `0.95rem` | 400 | 1.6 |
| Muted / helper | `0.85–0.9rem` | 400 | 1.5 |
| Field label | `0.85rem` | 500 | 1.4 |
| Brand | `1.1rem` | 700 | 1 |

Minimum interactive text size is `0.85rem`. Body copy never below `0.95rem` on mobile.

### 2.3 Contrast verification (WCAG 2.2, calculated)

| Pair | Ratio | Result |
| --- | --- | --- |
| `--text` on `--card` | **11.87:1** *(0.1.0 claimed 10.7)* | AA / AAA |
| `--text` on `--bg` | 14.48:1 | AA / AAA |
| `--muted` on `--card` | 5.71:1 | AA |
| `--muted` on `--bg` | 6.96:1 | AA |
| `--accent` on `--card` / `--bg` | 6.83:1 / 8.33:1 | AA |
| `--danger` on `--card` / `--bg` | 5.29:1 / 6.45:1 | AA |
| `--success` on `--card` | 8.40:1 | AA / AAA |
| `--on-accent` on `--accent` | 8.33:1 | AA / AAA |
| `--on-accent` on `--accent-strong` | 6.44:1 | AA |
| White on `--accent-strong` | 2.77:1 | **Fail — never use** |
| Old control border (`--border` on `--bg`) | 1.28:1 | **Fail** SC 1.4.11 (needs 3:1) |
| `--border-strong` on `--bg` / `--card` | 5.16:1 / 4.22:1 | Pass (non-text) |

Rule: **information is never conveyed by colour alone** — errors also get an icon/text, required fields get text, success gets text.

### 2.4 Focus, motion and touch

- **Focus ring:** every interactive element gets a visible ring using `:focus-visible` — `outline: 3px solid var(--focus); outline-offset: 2px;`. Do not rely on browser defaults or on a border-colour change alone. (`--focus` on `--bg` ≈ 10:1.)
- **Motion:** transitions ≤ 0.3 s; wrap non-essential animation in `@media (prefers-reduced-motion: no-preference)`. Spinner becomes a static "…" indicator under reduced motion.
- **Touch targets:** minimum 44 × 44 px for buttons and file-row actions (WCAG 2.2 SC 2.5.8 minimum is 24 px; 44 is the comfort target).

### 2.5 Spacing and layout

Scale (rem): `0.25, 0.5, 0.75, 1, 1.25, 1.5, 2, 3`.

| Area | Value |
| --- | --- |
| Nav padding | `1rem 2rem` (≥ 768 px), `0.75rem 1rem` (< 768 px) |
| Page container | `max-width: 1100px; margin-inline: auto; padding-inline: clamp(1rem, 4vw, 2rem)` |
| Hero | `2rem` all round |
| Card | `1.25rem` padding |
| Auth card | `2rem` padding, `max-width: 400px` |
| Form field gap | `1rem` |
| Tool workspace | `max-width: 760px` |

Breakpoints: `480px` (phone → large phone), `768px` (tablet), `1100px` (content max).

### 2.6 Token block (drop into `styles.css`)

```css
:root {
  --bg: #0f172a;  --bg-soft: #111c33;  --card: #1e293b;  --card-hover: #243349;
  --accent: #38bdf8;  --accent-strong: #0ea5e9;  --on-accent: #0f172a;
  --text: #e2e8f0;  --muted: #94a3b8;
  --danger: #f87171;  --success: #4ade80;  --warning: #fbbf24;
  --border: rgba(148, 163, 184, 0.15);  --border-strong: #7b8ba3;  --focus: #7dd3fc;
  --radius: 0.75rem;  --radius-sm: 0.5rem;  --radius-pill: 9999px;
  color-scheme: dark;
}

:focus-visible { outline: 3px solid var(--focus); outline-offset: 2px; }

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after { animation-duration: 0.01ms !important;
                            animation-iteration-count: 1 !important;
                            transition-duration: 0.01ms !important; }
}
```

A light theme is **not** planned for MVP. If added, override tokens under `@media (prefers-color-scheme: light)`, re-verify every pair in §2.3, and keep `color-scheme` in sync.

---

## 3. Component Library

Shared rules: every component uses tokens only; all states (hover, focus-visible, active, disabled, loading, error) are defined; no component relies on colour alone.

### Navigation bar (`.nav`)
- Flex, `space-between`, vertically centred; inside the page container.
- Brand: uppercase, `letter-spacing: 0.3em`, accent, bold — **reduce to `0.15em` below 480 px**.
- Links: flex, `1rem` gap. Authenticated: `Dashboard`, user email (truncate with ellipsis), `Log out` button.
- Below 480 px: hide the email, keep `Dashboard` and `Log out`.
- Landmark: `<nav aria-label="Main">`. Include a **skip link** (`<a class="skip-link" href="#main">Skip to content</a>`) as the first focusable element.

### Buttons (`.btn`)
- Inline-flex, centred, pill (`--radius-pill`), padding `0.65rem 1.5rem`, min-height 44 px, `0.95rem`/600.
- Variants: `.btn-primary` (accent bg, `--on-accent` text) · `.btn-ghost` (transparent, `--border-strong` outline) · `.btn-danger` (transparent, `--danger` outline + text).
- Hover: primary → `--accent-strong` background (text stays `--on-accent`); ghost/danger → `--card-hover` background. (Replaces the old blanket "opacity 0.88".)
- Disabled: `opacity: 0.5; cursor: not-allowed`, and `aria-disabled` / `disabled` set.
- Loading: spinner + busy label from `data-busy`, `aria-busy="true"`, button disabled.
- `.btn-block` = full width. Icon-only buttons need `aria-label`.

### Cards (`.card`)
- `--card` background, `1px --border`, `--radius`, `1.25rem` padding, left-aligned.
- Heading `1rem`/accent; description `0.875rem`/muted.
- Interactive cards (`a.card`) show `--card-hover` and the focus ring; the whole card is one link.
- Grid: `repeat(auto-fit, minmax(220px, 1fr))`, gap `1rem`.

### Form fields (`.field`)
- Label `0.85rem` muted above the input, always visible (no placeholder-as-label).
- Input: full width, `--bg` background, **`1px solid var(--border-strong)`**, `--radius-sm`, padding `0.65rem 0.85rem`, `0.95rem`.
- Focus: accent border **plus** the focus ring.
- Error: `--danger` border, `aria-invalid="true"`, message in `.field-msg` linked with `aria-describedby`; message text begins with an icon or "Error:" so it is not colour-only.
- Helper text (e.g. password rules) also linked via `aria-describedby`.
- `autocomplete` values: `email`, `current-password`, `new-password`, `name`.
- Password field: "Show password" toggle button (`aria-pressed`).

### Alerts (`.alert`)
- `--radius-sm`, padding `0.75rem 1rem`, `0.9rem`. Variants: `error` (danger tint/border/text), `success`, `warning`, `info`.
- Errors use `role="alert"`; success/info use `role="status"`. Icon + text; dismiss only when non-critical.

### Authentication card (`.auth-card`)
- `--card`, bordered, `--radius`, padding `2rem`, `max-width: 400px`, `width: 100%`. Subtitle muted `0.9rem`, `1.5rem` below.

### Toast (`.toast`)
- Fixed, bottom `1.5rem`, centred, pill, card background, `0.9rem`, padding `0.75rem 1.25rem`.
- Markup: `<div class="toast" role="status" aria-live="polite">` present in the DOM from load; text changes then `.show` toggles. Auto-hide 2.5 s **for success only**; errors use inline alerts instead (toasts vanish before they can be read).
- Under reduced motion: fade only, no movement.

### Spinner (`.spinner`)
- 14 × 14 px, `0.7s linear infinite`; decorative (`aria-hidden="true"`); status text carries the meaning.

### New components (tool experience)

**Tool card** (`.tool-card`) — an interactive card with icon (inline SVG, `aria-hidden`), name, one-line description. Used on landing and dashboard.

**Dropzone** (`.dropzone`)
- A real `<label>` wrapping `<input type="file" multiple>` so it works with keyboard, screen readers and mobile pickers; drag-and-drop is an enhancement.
- Dashed `--border-strong` outline; on drag-over: accent border + `--card-hover`.
- Text: "**Choose files** or drop them here" · "PDF only · up to 25 MB each · up to 10 files". Limits come from `/api/v1/config` (or a data attribute) — never hard-coded.
- Rejections are listed inline per file with the reason (see §7.4).

**File row** (`.file-row`)
- Columns: order number · file name (monospace, ellipsis) · pages · size · expiry · actions.
- Actions: **Move up / Move down** buttons (keyboard-accessible reordering; drag handle is optional), **Remove**. Each has a visible text label on ≥ 480 px and `aria-label` always.
- Expiry text: "Deleted automatically at 14:32".
- On < 480 px the row becomes a two-line card.

**Progress / status** (`.status`)
- Steps: `Uploading… → Processing… → Ready`. `role="status"`; announced text changes. Determinate `<progress>` for uploads (XHR/fetch streams), indeterminate text for processing.

**Result panel** (`.result`)
- Big `Download` primary button, file name, size, expiry, `Delete now` (ghost/danger), `Start over`.
- Compress: "4.8 MB → 1.9 MB (−60 %)"; if not reduced: warning alert "This file is already well optimised — no size saving was possible."

**Badge** (`.badge`) — small pill for `PDF`, `PNG`, page counts. Text always present.

**Empty state** (`.empty`) — icon, one sentence, one primary action ("Choose your first file").

**Segmented control / radio group** — for compress level, rotate angle, image format. Use `<fieldset><legend>` with native radios styled as buttons; arrow-key behaviour comes from native radios.

---

## 4. Page Specifications

### 4.1 Landing (`/`, signed out)

```
┌─────────────────────────────────────────────────────┐
│ FILENEST     Tools   API Docs      [Log in][Sign up] │  ← nav
├─────────────────────────────────────────────────────┤
│        PDF tools that delete your files               │  ← h1
│        after an hour. No ads.                         │
│  Merge, split, compress, rotate and convert PDFs.     │  ← subtitle
│              [ Get started — it's free ]              │  ← CTA
│                                                       │
│  ┌ Merge ┐ ┌ Split ┐ ┌Compress┐ ┌Rotate ┐ ┌ Convert┐│  ← tool cards
│                                                       │
│  ┌ Private by design ┐ ┌ No ads, clear limits ┐ ┌ Fast┐│  ← value cards
│                                                       │
│  Status: OK · v0.2.0                                  │  ← health (muted)
└─────────────────────────────────────────────────────┘
```

The CTA appears before the cards (the original placed it after them). Health status uses `role="status"` and shows a text state, not only a colour.

### 4.2 Login (`/login`)
Centered auth card: "Welcome back" · "Log in to your FileNest account." · Email · Password (+ show toggle) · **Log in** (block) · links: "Forgot password?" and "Don't have an account? Sign up". Error alert area above the form (`role="alert"`, hidden by default). On load, focus the email field. Session-expired notice via `?reason=expired`.

### 4.3 Register (`/register`)
"Create your account" · "Free to use — no credit card required." · Full name (optional) · Email · Password with visible rule "At least 8 characters" · **Create account** · "Already have an account? Log in". One-line privacy note: "Files are deleted automatically after 60 minutes."

### 4.4 Forgot password (`/forgot-password`) — new
Email field → **Send reset link** → always show: "If an account exists for that email, we've sent a reset link." (matches the API's generic `202`).

### 4.5 Reset password (`/reset-password?token=…`) — new
New password + confirm → **Set new password** → on success redirect to `/login?reset=1` with a success alert. Invalid/expired token → error alert with link to request a new one. Remove the token from the URL after reading it (`history.replaceState`).

### 4.6 Dashboard (`/` when authenticated, or `/app`)

```
┌───────────────────────────────────────────────────┐
│ FILENEST   Dashboard          you@mail.com [Log out]│
├───────────────────────────────────────────────────┤
│  What would you like to do?                         │
│  [Merge][Split][Compress][Rotate][PDF→Images][Images→PDF]│
│                                                     │
│  Recent files (deleted automatically)               │
│  ┌ report.pdf · 2.1 MB · deletes 14:32 · [↓][🗑] ┐  │
│  └ (empty state: "No files yet")                  ┘  │
└───────────────────────────────────────────────────┘
```

### 4.7 Tool page (`/tools/<tool>`) — shared shell for all six tools

```
┌─────────────────────────────────────────────────────┐
│ ← All tools                                          │
│ Merge PDF                                            │
│ Combine several PDFs into one, in the order you want.│
│                                                      │
│ 1 Add files      ┌ Dropzone ───────────────────────┐ │
│                  └ PDF only · ≤ 25 MB · ≤ 10 files ┘ │
│ 2 Arrange        file-row ▲▼ ✕ …                     │
│ 3 Options        (tool-specific controls)            │
│ [ Merge PDF ]    ← disabled until valid              │
│                                                      │
│ 4 Result         Status → Result panel               │
└─────────────────────────────────────────────────────┘
```

The numbered steps are real headings (`<h2>`), the workspace is one `<main>`, and focus moves to the result heading (or the error alert) when processing finishes.

| Tool | Step-3 options |
| --- | --- |
| Merge | Output file name |
| Split | Mode (`ranges` / `every N` / `extract`), range input with live validation and example `1-3,5,8-` |
| Compress | Level: Low / Recommended / Extreme (with one-line explanation each) |
| Rotate | Angle 90 / 180 / 270; pages (`all` or range) |
| PDF → Images | Format (PNG/JPG), DPI (72–300), pages |
| Images → PDF | Page size (A4 / Letter / Fit), margin; EXIF orientation applied automatically |

### 4.8 Settings (`/settings`) — later (Should)
Profile (name), change password, "Sign out of all devices".

### 4.9 Error pages
404 and generic error: friendly sentence, link home, no stack traces.

---

## 5. User Experience Flows

### 5.1 Registration
```
Landing → Register → Submit → Client validation → POST /auth/register
        → 201 → POST /auth/login → tokens stored → Dashboard
   duplicate email → inline alert  ·  weak password → field error  ·  429 → "Too many attempts, try again in N s"
```

### 5.2 Login
```
Login → Submit → POST /auth/login → tokens stored → Dashboard (or ?next=)
   wrong credentials → generic alert (no hint which field)
```

### 5.3 Session management
```
1. Login → access + refresh tokens stored (localStorage in MVP; see §6.2 for hardening path).
2. Each API call sends the access token in Authorization.
3. On 401:
   a. Acquire the cross-tab lock "filenest-refresh".
   b. If the stored access token changed since the failed request → another tab already
      refreshed → retry with the new token (no API call).
   c. Otherwise POST /auth/refresh with the current refresh token → store new pair → retry once.
   d. If refresh fails → clear tokens, broadcast logout, redirect to /login?reason=expired.
4. Logout → POST /auth/logout → clear tokens → redirect to /login.
5. Every refresh rotates the pair; the previous refresh token is revoked.
6. Reuse of a revoked refresh token (attacker) → whole family revoked.
7. A `storage` event listener logs out other tabs when tokens are cleared.
```

### 5.3.1 Why the lock matters
Without it, two tabs that receive a 401 at the same moment both send the same refresh token. The first succeeds; the second looks like a replay and revokes the family — the user is logged out although nothing malicious happened.

### 5.4 Password reset
```
/forgot-password → email → 202 (generic message) → email link /reset-password?token=…
→ new password → 204 → /login?reset=1 ("Password updated — log in.")
   invalid/expired/used token → error + link to request a new one
```

### 5.5 Tool run (all tools)
```
Choose files → (client pre-check: type/size/count) → POST /files/upload (progress)
→ server validation → file rows shown with page counts + expiry
→ arrange / set options → POST /pdf/<tool> → status "Processing…"
→ result panel (Download / Delete now / Start over)
   any error → alert with mapped message, files remain so the user can retry
```

---

## 6. JavaScript Architecture

Rule: **no inline scripts or `on*=` attributes** (required for CSP). Use `data-*` hooks. Write untrusted text with `textContent`; use `escapeHTML` only when building HTML strings.

### 6.1 Modules

| File | Responsibility |
| --- | --- |
| `api.js` | `FileNestAPI`: `apiFetch`, `login`, `register`, `logout`, `me`, `forgotPassword`, `resetPassword`, `uploadFiles`, `runTool`, `deleteFile`, `downloadUrl`, `TokenStore`, `ApiError` |
| `auth-forms.js` | Login/register/forgot/reset form handling and validation (`data-mode`) |
| `main.js` | Nav auth area, health check, `showToast`, `escapeHTML`, cross-tab logout listener |
| `tool.js` *(new)* | Tool-page controller: state machine `idle → uploading → ready → processing → done | error` |
| `dropzone.js` *(new)* | Dropzone behaviour, client-side pre-checks, file-row rendering and reordering |
| `messages.js` *(new)* | Error `code` → human message table (§7.4) |

`ApiError` always carries `status`, `code`, `message`, `body`.

### 6.2 Token handling

MVP: tokens in `localStorage` under `filenest_access_token` / `filenest_refresh_token`. Because that makes XSS equal to account takeover, these safeguards are mandatory: strict CSP, no inline JS, output encoding, no third-party scripts. **Target state (M6.06):** refresh token in an `httpOnly; Secure; SameSite=Strict; Path=/api/v1/auth` cookie, access token kept in memory only; the client then needs no persistent token storage.

### 6.3 Cross-tab refresh lock (reference implementation)

```js
let refreshInFlight = null;                       // same-tab de-duplication

async function refreshOnce(usedAccessToken) {
  if (refreshInFlight) return refreshInFlight;
  const run = async () => {
    // Another tab may already have refreshed while we waited for the lock.
    if (TokenStore.getAccess() && TokenStore.getAccess() !== usedAccessToken) return true;
    const refresh = TokenStore.getRefresh();
    if (!refresh) return false;
    const res = await fetch("/api/v1/auth/refresh", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    });
    if (!res.ok) return false;
    TokenStore.set(await res.json());
    return true;
  };
  refreshInFlight = (navigator.locks
    ? navigator.locks.request("filenest-refresh", run)
    : run()
  ).finally(() => { refreshInFlight = null; });
  return refreshInFlight;
}
```

### 6.4 Auth forms

- Activate on `#auth-form`; `data-mode` = `login | register | forgot | reset`.
- Validation: email pattern; password ≥ 8 chars (≤ 128); confirm-password match on reset.
- Feedback: `aria-invalid`, `.field-msg` linked by `aria-describedby`, error summary focus, button loading state.
- Success: redirect (`/`, or `?next=` if same-origin path — **validate to prevent open redirects**).

### 6.5 Main behaviour

`renderAuthArea()`, health check into `#status`, `showToast(message)`, `escapeHTML(value)`, and a `storage`/`filenest:logout` listener to re-render the nav.

---

## 7. Interaction Patterns

### 7.1 Loading
Buttons show spinner + busy text via `data-busy` and are disabled during the request (no double submit). Long operations show the status component and keep the page interactive (Cancel where feasible).

### 7.2 Errors
- Form field errors: inline, per field.
- API/tool errors: `.alert-error` near the action, focused programmatically.
- Session expiry: redirect to `/login?reason=expired` with an explanation.
- Never show raw server messages or stack traces; always map by `code`.

### 7.3 Success
Inline result panel for tool runs; toast only for lightweight confirmations ("Copied", "File deleted"). Auth success redirects.

### 7.4 Message table (API code → user text)

| `code` | Message shown |
| --- | --- |
| `FILE_TOO_LARGE` | "That file is larger than {limit} MB. Try compressing it first or choose a smaller file." |
| `UNSUPPORTED_MEDIA_TYPE` | "Only PDF files are supported here." / "Only JPG and PNG images are supported." |
| `INVALID_PDF` | "We couldn't read this PDF. It may be damaged." |
| `ENCRYPTED_PDF` | "This PDF is password-protected. Remove the password and try again." |
| `TOO_MANY_PAGES` | "This PDF has more than {limit} pages." |
| `INVALID_RANGE` | "Enter page ranges like 1-3,5,8-." |
| `RATE_LIMITED` | "Too many requests. Please wait {n} seconds and try again." |
| `PROCESSING_TIMEOUT` | "This took too long. Try a smaller file." |
| `INVALID_CREDENTIALS` | "Incorrect email or password." |
| `EMAIL_TAKEN` | "An account with this email already exists." |
| *(network failure)* | "Can't reach FileNest. Check your connection and try again." |
| *(unknown)* | "Something went wrong. Please try again." |

### 7.5 Microcopy principles
Plain language; say what happened, why, and what to do next; no blame ("You entered…"); privacy statements are specific ("Deleted automatically at 14:32"), never vague ("securely handled").

---

## 8. Accessibility (WCAG 2.2 AA)

**Structure & semantics**
- Landmarks: `<header>`/`<nav aria-label="Main">`, one `<main id="main">`, `<footer>`. One `<h1>` per page; headings in order.
- Skip link first in the tab order. `<html lang="en">`. Unique, descriptive `<title>` per page.
- Native controls (`<button>`, `<a>`, `<input>`, radios) before ARIA; no `div` buttons.

**Forms**
- Every input has a visible `<label>`; `autocomplete` set; errors linked with `aria-describedby`, `aria-invalid` toggled; required indicated in text.
- Error summary or focus moved to first invalid field on submit.

**Keyboard**
- Whole product usable with keyboard only. Reordering has Up/Down **buttons** (drag is optional).
- Dropzone is a `<label>` for a native file input — Enter/Space opens the picker.
- Focus is moved deliberately after async changes (result heading or error alert).

**Screen readers**
- Toasts and status: `role="status"` (polite). Errors: `role="alert"`.
- Decorative icons `aria-hidden="true"`; icon-only buttons have `aria-label`.
- File rows announce name, pages, size, and expiry in text order.

**Visual**
- Contrast table in §2.3; controls ≥ 3:1; focus ring ≥ 3:1.
- Zoom to 200 % and text-spacing overrides do not break layout; no horizontal scroll at 320 px (except tables in `overflow-x: auto`).
- Minimum target size 24 px (target 44 px).

**Testing checklist (part of Definition of Done for UI tasks)**
- [ ] Keyboard-only run through the full tool flow
- [ ] axe/Lighthouse: no serious/critical issues, a11y score ≥ 95
- [ ] Screen-reader smoke test (NVDA or VoiceOver) on login + one tool
- [ ] 320 px, 768 px and 1280 px viewports
- [ ] `prefers-reduced-motion` honoured

---

## 9. Responsive Behaviour and Future React

### 9.1 Responsive rules
- Hero heading uses `clamp(2rem, 5vw, 3.5rem)`.
- Card grids use `auto-fit`/`minmax(220px, 1fr)`.
- Auth card: `max-width: 400px; width: 100%` with page padding.
- Nav stays horizontal; below 480 px it drops the email and tightens letter-spacing.
- File rows collapse to two-line cards below 480 px; primary action buttons become full-width.
- Use relative units (`rem`, `%`, `clamp`) so user font-size preferences work.

### 9.2 If/when React arrives (Milestone 9)
- Keep the tokens in §2.6 as **CSS custom properties** — they work unchanged in React with plain CSS or CSS Modules.
- If Tailwind is adopted, map tokens in `tailwind.config` (`colors: { bg: "var(--bg)", … }`) so there is still one source of truth; do not introduce a parallel palette.
- Port `api.js` logic (including the cross-tab lock) rather than rewriting it.
- Keep server-rendered pages usable until React reaches parity; migrate tool by tool.
- Adoption criterion: page thumbnails / drag reordering become too complex for vanilla JS — not "because React is standard".
