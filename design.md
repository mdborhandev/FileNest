# FileNest — UI/UX Design Direction

**Version:** 0.1.0  
**Date:** 2026-09-20

---

## 1. Design Principles

1. **Clarity over cleverness** — Every element must have a clear purpose. No decorative ambiguity.
2. **Dark theme by default** — Deep navy/slate palette for comfortable, extended use.
3. **Responsive** — Works on desktop, tablet, and mobile.
4. **Accessible** — WCAG AA contrast ratios, semantic HTML, keyboard navigation, focus indicators.
5. **Fast** — No heavy frameworks on frontend. Instant page loads via server-rendered HTML.
6. **Consistent** — Shared tokens (colors, spacing, typography) across all pages.

---

## 2. Design Tokens

### Color Palette

| Token | Value | Usage |
| --- | --- | --- |
| `--bg` | `#0f172a` | Page background |
| `--bg-soft` | `#111c33` | Secondary backgrounds |
| `--card` | `#1e293b` | Cards, panels, inputs |
| `--accent` | `#38bdf8` | Primary actions, links, headings |
| `--accent-strong` | `#0ea5e9` | Hover states, emphasis |
| `--text` | `#e2e8f0` | Primary text |
| `--muted` | `#94a3b8` | Secondary text, labels |
| `--danger` | `#f87171` | Errors, destructive actions |
| `--success` | `#4ade80` | Success messages |
| `--border` | `rgba(148, 163, 184, 0.15)` | Dividers, card borders |
| `--radius` | `0.75rem` | Border radius (cards, buttons) |

### Typography

| Element | Size | Weight |
| --- | --- | --- |
| Page heading | `clamp(2rem, 5vw, 3.5rem)` | 800 |
| Card heading | `1rem` | 600 |
| Auth card heading | `1.5rem` | 700 |
| Body text | `0.95rem` | 400 |
| Muted text | `0.85–0.9rem` | 400 |
| Brand | `1.1rem` | 700 |

**Font family:** `system-ui, -apple-system, "Segoe UI", sans-serif`

### Spacing

- Navigation: `1rem 2rem` padding
- Hero: `2rem` all-around
- Cards: `1.25rem` inner padding
- Auth card: `2rem` inner padding, max-width `400px`
- Form fields: `1rem` margin-bottom

---

## 3. Component Library

### Navigation Bar (`.nav`)

- Flexbox, space-between, centered vertically
- Max-width: `1100px`, centered with `margin: 0 auto`
- Brand: uppercase, letter-spacing `0.3em`, accent color, bold
- Nav links: flex with `1rem` gap

### Buttons (`.btn`)

- Inline-flex, centered, rounded (`9999px` pill shape)
- Padding: `0.65rem 1.5rem`
- Font size: `0.95rem`, weight: `600`
- Variants:
  - `.btn-primary` — accent background, dark text (CTA)
  - `.btn-ghost` — transparent, bordered (secondary)
  - `.btn-danger` — transparent, red border (destructive)
- Hover: opacity `0.88`, no underline
- Disabled: opacity `0.5`, `cursor: not-allowed`
- `.btn-block` — full width
- Loading state: spinner icon + busy label

### Cards (`.card`)

- Background: `--card`, border `--border`, radius: `--radius`
- Padding: `1.25rem`, text-align: left
- Heading: `1rem`, accent color
- Description: `0.875rem`, muted color
- Grid layout: `repeat(auto-fit, minmax(220px, 1fr))` on landing page

### Form Fields (`.field`)

- Label: `0.85rem`, muted, margin-bottom `0.35rem`
- Input: full width, bg `--bg`, border `--border`, radius `0.5rem`
- Padding: `0.65rem 0.85rem`, font `0.95rem`
- Focus: border changes to accent
- Error: border changes to danger, `.field-error` shows message
- Field message (`.field-msg`): `0.8rem`, hidden by default, shown on error in danger color

### Alerts (`.alert`)

- Rounded `0.5rem`, padding `0.75rem 1rem`, font `0.9rem`, margin-bottom `1rem`
- `.alert-error` — danger background tint, danger border, danger text

### Authentication Card (`.auth-card`)

- Background: `--card`, bordered, rounded `--radius`
- Padding: `2rem`, max-width: `400px`, full width
- Subtitle: muted, `0.9rem`, margin-bottom `1.5rem`

### Toast (`.toast`)

- Fixed position: bottom `1.5rem`, center `left: 50%`, `transform: translateX(-50%)`
- Card background, bordered, `0.9rem` font
- Padding: `0.75rem 1.25rem`, rounded `9999px`
- Opacity transitions (`0.3s`), shown via `.show` class
- Auto-hide after `2.5s`

### Spinner (`.spinner`)

- `14px × 14px`, animated rotation (`0.7s linear infinite`)
- Used in button loading states

---

## 4. Page Specifications

### Landing Page (`/`)

