#!/bin/sh
set -eu

conf="/usr/local/apache2/conf/extra/leads-proxy.conf"
mkdir -p /usr/local/apache2/conf/extra

if [ -n "${LEADS_SERVICE_URL:-}" ]; then
  target="${LEADS_SERVICE_URL%/}"
  case "$target" in
    */v1/lead) ;;
    *) target="${target}/v1/lead" ;;
  esac
  cat > "$conf" <<EOF
ProxyRequests Off
SSLProxyEngine On
ProxyPass /v1/lead ${target}
ProxyPassReverse /v1/lead ${target}
EOF
else
  echo "# LEADS_SERVICE_URL is unset; /v1/lead is not proxied." > "$conf"
fi

if ! grep -q "leads-proxy.conf" /usr/local/apache2/conf/httpd.conf; then
  echo "Include conf/extra/leads-proxy.conf" >> /usr/local/apache2/conf/httpd.conf
fi

exec httpd-foreground
