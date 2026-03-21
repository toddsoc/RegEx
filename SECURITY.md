# Security Notes

This repository hosts internal apps behind a shared nginx gateway. The current baseline hardening is aimed at reducing abuse risk and limiting blast radius.

## Threat Model Assumptions

- Apps are internal-first, but authenticated internal/tailnet users are in scope for abuse.
- Availability and containment are primary goals.
- Public internet exposure is not assumed, but accidental exposure should still fail safely.

## Implemented Controls

### Application (regex app)

- Same-origin request enforcement for POST search requests using `Origin`/`Referer` checks.
- Maximum regex pattern length guard (`MAX_PATTERN_LENGTH`, default `256`).
- Regex timeout remains enabled (`REGEX_TIMEOUT_SECONDS`, default `0.05`).
- Dictionary config path containment: configured dictionary files must resolve under `apps/regex/data/`.

### Container Runtime

- App container runs as non-root user (`app`).
- Read-only root filesystem for `regex-app`.
- Linux capabilities dropped (`cap_drop: [ALL]`).
- `no-new-privileges` enabled.
- Writable temp paths isolated with `tmpfs` mounts (`/tmp`, `/var/tmp`).
- Gunicorn worker hardening: explicit timeout and worker recycling.

### Nginx Gateway

- Per-IP request throttling on `/RegEx/` (`30r/m` with burst).
- Request body size cap (`client_max_body_size 4k`).
- Security headers:
  - `X-Content-Type-Options: nosniff`
  - `X-Frame-Options: DENY`
  - `Referrer-Policy: same-origin`
  - `Content-Security-Policy` locked to same-origin resources (inline script currently allowed).

### Systemd Example (non-Docker)

- Adds `NoNewPrivileges`, `PrivateTmp`, `ProtectSystem=strict`, `ProtectHome`.
- Uses read-only app path and explicit writable runtime path.
- Includes `MAX_PATTERN_LENGTH` and hardened gunicorn flags.

## Security Verification Commands

Run from repo root:

```bash
docker compose -f compose/compose.yml up -d --build
docker compose -f compose/compose.yml exec -T nginx nginx -t
docker compose -f compose/compose.yml restart nginx
```

Check headers:

```bash
curl -s -D - http://localhost:8080/RegEx/ -o /dev/null
```

Check blocked cross-origin POST:

```bash
curl -s -X POST http://localhost:8080/RegEx/ \
  -H 'Origin: https://attacker.example' \
  --data-urlencode 'pattern=^a' \
  --data-urlencode 'dictionary=default'
```

Expected: response contains `Request blocked: invalid request origin.`

Check rate limiting:

```bash
for i in $(seq 1 80); do
  curl -s -o /dev/null -w '%{http_code}\n' \
    -X POST http://localhost:8080/RegEx/ \
    -H 'Origin: http://localhost:8080' \
    --data-urlencode 'pattern=^a' \
    --data-urlencode 'dictionary=default'
done | sort | uniq -c
```

Expected: mix of `200` and `429` under burst load.

Check non-root runtime:

```bash
docker compose -f compose/compose.yml exec -T regex-app sh -lc 'id'
docker compose -f compose/compose.yml exec -T regex-app sh -lc "cat /proc/1/status | grep -E '^(Name|Uid|Gid):'"
```

Expected: gunicorn process is not running as UID `0`.

## Future Improvements

- Replace inline script in template and remove `'unsafe-inline'` from CSP.
- Add explicit authentication/authorization if access expands beyond trusted internal users.
- Add dependency vulnerability scanning in CI (for Python and container base image).
- Add centralized logging/alerting for repeated `429` and invalid-origin request patterns.
