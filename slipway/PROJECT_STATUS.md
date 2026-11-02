# KOVA project status

**Updated:** 2026-11-02  
**Baseline:** Existing Flask/SQLite application `Slipway`, preserved and rebranded as KOVA.  
**Current milestone:** Stage 1 UI/UX foundation — partially implemented.

## Existing functionality preserved

- Flask application factory and environment-based configuration.
- SQLite database and schema migration mechanism.
- User records with `admin` / `student` roles.
- Scrypt password hashing and constant-time verification.
- Login, logout, current-user API and signed-cookie sessions.
- CSRF protection for mutating API requests.
- Five-failure / fifteen-minute account lockout and authentication audit events.
- Role decorators, security response headers, health and platform status APIs.
- CLI commands for database initialization and administrator creation.

## Implemented in this milestone

- KOVA user-facing branding and default database/config naming (`KOVA_*` environment variables).
- Responsive application shell with collapsible mobile navigation, sidebar, workspace header and account controls.
- Overview dashboard, demonstration metrics, illustrative activity chart and quick actions.
- Projects, deployments, templates, analytics, team, activity, notifications, settings, billing and new-project views.
- Search shortcuts, light/dark theme toggle, responsive layouts and toast feedback.
- Client-side ZIP filename/type and 50 MB size checks on the new-project screen. The file remains local; this is not a server upload.
- Clear demonstration-data and integration-placeholder labels. No fake live deployments or backend persistence are claimed.

## Not implemented / blocked

- Student management APIs and UI actions.
- Project database schema, CRUD APIs and ownership enforcement.
- Server-side ZIP upload, archive safety validation and storage.
- Firebase Authentication, Firestore, Storage, Hosting and Security Rules.
- Coolify API client, queue, worker, build isolation, deployment records, real URLs and logs.
- Scheduled 24-hour preview expiry and cleanup.
- Real analytics, notifications, quotas, billing or payment processing.
- Password reset, email verification, student password change, profile editing and session management UI.
- Per-IP rate limiting and production infrastructure hardening.

## Verification

- Python source compilation: passed with `python -m compileall -q .`.
- JavaScript syntax check: passed with `node --check` for both application scripts.
- Unit tests: currently blocked in this environment because Flask is not installed and outbound package installation is unavailable. Do not treat tests as passed.
- Browser visual/interaction testing: not performed in this environment.
- Real Firebase/Coolify connections: not configured or tested.

## Next steps

1. Install `requirements.txt` in a Python 3.12 virtual environment and run the complete unit suite.
2. Perform browser checks at desktop/tablet/mobile sizes and verify all navigation, theme and forms.
3. Add student administration and student password-change APIs with authorization tests.
4. Implement project metadata, ownership enforcement and secure ZIP handling before connecting deployment services.
5. Provision Firebase and deployment infrastructure only after explicit project/account and billing decisions.

**Release assessment:** Stage 1 is a visual and interaction foundation, not a complete deployment product. KOVA is not production-ready.
