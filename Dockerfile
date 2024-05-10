FROM python:3.12.3-alpine3.19 as python-base

WORKDIR /app

# RUN python3 -m venv .venv
# RUN . .venv/bin/activate

COPY . /app

RUN pip install . \
	&& pip install waitress

EXPOSE 5000
CMD [ "python", "app.py" ]
# RUN ["ls", "-a"]
# CMD [ "poetry", "run", "python", "-c", "print('Hello, World!')" ]