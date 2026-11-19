FROM python:3.12-slim AS site-build
WORKDIR /src
COPY data/ data/
COPY content/ content/
COPY build/ build/
COPY src/ src/
COPY assets/images/ assets/images/
RUN python3 build/build.py

FROM httpd:2.4
RUN apt-get update \
 && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/* \
 && sed -i \
      -e 's/^#LoadModule rewrite_module/LoadModule rewrite_module/' \
      -e 's/^#LoadModule headers_module/LoadModule headers_module/' \
      -e 's/^#LoadModule deflate_module/LoadModule deflate_module/' \
      -e 's/^#LoadModule expires_module/LoadModule expires_module/' \
      -e 's/^#LoadModule proxy_module/LoadModule proxy_module/' \
      -e 's/^#LoadModule proxy_http_module/LoadModule proxy_http_module/' \
      -e 's/^#LoadModule ssl_module/LoadModule ssl_module/' \
      -e 's/AllowOverride None/AllowOverride All/g' \
      /usr/local/apache2/conf/httpd.conf \
 && printf '\nServerTokens Prod\nServerSignature Off\nTraceEnable Off\n' >> /usr/local/apache2/conf/httpd.conf
COPY --from=site-build /src/public/ /usr/local/apache2/htdocs/
COPY docker/entrypoint.sh /usr/local/bin/site-entrypoint
RUN chmod 0755 /usr/local/bin/site-entrypoint
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl --fail --silent http://127.0.0.1/ -o /dev/null || exit 1
ENTRYPOINT ["site-entrypoint"]
CMD ["httpd-foreground"]
