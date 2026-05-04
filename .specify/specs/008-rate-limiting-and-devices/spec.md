# 008 - Active Security System: Rate Limiting and Device Control

## Executive Summary

This specification defines the brute-force protection, rate limiting, and
authorized-device control system in Neutral Starter Py. It protects sensitive
routes such as login, registration, and recovery through request limits per IP
and optionally per user, temporary lockouts after failed attempts, and device
fingerprinting.

The system combines HTTP-layer protection with `Flask-Limiter` and
application-layer logic in `SessionDev` for local development/admin access.

## Normative References

- `.specify/memory/constitution.md` - immutable project principles.
- `specs/000-core-system/spec.md` - request architecture and middleware.
- `specs/006-user-and-rbac/spec.md` - account state and disablement.
- `src/core/session_dev.py` - brute-force control for dev admin.
- `app/extensions.py` - `Flask-Limiter` configuration.

---

## 1. Goals

### 1.1 What this system must achieve

- brute-force protection for login and recovery flows;
- general rate limiting for APIs and sensitive routes;
- temporary account or source lockouts after repeated failures;
- device fingerprinting for authorized-device tracking;
- specific protection for local development/admin access.

### 1.2 Non-goals

- it does not replace an infrastructure WAF;
- it does not include built-in 2FA;
- it does not manage global network-level IP allow/deny lists.

---

## 2. Technical Contracts

### 2.1 Protection architecture

```text
HTTP layer (Flask-Limiter)
  - IP-based global limits
  - user-based route limits
  - route-specific limits

Application layer (SessionDev)
  - IP allowlist
  - failed-attempt tracking
  - device fingerprint validation
```

### 2.2 `Flask-Limiter`

#### General configuration

| Setting | Default | Description |
|---------|---------|-------------|
| `RATELIMIT_STORAGE_URI` | `memory://` | Storage backend |
| `RATELIMIT_STRATEGY` | `fixed-window` | Window strategy |
| `RATELIMIT_DEFAULT` | `200 per day, 50 per hour` | Default global limit |

#### Common decorators

```python
from app.extensions import limiter

@limiter.limit("10 per minute")
def login_route():
    pass

@limiter.limit("5 per minute", key_func=lambda: current_user.id)
def sensitive_operation():
    pass

@limiter.exempt
def admin_dashboard():
    pass
```

### 2.3 `SessionDev` development access control

#### Purpose

`SessionDev` manages local admin access without depending on the user database.
It uses:

- credentials from environment variables;
- configurable IP allowlisting;
- failed-attempt tracking per IP;
- signed cookies for session state;
- built-in CSRF protection.

#### Environment configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DEV_ADMIN_USER` | - | Dev admin username |
| `DEV_ADMIN_PASSWORD` | - | Plaintext password for local/dev only |
| `DEV_ADMIN_ALLOWED_IPS` | `127.0.0.1, ::1, 192.168.0.0/16...` | Allowed ranges |
| `DEV_ADMIN_AUTH_COOKIE_KEY` | `DEV_ADMIN_SESSION` | Auth cookie name |
| `DEV_ADMIN_ROLE_COOKIE_KEY` | `dev_admin_role` | Role cookie name |
| `DEV_ADMIN_CSRF_SESSION_KEY` | `DEV_ADMIN_CSRF` | CSRF session key |

#### Protection logic

```python
_LOGIN_WINDOW_SECONDS = 300
_LOGIN_MAX_ATTEMPTS = 7
_LOGIN_ATTEMPTS = {}
```

Algorithm:

1. verify the source IP against `DEV_ADMIN_ALLOWED_IPS`;
2. reject immediately if the IP is blocked;
3. verify credentials against environment variables;
4. on failure, increment the attempt counter inside the active time window;
5. block the IP if the counter exceeds `_LOGIN_MAX_ATTEMPTS`;
6. on success, create signed cookies and clear the attempt counter.

### 2.4 Device fingerprinting

#### Fingerprint components

| Component | Source | Example |
|-----------|--------|---------|
| IP address | `request.remote_addr` | `192.168.1.100` |
| User-Agent | `request.user_agent.string` | `Mozilla/5.0...` |
| Accept | `request.headers.get("Accept")` | `text/html,...` |
| Accept-Language | `request.headers.get("Accept-Language")` | `es-ES,es;q=0.9` |
| Accept-Encoding | `request.headers.get("Accept-Encoding")` | `gzip, deflate, br` |

#### Fingerprint generation

