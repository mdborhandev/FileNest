# FileNest — Project Analysis & Audit

**Date:** 2026-09-20  
**Scope:** `prd.md`, `design.md`, `rules.md`, `tasks.md`, `memory.md` (v0.1.0)  
**Not reviewed:** `architecture.md`, `PROJECT_STACK.md`, `CHECKLIST.md`, and the source code itself (they were not provided). Findings about code behaviour are inferred from what the docs say, and are marked *verify*.  
**Output of this audit:** revised v0.2.0 of all five documents (this file explains why they changed).

---

## 1. Executive Summary

FileNest has a solid foundation: async FastAPI, refresh-token rotation with family revocation, Argon2, a clean model/schema split, and tests for auth. The documents are well organised and consistent in tone.

The main risks are **not** in the auth code. They are in the gaps *between* the documents and between the documents and the product goal ("an iLovePDF-style tool"):

1. **There is no path for a user to actually use a PDF tool.** The MVP frontend covers only landing/login/register; tool pages are parked in a React milestone that is not started. Backend-only PDF tools are not a product.
2. **The "privacy-first" promise has no supporting design.** No retention policy, no auto-deletion, no ownership rules for files, no limits, and all security hardening is scheduled *after* file upload exists.
3. **A likely licence problem:** PyMuPDF is offered under AGPL-3.0 or a commercial licence. That matters for a network-served SaaS. It was chosen first in the stack without a licence decision.
4. **A secret is stored in a doc meant to be shared with AI assistants** (`memory.md` contains the dev DB password twice).
5. **A real session bug is designed in:** refresh-token rotation + reuse detection + `localStorage` shared between browser tabs means two tabs refreshing at once will look like token theft and log the user out.
6. **The documents contradict each other** on Celery/Redis, on the frontend stack, on quote style, on line length, and on whether tokens are "sensitive".

The revised documents fix or explicitly decide each of these (Section 3), re-baseline the plan around a shippable MVP (Section 6), and add the analysis the originals lacked: personas, competitive positioning, threat model, risk register, measurable success criteria and acceptance criteria.

---

## 2. What Is Already Good (keep)

| Area | Why it works |
| --- | --- |
| Refresh-token family rotation with reuse detection | Correct, modern pattern; hashed at rest (SHA-256) |
| Separate access/refresh secrets, `type` claim validation | Limits blast radius |
| Models ≠ Schemas rule | Prevents `hashed_password` leaks |
| Async-only DB access, `NullPool` test sessions | Avoids event-loop/connection bugs in tests |
| Storage behind an abstraction | Makes S3/MinIO migration cheap |
| Design tokens + simple component list | Enough consistency without a framework |
| Contrast, semantic HTML, labelled inputs already considered | Good accessibility baseline |

---

## 3. Findings

Severity: **High** = fix before any file upload ships or before public exposure · **Med** = fix during MVP · **Low** = tidy-up.

### 3.1 Security & privacy

| ID | Sev | Finding | Resolution (where) |
| --- | --- | --- | --- |
| F-01 | High | `memory.md` contains the dev DB password (twice: config section and test command). Anything that shares this file (AI tools, screenshots, a public repo) leaks it. | Removed; placeholders used. **Rotate the password** and check git history (`tasks.md` 2.01). |
| F-02 | High | **Multi-tab refresh race.** `refreshInFlight` de-duplicates only inside one tab. Two tabs hitting 401 together both send the same refresh token; the second is treated as *reuse* and the whole family is revoked → user logged out everywhere. | Cross-tab lock via `navigator.locks` + re-read store after acquiring (design §6); optional short server-side grace window (tasks 2.06). |
| F-03 | High | `localStorage` holds both tokens, `rules.md` calls tokens "not sensitive", and CSP is the *last* milestone. Any XSS = full account takeover. | Rule corrected; no-inline-JS + CSP moved into MVP (M6); httpOnly-cookie refresh token documented as target (D4). |
| F-04 | High | `password_resets` has no `expires_at`/`created_at`; `refresh_tokens` has no `created_at`. Reset tokens cannot expire in the DB. | Data model in PRD §8 corrected; migration task 2.03. |
| F-05 | High | No file retention or deletion policy, despite "privacy-first" being a core value proposition. | Retention default + user delete + cleanup job (PRD §7.3, tasks 3.08). |
| F-06 | High | No hostile-input handling: size, page count, decompression/pixel bombs, encrypted PDFs, timeouts, concurrency. Scheduled in the last-but-one milestone, after upload. | Limits + validation moved to the *file infrastructure* milestone (tasks 3.05, 3.10). |
| F-07 | Med | User-enumeration: `409` on register, and forgot-password response could reveal existence. No brute-force throttle on login. | Generic forgot-password response and throttling specified (PRD §7.2, tasks 6.02). |
| F-08 | Med | IDOR risk once files exist (`GET /files/{id}`). | Ownership check is an explicit rule + test (rules §12, tasks 3.11). |

