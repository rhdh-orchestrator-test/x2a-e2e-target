# nginx_multisite

Installs and configures nginx for multiple sites with TLS, security hardening, fail2ban, and UFW.

## Site definitions

Define `nginx_multisite_sites` as a mapping keyed by site name:

```yaml
nginx_multisite_sites:
  example.com:
    id: example.com
    document_root: /var/www/example.com
    ssl_enabled: true
```

The role generates self-signed certificates for SSL-enabled sites. Provide
`nginx_multisite_site_token` through an approved credential source when a site token is required.
