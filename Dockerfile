FROM node:lts-alpine3.19 as nodeBuild

WORKDIR app
COPY assets .
RUN npm ci && npm run prod

FROM python:3.12.3-alpine3.19

WORKDIR app

COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install waitress
COPY cherrybin ./cherrybin
RUN mkdir -p ./cherrybin/static/dist
COPY --from=nodeBuild /cherrybin/static/dist ./cherrybin/static/dist

EXPOSE 5000
CMD [ "waitress-serve", "--listen", "0.0.0.0:5000", "--call", "cherrybin:create_app" ]
