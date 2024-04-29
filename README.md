# instapasta

Simple Pastebin clone with Flask and Firebase

# Running development environment

## Prerequisites

GCC must be installed in the host system.

## Running Flask environment

```
python3 -m venv .venv
. .venv/bin/activate
pip install -e .
flask --app instapasta --debug run
```

## Running front-end environment (CSS and JS with Webpack)

```
cd assets
npm run watch
```