### 3.2 Product & scope

| ID | Sev | Finding | Resolution |
| --- | --- | --- | --- |
| F-09 | High | MVP has PDF tool endpoints but **no UI** for them (React frontend not started). | Decision D2: server-rendered tool pages are part of MVP; React becomes post-MVP (tasks M5, M9). |
| F-10 | Med | PRD contradicts itself: "Redis is required for Celery" vs "Celery/Redis should NOT be implemented in MVP" vs NFR "background processing via Celery". | Decision D1: MVP processes synchronously with guards; Celery = M8. |
| F-11 | Med | No success metrics with numbers, no acceptance criteria, no out-of-scope list, no risks, no quotas. | Added (PRD §§9–13). |
| F-12 | Med | Tool endpoints have no request/response contract and no forward-compatibility with async jobs. | Two-step contract (upload → tool by `file_ids`) and error-code table (PRD §6). |
| F-13 | Med | Password reset is "High priority MVP" but has no email service, no pages, and no tests in the plan. | Tasks 2.07, 2.08, 5.03. |
| F-14 | Med | Guest use (iLovePDF allows tools without an account) is neither chosen nor rejected. | Open question Q1; MVP = login required (simpler abuse control). |

### 3.3 Dependencies & architecture

| ID | Sev | Finding | Resolution |
| --- | --- | --- | --- |
| F-15 | High | PyMuPDF is dual-licensed **AGPL** / commercial. Serving it over a network to users triggers AGPL obligations unless you comply or buy a commercial licence. | Decision D3: permissive stack by default (pypdf, pypdfium2, Pillow, ReportLab); PyMuPDF only after an explicit licence decision. **Verify licences before adding any dependency.** |
| F-16 | Med | `alembic.ini` hard-codes a URL (`filenest:filenest@…/filenest`) that differs from the app's real DB. Migrations may run against the wrong database. | `env.py` must read from `settings` (tasks 2.02). |
| F-17 | Low | Test/dev packages (`pytest`, `httpx`) are in the runtime `requirements.txt`. | Split into `requirements-dev.txt` (tasks 2.12). |
| F-18 | Low | Celery worker command has a typo: `--logloglevel=info`. | Fixed in `memory.md`. |
| F-19 | Med | No `pyproject.toml`; rules claim "violations will be caught by CI" but there is no CI and no linter config. | Config snippet in `rules.md` §19; CI in tasks 2.05. |

### 3.4 Design & accessibility (values verified by calculation)

