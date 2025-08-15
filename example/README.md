This folder contains a minimal Compose setup to use the plugin without building a custom image.

Steps:
1) Copy `sweb.ini.example` to `sweb.ini` and fill your token or login/password.
2) Run:
   ```bash
   docker compose up --abort-on-container-exit
   ```
3) Certs will be written to `./letsencrypt`.
