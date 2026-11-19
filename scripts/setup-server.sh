#!/bin/sh
# Apache setup for a VM that is not using the Coolify Dockerfile.
# Lead forms post to /v1/lead. This script does not install PHP and does not
# create a lead webhook. Proxy /v1/lead only when LEADS_SERVICE_URL is set.
set -eu

if [ "$(id -u)" -ne 0 ]; then
  echo "Run as root." >&2
  exit 1
fi

if [ -z "${SITE_DOMAIN:-}" ]; then
  echo "Set SITE_DOMAIN, for example www.mbconstructionandelectric.com" >&2
  exit 1
fi

export DEBIAN_FRONTEND=noninteractive
apt-get update
apt-get install -y apache2 certbot python3-certbot-apache rsync
a2enmod rewrite headers deflate expires proxy proxy_http ssl
sed -i 's/AllowOverride None/AllowOverride All/g' /etc/apache2/apache2.conf

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT_DIR/build/build.py"
WEBROOT="/var/www/${SITE_DOMAIN}"
mkdir -p "$WEBROOT"
rsync -a --delete "$ROOT_DIR/public/" "$WEBROOT/"

PROXY=""
if [ -n "${LEADS_SERVICE_URL:-}" ]; then
  TARGET="${LEADS_SERVICE_URL%/}"
  case "$TARGET" in
    */v1/lead) ;;
    *) TARGET="${TARGET}/v1/lead" ;;
  esac
  PROXY=$(cat <<EOF
    SSLProxyEngine on
    ProxyPass /v1/lead ${TARGET}
    ProxyPassReverse /v1/lead ${TARGET}
EOF
)
fi

cat > "/etc/apache2/sites-available/${SITE_DOMAIN}.conf" <<EOF
<VirtualHost *:80>
    ServerName ${SITE_DOMAIN}
    DocumentRoot ${WEBROOT}
    <Directory ${WEBROOT}>
        AllowOverride All
        Require all granted
    </Directory>
${PROXY}
</VirtualHost>
EOF

a2ensite "${SITE_DOMAIN}.conf"
a2dissite 000-default.conf || true
apache2ctl configtest
systemctl reload apache2

if [ "${ENABLE_CERTBOT:-}" = "1" ]; then
  certbot --apache -d "${SITE_DOMAIN}" --non-interactive --agree-tos -m "${CERTBOT_EMAIL:?Set CERTBOT_EMAIL}"
fi

echo "Site files are in ${WEBROOT}"