| ID | Sev | Finding | Resolution |
| --- | --- | --- | --- |
| F-20 | Med | Input border `rgba(148,163,184,.15)` on the dark background is **1.28:1**. WCAG 2.2 SC 1.4.11 needs **3:1** for the boundary of a form control. | New `--border-strong: #7b8ba3` (5.16:1 on bg, 4.22:1 on card) for controls. |
| F-21 | Low | The doc states text on card is 10.7:1; actual is **11.87:1**. | Corrected; full table in design §2.3. |
| F-22 | Med | Focus relies on "browser defaults on `:focus`"; the input focus cue is a border colour change only. | Explicit `:focus-visible` ring, ≥3:1 (design §2.4). |
| F-23 | Low | `--radius` is listed for buttons but buttons are pill-shaped (`9999px`). | Added `--radius-pill`. |
| F-24 | Low | White text on `--accent-strong` is **2.77:1** (fails AA). Easy trap for hover states. | Rule: text on accent surfaces is always `--on-accent` (`#0f172a`, 6.4–8.3:1). |
| F-25 | Med | Toast and alert have no live-region semantics; screen-reader users get no feedback. | `role="status"` / `role="alert"` specified. |
| F-26 | Med | "No heavy frameworks" principle conflicts with planned React + Vite + Tailwind. | D2 + design §9 says how tokens carry over. |

### 3.5 Documentation quality

| ID | Sev | Finding | Resolution |
| --- | --- | --- | --- |
| F-27 | Med | `tasks.md` "MVP ≈ 25%" is not derived from anything and mixes MVP with post-MVP milestones. | Progress is now computed from task rows, split MVP vs post-MVP. |
| F-28 | Low | Tasks have no priority, dependency or acceptance criteria; tests are a separate milestone rather than part of each feature. | Rebuilt with IDs, P0–P2, dependencies, acceptance; tests attached to features. |
| F-29 | Low | `memory.md` duplicates a Known-Gaps bullet, embeds a timestamp that is stale immediately, and mixes stable facts with volatile ones. | Restructured into stable / volatile sections. |
| F-30 | Low | Rules contradict each other (single-quote dict keys vs `ruff format`; 88 vs 100 columns; sync `authenticate_user` signature taking `AsyncSession`; "delegate to workers" with no workers). | Resolved (rules §§4, 5, 6, 8). |

---

## 4. Decisions Recorded

These are proposals I made to resolve contradictions. They are written into the revised documents as decided; **change them if you disagree** and update the affected files.

| # | Decision | Rationale | Revisit when |
| --- | --- | --- | --- |
| D1 | **MVP processes PDFs synchronously** inside the request, using `asyncio.to_thread`, a concurrency semaphore, size/page limits and a timeout. Celery/Redis arrive in M8. | Removes an infrastructure dependency from MVP; service functions stay pure so they move into Celery unchanged. | Typical job > ~10 s, or > ~5 concurrent users |
| D2 | **MVP UI stays server-rendered + vanilla JS**, and includes tool pages. React is post-MVP and only if the UI outgrows vanilla JS (page reordering, thumbnails). | Matches the "fast, no heavy frameworks" principle; ships sooner. | Page-preview/reorder UX becomes painful |
| D3 | **Permissive-licence PDF stack** by default: `pypdf` (merge/split/rotate/basic compress), `pypdfium2` (render to images), `Pillow` + `ReportLab` (images → PDF). Stronger image recompression via `pikepdf` if needed. **No PyMuPDF/Ghostscript** unless you accept AGPL or buy a licence. | Avoids AGPL obligations for a hosted service. | Compression quality is not competitive |
| D4 | **Tokens:** MVP keeps `localStorage` but adds CSP, no inline JS, and a cross-tab refresh lock. Target state: refresh token in an `httpOnly; Secure; SameSite=Strict` cookie scoped to `/api/v1/auth`, access token in memory. | Realistic MVP path with a defined hardening step. | Before public launch (M6.06) |
| D5 | **Two-step tool API:** upload files → tools take `file_ids` and return a result file. | Matches the iLovePDF flow (upload many, reorder, then run), supports retries, and is forward-compatible with async jobs (`202` + job). | — |
| D6 | **Retention:** uploaded and result files auto-delete after **60 minutes** by default (`FILE_RETENTION_MINUTES`), user can delete sooner. | Backs the privacy claim; limits storage cost. | Dashboard "file history" feature is built |

