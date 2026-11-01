# nginx_multisite

Installs and configures a hardened Nginx server hosting three HTTPS-enabled static sites.

## Role variables

- `nginx_multisite_sites`: Mapping of hostnames to document roots and SSL settings.
- `nginx_multisite_ssl_certificate_path`: Certificate directory.
- `nginx_multisite_ssl_private_key_path`: Private-key directory.
- `nginx_multisite_fail2ban_enabled`: Enable Fail2ban configuration.
- `nginx_multisite_ufw_enabled`: Configure and enable UFW.
- `nginx_multisite_ssh_disable_root`: Disable SSH root login.
- `nginx_multisite_ssh_password_auth`: Keep SSH password authentication enabled.

The role generates development self-signed certificates. Replace them with certificates managed by an approved secret-management process for production use.
