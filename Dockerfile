FROM python:3.12.3-alpine3.19 as python-base

COPY requirements.txt .

RUN pip install -r requirements.txt
RUN pip install waitress

COPY cherrybin ./cherrybin

EXPOSE 5000
CMD [ "waitress-serve", "--listen", "0.0.0.0:5000", "--call", "cherrybin:create_app" ]