**Open questions for you** (PRD §14): guest mode, real limits, e-mail provider, hosting region, ads vs subscription.

---

## 5. Competitive & Market Analysis

Evidence base: public review sites and pricing pages retrieved 2026-09-20, plus general product knowledge. Prices differ between sources, so treat them as directional only.

### 5.1 What the incumbent looks like (iLovePDF)

- Freemium: the free plan gives access to the tools with **limited processing, limited batch size and limited file size per task**; ads on the free tier; paid tiers add unlimited processing, desktop/mobile apps, e-signatures, workflows and no ads.
- A **Business** tier sells SSO, custom contracts and **regional file processing** — i.e. data-residency is a paid enterprise feature.
- Reviewers praise ease of use and merging; recurring complaints are **restrictive file-size limits**, **inconsistent image-conversion quality** and layout drift when converting PDF → Word.
- Delivered on web, desktop and mobile.

### 5.2 Positioning matrix

| Dimension | Incumbents (iLovePDF, Smallpdf, Adobe online tools) | FileNest opportunity |
| --- | --- | --- |
| Breadth (Word/Excel/OCR/e-sign) | Very broad | **Do not compete on breadth in MVP.** Six core tools done well. |
| File-size limits on free tier | Frequent complaint | Publish generous, honest limits; show them *before* upload |
| Privacy | Marketing claims | **Concrete and visible:** 60-min auto-delete, delete-now button, no ads, no third-party trackers |
| Ads | Present on free tiers | Ad-free by design |
| Speed | Good | Sync path for small files, no queue for common cases |
| Data residency | Enterprise-only | Choose hosting region deliberately; state it on the privacy page |
| Developer/API access | Separate paid API | Public OpenAPI already exists — a later differentiator |

**Recommended positioning statement:** *"The PDF toolkit that deletes your files in an hour and never shows ads."* Everything in the MVP should make that sentence true and provable.

### 5.3 Where FileNest will be weaker (be honest in planning)

- PDF → Word/Excel/PowerPoint needs LibreOffice-class tooling or a commercial engine; expensive and slow. Keep out of MVP.
- OCR needs Tesseract (Apache-2.0) or a cloud API; adds CPU load — belongs with background jobs (M8).
- Compression quality: a pure-Python permissive stack will trail Ghostscript-based competitors on image-heavy files. Set expectations ("up to X% smaller") and measure.

---

## 6. Re-baselined Plan

Original: "MVP ≈ 25% complete" (unsupported — it counted finished documentation files and post-MVP work). Re-computed from the new task list (`tasks.md` §Progress): **11 of 95 MVP tasks done (≈ 12 %)**, with MVP scope = M1–M7 and post-MVP = M8–M9. The new plan is more granular and includes hardening, security and release work the old plan omitted, so the figures are not directly comparable; the honest reading is that the auth foundation is solid and most of the product is still ahead. The MVP is now *smaller in surface area but complete in experience*:

```
M1 Auth ✅ → M2 Hardening → M3 File infra → M4 PDF tools → M5 Web UI → M6 Security → M7 Release
                                                                              └─ post-MVP: M8 Celery, M9 React
```

**Critical path (do in this order):**

1. Rotate the exposed password; fix alembic URL; add the missing migration columns. *(1 day)*
2. Add lint/type config + minimal CI so the rules are actually enforced.
3. Cross-tab refresh lock.
4. Storage + `PdfFile` + upload/download + validation + retention.
5. **Rotate** first (simplest), then **Merge**, **Split**, **PDF→Images**, **Images→PDF**, **Compress** last (hardest, most quality risk).
6. Web UI for each tool as its endpoint lands (vertical slices), not all at the end.
7. Rate limiting, CSP, security tests.
8. Docker + Nginx + privacy page → public beta.

---

## 7. Threat Model (condensed)

