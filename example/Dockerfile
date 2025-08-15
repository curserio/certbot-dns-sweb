FROM certbot/certbot:latest

USER root

RUN apk add --no-cache git py3-pip

RUN pip install --upgrade pip
RUN pip install git+https://github.com/curserio/certbot-dns-sweb.git
