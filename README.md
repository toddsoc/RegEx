# Word Regex Search

Simple Flask application that accepts a regex pattern, runs it against an English word list, and returns matching words in a browser UI. The app is designed to run behind nginx on Ubuntu via gunicorn.

## Features

- Search an English word list with arbitrary regex patterns.
- Show invalid regex errors in the UI.
- Use regex evaluation timeouts to reduce catastrophic backtracking risk.
- Prefer a system dictionary on Ubuntu, with a bundled fallback word list for local development.

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

## Notes

- `gunicorn` is used for Ubuntu deployment. It is not used for local development on Windows.
- If you want a larger dictionary, install `wamerican`, `wbritish`, or point `WORD_LIST_PATH` at your own word file.