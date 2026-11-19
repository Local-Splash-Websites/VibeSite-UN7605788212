# MB Construction and Electric

Static website for MB Construction and Electric, an electrician and general contractor in La Quinta, California. Pages are generated with a small Python script (standard library only) and served by Apache.

## Build

```sh
python3 build/build.py
```

The generator reads `data/site.json`, `content/`, and `src/`, and writes `public/`. Business facts (name, address, phone, hours, license) live in `data/site.json`.

## Preview

```sh
sh scripts/preview.sh
```

That builds the site and serves `public/` at `http://127.0.0.1:8080/` with clean URLs, the zero-width residential redirect, and the `/site/394d9953/` redirect.

## Deploy

Production deploys from the `Dockerfile` on merge to `main` (Coolify). The image builds the site, then serves `public/` with `httpd:2.4`. Rewrite, headers, deflate, expires, proxy, and ssl are enabled, and `AllowOverride All` is set so `public/.htaccess` applies.

`/v1/lead` is proxied to `${LEADS_SERVICE_URL}/v1/lead` when `LEADS_SERVICE_URL` is set. If the variable already ends in `/v1/lead`, that URL is used as-is. Leave it empty to run the site without a leads proxy.

A curl health check requests `http://127.0.0.1/`.

```sh
docker build -t mb-construction .
docker run --rm -p 8080:80 -e LEADS_SERVICE_URL mb-construction
```

`scripts/setup-server.sh` is the non-Coolify Apache + certbot path. It does not install a PHP lead handler. `scripts/deploy.sh` only builds and, if `DEPLOY_TARGET` is set, rsyncs `public/`.

## Environment

`.env.example` lists every variable. Do not put real secrets in it.

| Variable | Purpose |
| --- | --- |
| `LEADS_SERVICE_URL` | Upstream base URL for the `/v1/lead` proxy |
| `SITE_DOMAIN` | Apache vhost name for `scripts/setup-server.sh` |
| `SITE_NAME` | Label for local notes |
| `CANONICAL_HOST` | Deploy note. Built canonical URLs come from `data/site.json` |

The canonical host in the pages is `https://www.mbconstructionandelectric.com`.

## Forms

Quote and contact forms post to `/v1/lead` with `site_id=394d9953` and the field names `name`, `phone`, `email`, `address`, and `message`. A honeypot field is named `company_website`. Do not send test submissions.
