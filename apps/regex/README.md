# Regex App

Word Regex Search is the first app hosted in this repository. It is served behind the shared nginx gateway at `/RegEx/`.

## Layout

- `src/word_regex_app/`: Flask application package
- `src/wsgi.py`: gunicorn entrypoint
- `data/`: bundled fallback word list
- `tests/`: app-specific unittest suite
- `Dockerfile`: container build for this app only
- `requirements.txt`: Python dependencies for this app only

## Local testing

From the repository root:

```bash
PYTHONPATH=apps/regex/src .venv/bin/python -m unittest discover -s apps/regex/tests -v
docker compose -f compose/compose.yml up -d --build
```

Then open:

```text
http://localhost:8080/RegEx/
```

On the current Tailscale-enabled VM, the tailnet URL is:

```text
https://todd-ubuntu-docker.nuthatch-ruler.ts.net/RegEx/
```