```python
def generate_fingerprint(request) -> str:
    components = [
        get_ip(),
        request.headers.get("User-Agent", ""),
        request.headers.get("Accept", ""),
        request.headers.get("Accept-Language", ""),
        request.headers.get("Accept-Encoding", ""),
    ]
    raw = "|".join(components)
    return hashlib.sha256(raw.encode()).hexdigest()[:32]
```

---

## 3. Behavior

### 3.1 Login protection flow

1. `Flask-Limiter` checks the IP quota for the route;
2. the handler evaluates credentials;
3. on success, the login continues normally;
4. on failure, the failure counter increases and may trigger a temporary
   lockout;
5. UI responses must remain generic and must not reveal whether the account
   exists.

### 3.2 `SessionDev` flow

1. request hits `/admin/dev/*`;
2. the source IP must be inside `DEV_ADMIN_ALLOWED_IPS`;
3. if auth cookies are valid, access is allowed;
4. otherwise the login form is shown;
5. failed credential submissions increment the IP counter;
6. after 7 failed attempts in 5 minutes, the source is blocked temporarily;
7. successful authentication issues signed cookies and resets the counter.

---

## 4. Security

### 4.1 Security controls

- [x] IP-based rate limiting;
- [x] optional user-based rate limiting for authenticated routes;
- [x] temporary lockouts after repeated failures;
- [x] IP allowlisting for dev admin access;
- [x] signed cookies for dev admin sessions;
- [x] CSRF protection on admin forms;
- [x] generic authentication error messages.

### 4.2 Risks and mitigations

| Risk | Mitigation | Level |
|------|------------|-------|
| Distributed brute force | IP and user limits plus temporary lockout | High |
| Credential stuffing | Rate limiting and generic failures | High |
| Dev admin session hijacking | Signed cookies, IP allowlist, CSRF | High |
| Timing leaks | Constant-time password verification where applicable | Medium |
| IP spoofing / proxy confusion | `get_ip()` with proxy awareness | Medium |

---

## 5. Implementation and Deployment

### 5.1 `Flask-Limiter` configuration

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=Config.RATELIMIT_STORAGE_URI,
    strategy=Config.RATELIMIT_STRATEGY,
    default_limits=["200 per day", "50 per hour"],
)
```

### 5.2 Recommended usage patterns

```python
@limiter.limit("5 per minute")    # auth routes
@limiter.limit("10 per minute")   # form routes
@limiter.limit("100 per minute")  # public read routes
@limiter.limit("1000 per hour", key_func=lambda: request.headers.get("X-API-Key"))
```

---

## 6. Testing

### 6.1 Required test cases

- [ ] rate limiting blocks requests after the configured threshold;
- [ ] lockouts reset after the configured time window;
- [ ] `SessionDev` rejects unauthorized IPs;
- [ ] `SessionDev` blocks an IP after 7 failed attempts in 5 minutes;
- [ ] `SessionDev` cookies cannot be forged without the secret key;
- [ ] CSRF tokens are required on admin forms;
- [ ] auth errors do not reveal whether a user exists.

---

## 7. Acceptance Criteria

- [x] sensitive routes have rate limiting configured;
- [x] temporary lockout works after repeated failures;
- [x] `SessionDev` is protected by IP allowlisting, credentials, and rate
  limiting;
- [x] admin session cookies are signed and verifiable;
- [x] admin forms use CSRF protection;
- [x] error messages do not reveal sensitive authentication information.

---

## 8. Impact and Dependencies

### 8.1 Protected routes

| Route | Type | Protection |
|-------|------|------------|
| `/sign/in` (POST) | Auth | `5/min` plus failure tracking |
| `/sign/up` (POST) | Auth | `5/min` |
| `/sign/reminder` (POST) | Auth | `3/min` |
| `/admin/dev/*` | Admin | IP allowlist, rate limiting, credentials |

---

## 9. Decisions and Risks

### 9.1 Architectural decisions

| Decision | Context | Consequence |
|----------|---------|-------------|
| `Flask-Limiter` + `SessionDev` | Two-layer protection | More code, stronger security |
| In-memory `SessionDev` counters | Simpler for development mode | Reset on restart, no horizontal scaling |
| IP allowlisting for admin | Maximize protection for sensitive access | Harder configuration on changing networks |

### 9.2 Known limitations

- `SessionDev` counters reset on server restart;
- without Redis, rate limiting remains per instance.

---

## 10. Glossary

| Term | Definition |
|------|------------|
| **Rate limiting** | Restricting request count per time window |
| **Brute force** | Systematic credential guessing |
| **IP allowlist** | Explicit list of allowed IPs or ranges |
| **Device fingerprint** | Hash of client/device characteristics |
| **Time window** | Period used to count attempts |
