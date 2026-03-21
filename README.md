# Multi-App Nginx Workspace

This repository is now organized to host multiple small apps behind one shared nginx gateway. Each app lives in its own subdirectory under `apps/`, while shared deployment assets live under `infra/`, `compose/`, and `scripts/`.

Copyright (c) 2026 The Smart Guild LLC. Licensed under the MIT License. See [`LICENSE`](/home/toddsoc/projects/regex-search/LICENSE).

## Layout

- `apps/`: self-contained applications
- `apps/regex/`: the current regex search app
- `compose/compose.yml`: shared Docker Compose entrypoint
- `infra/nginx/`: shared nginx routing and site examples
- `infra/systemd/`: service examples for non-Docker deployment
- `scripts/`: shared operational helpers such as Tailscale setup

## Current apps

- [`apps/regex/README.md`](/home/toddsoc/projects/regex-search/apps/regex/README.md): Flask regex search app served at `/RegEx/`

## Shared Docker workflow

Start the shared gateway and the regex app with:

```bash
docker compose -f compose/compose.yml up -d --build
```

Then open:

```text
http://localhost:8080/RegEx/
```

## Tailscale HTTPS access

Once the Docker stack is up, publish the shared nginx endpoint with:

```bash
./scripts/tailscale_serve.sh
```

The expected app URL on this VM is:

```text
https://todd-ubuntu-docker.nuthatch-ruler.ts.net/RegEx/
```

## Adding another app

1. Create a new directory under `apps/<name>/`.
2. Add the app's container build and dependencies there.
3. Add an nginx path-routing file under `infra/nginx/conf.d/`.
4. Add a service to [`compose/compose.yml`](/home/toddsoc/projects/regex-search/compose/compose.yml).
5. Mount the app at a stable path such as `/$AppName/`.

## License

This project is licensed under the MIT License and owned by The Smart Guild LLC.

Maintainer reference for source files: Todd O'Connell `<toddsoc@linux.com>`.
