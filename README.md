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

Create a file sweb.ini:

```
dns_sweb_api_user = YOUR_LOGIN
dns_sweb_api_key = YOUR_API_KEY
```

Set file permissions:

```
chmod 600 sweb.ini
```

## 🚀 Usage

Example for wildcard + root domain:

```
certbot certonly \
  --authenticator dns-sweb \
  --dns-sweb-credentials ./sweb.ini \
  -d example.com \
  -d '*.example.com'
```

## 🐳 Docker usage

You can use this plugin inside Docker by building an image with it installed.

Example Dockerfile:

```
FROM certbot/certbot:latest
RUN pip install git+https://github.com/YOUR_USERNAME/certbot-dns-sweb.git
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
      certbot certonly
      --authenticator dns-sweb
      --dns-sweb-credentials /etc/letsencrypt/sweb.ini
      -d example.com
      -d '*.example.com'
```
