# cherry[bin]

Simple Pastebin clone with Flask and Firebase

# Running development environment

## Prerequisites

- GCC installed in the host system

Creating venv and installing dependencies.

```
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt && pip install -r requirements-dev.txt
```

You also need a key for AES-GCM-SIV encryption.

```python
from cryptography.hazmat.primitives.ciphers.aead import AESGCMSIV
import base64
print(base64.b64encode(AESGCMSIV.generate_key(bit_length=256)))
```

Copy resulting value, omitting the `b` and paste it into `ENCRYPTION_KEY` environment variable.

## Running Flask environment

```
flask --app cherrybin --debug run
```

## Running front-end environment (CSS and JS with Webpack)

```
cd assets
npm run watch
```

# Production deployment

## Run with Podman/Docker

```
podman run --env-file ./cherrybin/.env -p 5000:5000 localhost/instapasta:latest
```

## Run with Podman/Docker Compose

```
podman-compose up -d
```

## Run on bare metal
