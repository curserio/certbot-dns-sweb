# Certbot DNS SpaceWeb Plugin

[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![Certbot](https://img.shields.io/badge/certbot-compatible-brightgreen)]()

A Certbot DNS-01 authenticator plugin for SpaceWeb hosting provider using the **official SpaceWeb API**.

---

## ✨ Features
- ✅ Supports wildcard certificates (`*.example.com`)
- ✅ Uses **official** SpaceWeb API (`https://api.sweb.ru`)
- ✅ Works with Certbot renewals
- ✅ Can be used inside Docker

---

## 📦 Installation

Clone repository:

```bash
git clone https://github.com/curserio/certbot-dns-sweb.git
cd certbot-dns-sweb
```

Install locally:

```bash
pip install .
```

Or install directly from GitHub:

```
pip install git+https://github.com/curserio/certbot-dns-sweb.git
```

## ⚙️ Configuration

Create a credentials file `sweb.ini` with the following fields:

```ini
dns_sweb_login = your_login_here
dns_sweb_password = your_password_here
```

Notes:

Either token or login + password must be provided.

base_url is optional and usually not needed.

Set file permissions:

```
chmod 600 sweb.ini
```

## Propagation Delay

DNS changes may take time to propagate. Use the --dns-sweb-propagation-seconds option to set the wait time before Certbot checks for the TXT record.

For SpaceWeb, it is recommended to wait at least 15 minutes:

```
certbot certonly \
--authenticator dns-sweb \
--dns-sweb-credentials ./sweb.ini \
--dns-sweb-propagation-seconds 900 \
-d example.com -d '*.example.com'
```

900 seconds = 15 minutes

Do not use less than 15 minutes for SpaceWeb to ensure Let's Encrypt can see the TXT record.

## 🚀 Usage

Example for wildcard + root domain:

```
certbot certonly \
  --authenticator dns-sweb \
  --dns-sweb-credentials ./sweb.ini \
  --dns-sweb-propagation-seconds 900 \
  -d example.com \
  -d '*.example.com'
```

## 🐳 Docker usage

You can use this plugin inside Docker by building an image with it installed.

Example Dockerfile:

```
FROM certbot/certbot:latest

USER root

RUN apk add --no-cache git py3-pip

RUN pip install --upgrade pip
RUN pip install git+https://github.com/curserio/certbot-dns-sweb.git
```

Example docker-compose.yml:

```
version: '3'
services:
  certbot:
    build: .
    volumes:
      - ./sweb.ini:/etc/letsencrypt/sweb.ini:ro
      - ./certs:/etc/letsencrypt
    command: >
      certonly
      --non-interactive
      --authenticator dns-sweb
      --dns-sweb-credentials /etc/letsencrypt/sweb.ini
      --dns-sweb-propagation-seconds 900
      --email your@email.com
      --agree-tos
      -d example.com
      -d '*.example.com'
```

## Issue Certificates

Using Docker Compose:

```
docker compose run --rm certbot
```

This will issue certificates for the domains defined in the compose file:

example.com

*.example.com


Renew Certificates

To renew existing certificates change `certonly` to `renew`

Certbot will automatically use the previously issued certificates stored in /etc/letsencrypt.

You can set up a cron job or systemd timer to periodically run this command to keep certificates up-to-date.