| # | Threat | Likelihood | Impact | Mitigation |
| --- | --- | --- | --- | --- |
| T1 | Token theft via XSS | Med | High | CSP, no inline JS, `escapeHTML`/`textContent`, httpOnly cookie target |
| T2 | Malicious PDF (parser bugs, decompression bomb, huge page count) | High | Med–High | Size/page/pixel caps, timeouts, no shell-outs, run as non-root, keep libs updated |
| T3 | Upload flooding / CPU exhaustion | High | Med | Rate limits, per-user quota, concurrency semaphore, Nginx body limit |
| T4 | IDOR on files | Med | High | Every file query filtered by `user_id`; UUID ids; tests |
| T5 | Path traversal via filename | Med | High | Never use client filename on disk; store by UUID key |
| T6 | Credential stuffing / brute force | High | Med | Throttling per email+IP, generic errors, Argon2 |
| T7 | Refresh-token replay | Low | High | Already mitigated (rotation + family revoke); fix multi-tab false positives |
| T8 | Data left on disk after use | Med | High (trust) | Retention job, delete endpoint, startup sweep |
| T9 | Secrets leaked in docs/logs/git | Med | High | Secret scanning, log redaction, placeholders in `memory.md` |
| T10 | Vulnerable dependencies | Med | Med | `pip-audit` in CI, Dependabot, pinned ranges |

---

## 8. Risk Register

| # | Risk | Prob. | Impact | Owner action |
| --- | --- | --- | --- | --- |
| R1 | AGPL exposure from PyMuPDF/Ghostscript | Med | High | Follow D3; record licence for each dependency in PR |
| R2 | Scope creep toward Word/OCR/e-sign | High | Med | Out-of-scope list (PRD §12); post-MVP backlog only |
| R3 | Compression underperforms competitors | Med | Med | Ship last; benchmark on a fixed corpus; label honestly |
| R4 | Sync processing blocks under load | Med | Med | Semaphore + timeout; measure; M8 ready by design |
| R5 | Storage cost/abuse from free tier | Med | Med | 60-min retention, quotas, rate limits |
| R6 | Solo-developer bandwidth | High | High | Vertical slices, small PRs, strict MVP scope, definition of done |
| R7 | Email deliverability for password reset | Med | Med | Use a transactional provider; console backend in dev |
| R8 | Docs drift from code again | High | Low | Update docs in the same PR; `memory.md` has an "as of" date |

---

## 9. Verified Contrast Table (WCAG 2.2)

Calculated with the WCAG relative-luminance formula.

| Pair | Ratio | Meets |
| --- | --- | --- |
| `--text` on `--card` | 11.87:1 | AA, AAA |
| `--text` on `--bg` | 14.48:1 | AA, AAA |
| `--muted` on `--card` | 5.71:1 | AA |
| `--muted` on `--bg` | 6.96:1 | AA |
| `--accent` on `--card` | 6.83:1 | AA |
| `--accent` on `--bg` | 8.33:1 | AA, AAA |
| `--danger` on `--card` | 5.29:1 | AA |
| `--danger` on `--bg` | 6.45:1 | AA |
| `--success` on `--card` | 8.40:1 | AA, AAA |
| Dark text on `--accent` (primary button) | 8.33:1 | AA, AAA |
| Dark text on `--accent-strong` (button hover) | 6.44:1 | AA |
| White text on `--accent-strong` | 2.77:1 | **Fails** — do not use |
| Old input border on `--bg` | 1.28:1 | **Fails** 1.4.11 (needs 3:1) |
| New `--border-strong` on `--bg` / `--card` | 5.16:1 / 4.22:1 | AA (non-text) |

---

## 10. How to Use This Package

1. Read Section 3 and **confirm or change Decisions D1–D6**.
2. Do tasks 2.01–2.03 immediately (secret, alembic URL, migration).
3. Replace the five documents in your repo; keep `ANALYSIS.md` next to them (or under `docs/`).
4. Update `memory.md`'s "as of" date whenever you finish a milestone.
5. If you send me `architecture.md` and `PROJECT_STACK.md`, I will align them with D1–D6 too.
