# KOVA implementation checklist

Legend: `[x]` implemented in source · `[~]` partial / UI placeholder · `[ ]` not implemented · `[!]` blocked or unverified

## Baseline and preservation
- [x] Inspect original nested source archive and document existing architecture
- [x] Preserve Flask app factory, SQLite, scrypt auth, CSRF, lockout and audit log
- [x] Preserve role decorators, health/status APIs and admin CLI
- [x] Rebrand user-facing app and default config to KOVA
- [ ] Reproduce original unit suite in a dependency-complete environment

## Stage 1 — UI/UX
- [x] KOVA login experience and responsive application shell
- [x] Sidebar navigation and mobile navigation drawer
- [x] Overview, projects, deployments, templates, analytics, team, activity, notifications, settings, billing and new-project screens
- [x] Demonstration data labels and integration placeholders
- [x] Theme toggle and persisted local theme preference
- [x] Project search and technology filter (demonstration list)
- [~] ZIP selection checks (browser-only; no upload)
- [~] Buttons for future backend actions clearly indicate unavailable integrations
- [ ] Browser test all pages, forms, keyboard interactions and responsive breakpoints
- [ ] Browser console and accessibility audit
- [ ] Full dark/light visual review

## Stage 2 — Firebase and persistent data
- [ ] Firebase project/region/billing decision
- [ ] Authentication, Firestore and Security Rules
- [ ] Student registration/invitation, login, logout, password reset and email verification
- [ ] Admin student creation/list/deactivation
- [ ] Project/deployment data persistence
- [ ] Secure ZIP storage and cleanup
- [ ] Rules and cross-account access tests

## Stage 3 — Deployment engine
- [ ] Compare provider terms, pricing, API, runtimes and concurrency
- [ ] Coolify or other provider adapter and server-side secrets
- [ ] Durable deployment queue and worker
- [ ] ZIP inspection and safe extraction
- [ ] Isolated build/runtime execution and quotas
- [ ] Real deployment status, URLs, logs, redeploy and delete
- [ ] Scheduled preview expiration and cleanup
- [ ] Real deployment tests per framework

## Stage 4 — Production readiness
- [ ] Secret manager and configuration validation
- [ ] Payment provider integration with signed webhooks
- [ ] Backend-enforced quotas and admin controls
- [ ] Security audit, backup/restore and monitoring
- [ ] 110-user load test without 110 billable deployments
- [ ] Production acceptance and rollback plan
