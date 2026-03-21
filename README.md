# Word Regex Search

Simple Flask application that accepts a regex pattern, runs it against an English word list, and returns matching words in a browser UI. The default hosted setup for this project is an nginx Docker container proxying requests to the Flask app container.

Copyright (c) 2026 The Smart Guild LLC. Licensed under the MIT License. See [`LICENSE`](/home/toddsoc/projects/regex-search/LICENSE).

## Features

- Search an English word list with arbitrary regex patterns.
- Show invalid regex errors in the UI.
- Use regex evaluation timeouts to reduce catastrophic backtracking risk.
- Prefer a system dictionary on Ubuntu, with a bundled fallback word list for local development.

## Docker deployment behind nginx

This repo includes a two-container Docker setup intended to mirror the expected hosted environment:

- `nginx`: the public web entrypoint, exposed on port `8080`
- `app`: the internal Flask/gunicorn service, reachable only from the Docker network on port `8000`

Start the stack with:

```bash
docker compose up --build
```

Then open `http://localhost:8080/RegEx/`.

The nginx container uses `deploy/nginx-word-regex-search.docker.conf` and proxies traffic to the internal `app` service at the `/RegEx/` path.

To have these containers restart after a machine reboot, make sure each service has `restart: unless-stopped` in `docker-compose.yml` (already set in this repo), start them in detached mode, and ensure Docker starts on boot:

```bash
docker compose up -d --build
sudo systemctl enable docker
```

## Tailscale HTTPS access

If this VM is already joined to your tailnet, you can publish the Docker nginx endpoint over Tailscale HTTPS. This repo includes [`tailscale_serve.sh`](/home/toddsoc/projects/regex-search/tailscale_serve.sh), which resets any existing `tailscale serve` mapping and points it at the app's HTTP listener on port `8080`.

Run it after the app stack is up:

```bash
docker compose up -d --build
chmod +x ./tailscale_serve.sh
./tailscale_serve.sh
```

The script uses `sudo tailscale serve ...` because most Linux Tailscale installs require elevated privileges unless you have already granted operator access with:

```bash
sudo tailscale set --operator=$USER
```

After the script finishes, inspect the HTTPS URL with:

```bash
tailscale serve status
```

On this VM, the expected tailnet-only URL is:

```text
https://todd-ubuntu-docker.nuthatch-ruler.ts.net/RegEx/
```

If you need to target a different local port, override `PORT` when running the script:

```bash
PORT=3000 ./tailscale_serve.sh
```

## Local development

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
$env:FLASK_APP = "wsgi:app"
flask run --debug
```

### Linux or macOS shell

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
export FLASK_APP=wsgi:app
flask run --debug
```

## Run tests

### Windows PowerShell

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

### Linux or macOS shell

```bash
.venv/bin/python -m unittest discover -s tests -v
```

The app will prefer the first word list it can find in this order:

1. `WORD_LIST_PATH`
2. `/usr/share/dict/words`
3. `data/words.txt`

## Configuration

- `WORD_LIST_PATH`: absolute path to the dictionary file to search.
- `RESULT_LIMIT`: max matches returned to the page. Default: `200`.
- `REGEX_TIMEOUT_SECONDS`: per-match regex timeout. Default: `0.05`.

## Ubuntu deployment behind nginx

1. Install system packages.

```bash
sudo apt update
sudo apt install -y python3 python3-venv nginx wamerican
```

2. Copy the project to `/var/www/word-regex-search`.

3. Create a virtual environment and install dependencies.

```bash
cd /var/www/word-regex-search
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

4. Install the systemd service.

```bash
sudo cp deploy/word-regex-search.service.example /etc/systemd/system/word-regex-search.service
sudo systemctl daemon-reload
sudo systemctl enable --now word-regex-search
```

5. Install the nginx site.

```bash
sudo cp deploy/nginx-word-regex-search.conf.example /etc/nginx/sites-available/word-regex-search
sudo ln -s /etc/nginx/sites-available/word-regex-search /etc/nginx/sites-enabled/word-regex-search
sudo nginx -t
sudo systemctl reload nginx
```

6. Update `server_name` in the nginx config and, if needed, adjust the service file paths to match your deployment directory.

Both nginx examples in this repo are configured to redirect `/` to `/RegEx/`, so the application is served from `https://$FQDN/RegEx/`.

## Notes

- Docker is the primary hosted deployment path documented in this repo.
- `gunicorn` is used inside the Docker app container and in the Ubuntu deployment example. It is not used for local Flask development on Windows.
- If you want a larger dictionary, install `wamerican`, `wbritish`, or point `WORD_LIST_PATH` at your own word file.

## License

This project is licensed under the MIT License and owned by The Smart Guild LLC.

Maintainer reference for source files: Todd O'Connell `<toddsoc@linux.com>`.
