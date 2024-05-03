# cherry//bin

Simple Pastebin clone with Flask and Firebase

# Running development environment

## Prerequisites

GCC must be installed in the host system.

Creating venv and installing dependencies.

```
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
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
