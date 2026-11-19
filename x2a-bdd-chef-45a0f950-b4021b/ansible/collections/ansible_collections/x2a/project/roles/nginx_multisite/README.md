# nginx_multisite

Installs and configures nginx with fail2ban, UFW, SSH hardening, kernel security settings, and dynamic virtual hosts.

## Variables

- `nginx_sites`: Mapping of site names to `document_root` and `ssl_enabled` values.
- `site_token`: Secret token supplied by the AAP credential integration.
- `nginx_multisite_secure_logging`: Hides output for secret-handling tasks; defaults to `true`.

The role generates 2048-bit RSA self-signed certificates valid for 365 days for SSL-enabled sites.
