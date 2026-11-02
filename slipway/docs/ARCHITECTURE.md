# KOVA architecture

## Current implementation

KOVA continues the supplied Slipway codebase rather than replacing its stack.

```text
Browser
  ├── KOVA login and responsive dashboard (HTML/CSS/vanilla JS)
  └── same-origin JSON API (session cookie + CSRF token)
          |
          v
       Flask application
          ├── auth.py       login/logout/current-user + role decorators
          ├── pages.py      login and authenticated app shell
          ├── status.py     health and real platform status
          ├── users.py      user creation and validation helper
          ├── security.py   scrypt password hashing
          ├── config.py     KOVA environment configuration
          └── db.py         SQLite + numbered migrations
                    |
                    v
             SQLite database
             ├── users
             └── audit_log
```

## Frontend routes/views

The authenticated shell currently switches client-side between Overview, Projects, Deployments, Templates, Analytics, Team, Activity, Notifications, Settings, Billing and New Project. These views are a Stage 1 UI foundation. Lists and metrics explicitly marked as demo data are illustrative and are not persisted.

The ZIP selector currently validates extension and size in the browser only. It does not transmit, store, extract, build or deploy the selected archive.

## Existing security controls retained

- Scrypt password hashes.
- Signed Flask session cookie and session rotation on successful login.
- CSRF token required for mutating `/api/` calls.
- Account lockout after repeated failed logins.
- Server-side admin/login decorators.
- Same-origin Content Security Policy and basic security headers.
- Auth events recorded in `audit_log`.

## Target architecture (not yet implemented)

```text
KOVA browser
   | HTTPS + session + CSRF
   v
Flask control plane
   ├── authentication / authorization
   ├── student and project APIs
   ├── secure ZIP validation and private storage
   ├── deployment records and state machine
   ├── queue producer
   ├── Firebase adapter
   └── deployment provider adapter
          |                     |
          v                     v
Firebase services        Durable worker / isolated builds
(Auth, Firestore,         (bounded CPU/RAM/disk/time/network)
 Storage if permitted)          |
                               v
                       Coolify / compatible runtime
```

## Planned data model

The present schema contains only `users` and `audit_log`. Projects, deployments, notifications, usage and payments must be added through forward-only migrations. Every project/deployment API must enforce owner identity on the server; frontend visibility is not an authorization boundary.

## Important deployment safety

Student ZIP files are untrusted. Before extraction, validate archive paths, symlinks, file count, compressed and expanded sizes, compression ratio and time limits. Never execute code during validation. Build and run arbitrary student code only in isolated environments with resource limits and restricted network access. Never mount a host Docker socket into student workloads.

## External dependencies and decisions

Firebase and Coolify are not connected. `COOLIFY_URL` / `COOLIFY_TOKEN` are configuration placeholders only. Provider support, terms, pricing, runtime compatibility and API behavior must be verified against the actual service/version. Do not enable paid services without explicit approval.
