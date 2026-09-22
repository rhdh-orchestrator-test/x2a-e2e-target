---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Web server cookbook that configures nginx with 3 SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), implements comprehensive security hardening with fail2ban, UFW firewall, SSH restrictions, and deploys self-signed SSL certificates for each site.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:
- **test.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/test
  - Port/Socket: 80 (redirects to 443), 443 (HTTPS)
  - Key Config: Self-signed SSL certificate, security headers, gzip compression

- **ci.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/ci
  - Port/Socket: 80 (redirects to 443), 443 (HTTPS)
  - Key Config: Self-signed SSL certificate, security headers, gzip compression

- **status.cluster.local**: SSL-enabled virtual host
  - Location/Path: /opt/server/status
  - Port/Socket: 80 (redirects to 443), 443 (HTTPS)
  - Key Config: Self-signed SSL certificate, security headers, gzip compression

## File Structure

```
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
cookbooks/nginx-multisite/attributes/default.rb
```

## Module Explanation

The cookbook performs operations in this order:

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Orchestrates the complete nginx multisite setup
   - Includes recipes in order: security, nginx, ssl, sites
   - Resources: include_recipe (4)

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs security packages: fail2ban, ufw
   - Configures fail2ban service with custom jail configuration
   - Sets up UFW firewall rules: deny default, allow ssh/http/https
   - Deploys system security hardening via sysctl
   - Conditionally disables SSH root login and password authentication
   - Resources: package (1), service (1), template (2), execute (6), service (1)
   - Templates:
     - fail2ban.jail.local.erb → /etc/fail2ban/jail.local
     - sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration and security configuration
   - Starts and enables nginx service
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Creates document root directory for each site
     - Deploys index.html file for each site from cookbook files
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)
   - Templates:
     - nginx.conf.erb → /etc/nginx/nginx.conf
     - security.conf.erb → /etc/nginx/conf.d/security.conf

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group and SSL directories
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Generates self-signed SSL certificate for each site
     - Sets proper permissions (640) and ownership (root:ssl-cert) for private keys
   - Resources: package (1), group (1), directory (2), execute (3)

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Deploys nginx virtual host configuration for each site
     - Creates symbolic link to enable each site
   - Removes default nginx site configuration
   - Resources: template (3), link (3), file (1)
   - Templates:
     - site.conf.erb → /etc/nginx/sites-available/test.cluster.local
     - site.conf.erb → /etc/nginx/sites-available/ci.cluster.local
     - site.conf.erb → /etc/nginx/sites-available/status.cluster.local

## Dependencies

**External cookbook dependencies**: None (standalone cookbook)
**System package dependencies**: nginx, fail2ban, ufw, openssl, ca-certificates
**Service dependencies**: nginx, fail2ban, ssh

## Credentials

**Detection Summary**: No credentials detected across all files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. SSL certificates are self-signed and generated locally without external credential requirements.

## Checks for the Migration

**Files to verify**:
- /etc/nginx/nginx.conf
- /etc/nginx/conf.d/security.conf
- /etc/nginx/sites-available/test.cluster.local
- /etc/nginx/sites-available/ci.cluster.local
- /etc/nginx/sites-available/status.cluster.local
- /etc/nginx/sites-enabled/test.cluster.local
- /etc/nginx/sites-enabled/ci.cluster.local
- /etc/nginx/sites-enabled/status.cluster.local
- /opt/server/test/index.html
- /opt/server/ci/index.html
- /opt/server/status/index.html
- /etc/ssl/certs/test.cluster.local.crt
- /etc/ssl/certs/ci.cluster.local.crt
- /etc/ssl/certs/status.cluster.local.crt
- /etc/ssl/private/test.cluster.local.key
- /etc/ssl/private/ci.cluster.local.key
- /etc/ssl/private/status.cluster.local.key
- /etc/fail2ban/jail.local
- /etc/sysctl.d/99-security.conf

**Service endpoints to check**:
- Ports listening: 80, 443, 22
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
- fail2ban.jail.local.erb renders 1 time to /etc/fail2ban/jail.local
- nginx.conf.erb renders 1 time to /etc/nginx/nginx.conf
- security.conf.erb renders 1 time to /etc/nginx/conf.d/security.conf
- sysctl-security.conf.erb renders 1 time to /etc/sysctl.d/99-security.conf
- site.conf.erb renders 3 times (once per site)

## Pre-flight checks:
```bash
# Service status
systemctl status nginx
systemctl status fail2ban
ps aux | grep nginx
ps aux | grep fail2ban

# Nginx configuration validation
nginx -t
nginx -T | grep -E 'server_name|listen|ssl_certificate'

# Site-specific checks - test.cluster.local
curl -I http://test.cluster.local
curl -I -k https://test.cluster.local
curl -s -k https://test.cluster.local | grep -i "test"
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local </dev/null 2>/dev/null | openssl x509 -noout -subject | grep "CN=test.cluster.local"

# Site-specific checks - ci.cluster.local
curl -I http://ci.cluster.local
curl -I -k https://ci.cluster.local
curl -s -k https://ci.cluster.local | grep -i "ci"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local </dev/null 2>/dev/null | openssl x509 -noout -subject | grep "CN=ci.cluster.local"

# Site-specific checks - status.cluster.local
curl -I http://status.cluster.local
curl -I -k https://status.cluster.local
curl -s -k https://status.cluster.local | grep -i "status"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local </dev/null 2>/dev/null | openssl x509 -noout -subject | grep "CN=status.cluster.local"

# SSL certificate validation - test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Issuer:|Not After'
ls -la /etc/ssl/private/test.cluster.local.key

# SSL certificate validation - ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Issuer:|Not After'
ls -la /etc/ssl/private/ci.cluster.local.key

# SSL certificate validation - status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Issuer:|Not After'
ls -la /etc/ssl/private/status.cluster.local.key

# Security configuration validation
fail2ban-client status
fail2ban-client status nginx-http-auth
ufw status verbose
cat /etc/fail2ban/jail.local | grep -E 'enabled|bantime|maxretry'
sysctl net.ipv4.conf.all.send_redirects
sysctl net.ipv4.conf.all.accept_redirects

# SSH security validation
grep "PermitRootLogin" /etc/ssh/sshd_config
grep "PasswordAuthentication" /etc/ssh/sshd_config

# Document root validation
ls -la /opt/server/test/index.html
ls -la /opt/server/ci/index.html
ls -la /opt/server/status/index.html

# Network listening
netstat -tulpn | grep :80
netstat -tulpn | grep :443
ss -tlnp | grep nginx
```