```
┌─────────────────────────────────────────┐
│ FileNest    API Docs    [Login | Sign up]│  ← nav
├─────────────────────────────────────────┤
│                                         │
│      PDF Tools Platform                 │  ← h1 hero
│  Manage, convert and process your       │
│  PDF documents with a fast and          │  ← subtitle
│  secure backend. Sign up, log in,       │
│  and get started in seconds.            │
│                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │ Secure   │ │Document  │ │ Background││
│  │ Auth     │ │Handling  │ │ Tasks    ││  ← cards
│  │ ...      │ │ ...      │ │ ...      ││
│  └──────────┘ └──────────┘ └──────────┘│
│                                         │
│       [ Get started ]                   │  ← CTA button
│       Status: ok — v0.1.0               │  ← health status
│                                         │
└─────────────────────────────────────────┘
```

### Login Page (`/login`)

Centered card with:
- "Welcome back" heading
- "Log in to your FileNest account." subtitle
- Email field (type=email, required)
- Password field (type=password, required, min 8 chars)
- "Log in" submit button (pills, full width)
- "Don't have an account? Sign up" footer link
- Error alert area (hidden by default)

### Register Page (`/register`)

Centered card with:
- "Create your account" heading
- "Free to use — no credit card required." subtitle
- Full name field (optional)
- Email field (required)
- Password field (required, min 8 chars)
- "Create account" submit button
- "Already have an account? Log in" footer link

### Future Pages

- **Dashboard** (`/`) when authenticated — file list, upload area, tool selection
- **PDF tool pages** — dedicated pages per tool with drag-drop upload, options, results
- **Settings page** — profile management, password change, session management

---

## 5. User Experience Flows

### Registration Flow

```
Landing → Register → Submit → Validate → Create user → Login → Dashboard
                                                              ↑
                                              If duplicate email → error shown
                                              If weak password → field highlighted
```

### Login Flow

```
Landing → Login → Submit → Validate → Authenticate → Token pair stored
                                                         ↑
                                              If wrong password → error shown
```

### Session Management Flow

```
1. User logs in → access + refresh tokens stored in localStorage
2. Each API call sends access token in Authorization header
3. If access token expires (401):
   a. Automatically call /auth/refresh with refresh token
   b. If refresh succeeds → retry original request with new access token
   c. If refresh fails → clear tokens, redirect to /login
4. User clicks Logout → call /auth/logout → clear tokens → redirect to /login
5. Refresh token rotation: each /auth/refresh returns new pair,
   previous refresh token is revoked
6. Reuse of revoked refresh token → entire family revoked
```

### Password Reset Flow

```
1. User enters email on /forgot-password
2. System sends email with reset token link → /reset-password?token=xxx
3. User enters new password, submits → token validated, password updated
4. User redirected to /login
```

---

## 6. JavaScript Architecture

### Module: `api.js` — API Client

- `FileNestAPI` global object exposing: `apiFetch`, `login`, `register`, `logout`, `me`, `TokenStore`, `ApiError`
- `TokenStore` — manages access/refresh tokens in localStorage
- `apiFetch(path, options)` — core fetch wrapper with:
  - Automatic Authorization header injection
  - Auto token refresh on 401 (deduplicated with `refreshInFlight`)
  - Session expiry handling (clear tokens, dispatch `filenest:logout` event, redirect)
- All errors thrown as `ApiError` with `status`, `message`, `body`

### Module: `auth-forms.js` — Form Handling

- Listens for `DOMContentLoaded`
- Activates on pages with `#auth-form` element
- Reads `data-mode` attribute (`login` or `register`)
- Client-side validation:
  - Email: regex pattern check
  - Password: minimum 8 characters
- Visual feedback: field highlighting, error messages, button loading state
- On success: redirect to `/`
- On error: alert box with message

### Module: `main.js` — Global Behavior

- `renderAuthArea()` — shows user email + logout button in nav when authenticated
- Listens for `filenest:logout` event to re-render nav
- Health check on load — displays status in `#status` element
- `showToast(message)` — bottom-center toast notification (auto-hide 2.5s)
- `escapeHTML(value)` — XSS prevention utility

---

## 7. Interaction Patterns

### Loading States

Buttons show spinner + busy text when submitting (via `data-busy` attribute).
Button is disabled during request to prevent double-submit.

### Error Display

- Form errors: red border on input + `.field-error` class + message text below field
- API errors: alert box in auth card (`.alert-error`)
- Session expiry: redirect to login page

### Success Feedback

- Toast notification at bottom of screen
- Auto-redirect to home page after login/register

### Accessibility

- Semantic HTML: `<main>`, `<nav>`, `<form>`, `<label>`, `<button>`
- All inputs have associated `<label>` elements
- `autocomplete` attributes on auth inputs
- Focus-visible styles via browser defaults on `:focus`
- Color contrast meets WCAG AA (text on `--card` is `#e2e8f0` on `#1e293b` = 10.7:1)
- Keyboard navigable (all interactive elements are `<a>` or `<button>`)

---

## 8. Responsive Behavior

- Hero heading uses `clamp(2rem, 5vw, 3.5rem)` — scales with viewport
- Cards grid uses `auto-fit` with `minmax(220px, 1fr)` — wraps on narrow screens
- Auth card is `max-width: 400px`, `width: 100%` — fits mobile with padding
- Navigation uses flex with `gap: 1rem` — stays horizontal until very narrow
- All text uses relative units (rem) — scales with user preferences
