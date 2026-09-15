---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Multi-site nginx web server with SSL-enabled virtual hosts for 3 subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), including comprehensive security hardening with fail2ban, UFW firewall, SSH restrictions, and self-signed SSL certificates.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:
- **test.cluster.local**: Testing and development environment
  - Location/Path: /opt/server/test
  - Port/Socket: HTTP 80 (redirects to HTTPS), HTTPS 443
  - Key Config: SSL enabled, self-signed certificate, security headers, gzip compression

- **ci.cluster.local**: Continuous integration environment
  - Location/Path: /opt/server/ci
  - Port/Socket: HTTP 80 (redirects to HTTPS), HTTPS 443
  - Key Config: SSL enabled, self-signed certificate, security headers, gzip compression

- **status.cluster.local**: Status monitoring environment
  - Location/Path: /opt/server/status
  - Port/Socket: HTTP 80 (redirects to HTTPS), HTTPS 443
  - Key Config: SSL enabled, self-signed certificate, security headers, gzip compression

## File Structure

**Recipes:**
```
cookbooks/nginx-multisite/recipes/default.rb
cookbooks/nginx-multisite/recipes/security.rb
cookbooks/nginx-multisite/recipes/nginx.rb
cookbooks/nginx-multisite/recipes/ssl.rb
cookbooks/nginx-multisite/recipes/sites.rb
```

**Templates:**
```
cookbooks/nginx-multisite/templates/default/fail2ban.jail.local.erb
cookbooks/nginx-multisite/templates/default/nginx.conf.erb
cookbooks/nginx-multisite/templates/default/security.conf.erb
cookbooks/nginx-multisite/templates/default/site.conf.erb
cookbooks/nginx-multisite/templates/default/sysctl-security.conf.erb
```

**Attributes:**
```
cookbooks/nginx-multisite/attributes/default.rb
```

**Files:**
```
cookbooks/nginx-multisite/files/default/test/index.html
cookbooks/nginx-multisite/files/default/ci/index.html
cookbooks/nginx-multisite/files/default/status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs security packages: fail2ban, ufw
   - Configures fail2ban service with SSH, nginx-http-auth, nginx-limit-req, and nginx-botsearch jails
   - Deploys fail2ban configuration template to /etc/fail2ban/jail.local
     - Template: fail2ban.jail.local.erb → /etc/fail2ban/jail.local
   - Configures UFW firewall with default deny policy
   - Allows UFW ports: SSH (22), HTTP (80), HTTPS (443)
   - Enables UFW firewall
   - Deploys kernel security parameters template to /etc/sysctl.d/99-security.conf
     - Template: sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf
   - Conditionally disables SSH root login (if node['security']['ssh']['disable_root'] = true)
   - Conditionally disables SSH password authentication (if node['security']['ssh']['password_auth'] = false)

2. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration template to /etc/nginx/nginx.conf
     - Template: nginx.conf.erb → /etc/nginx/nginx.conf
   - Deploys nginx security configuration template to /etc/nginx/conf.d/security.conf
     - Template: security.conf.erb → /etc/nginx/conf.d/security.conf
   - Enables and starts nginx service
   - Creates document root directory for test.cluster.local
   - Creates document root directory for ci.cluster.local
   - Creates document root directory for status.cluster.local
   - Deploys static index.html file to test.cluster.local document root
   - Deploys static index.html file to ci.cluster.local document root
   - Deploys static index.html file to status.cluster.local document root

3. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group
   - Creates SSL certificate directory: /etc/ssl/certs (mode 755)
   - Creates SSL private key directory: /etc/ssl/private (mode 710, group ssl-cert)
   - Generates self-signed SSL certificate for test.cluster.local (365 days validity)
     - Certificate path: /etc/ssl/certs/test.cluster.local.crt
     - Private key path: /etc/ssl/private/test.cluster.local.key
   - Generates self-signed SSL certificate for ci.cluster.local (365 days validity)
     - Certificate path: /etc/ssl/certs/ci.cluster.local.crt
     - Private key path: /etc/ssl/private/ci.cluster.local.key
   - Generates self-signed SSL certificate for status.cluster.local (365 days validity)
     - Certificate path: /etc/ssl/certs/status.cluster.local.crt
     - Private key path: /etc/ssl/private/status.cluster.local.key
   - Sets key permissions: 640, owner root:ssl-cert for all private keys

4. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Deploys nginx virtual host configuration for test.cluster.local
     - Template: site.conf.erb → /etc/nginx/sites-available/test.cluster.local
   - Creates symbolic link to enable test.cluster.local site
     - Link: /etc/nginx/sites-available/test.cluster.local → /etc/nginx/sites-enabled/test.cluster.local
   - Deploys nginx virtual host configuration for ci.cluster.local
     - Template: site.conf.erb → /etc/nginx/sites-available/ci.cluster.local
   - Creates symbolic link to enable ci.cluster.local site
     - Link: /etc/nginx/sites-available/ci.cluster.local → /etc/nginx/sites-enabled/ci.cluster.local
   - Deploys nginx virtual host configuration for status.cluster.local
     - Template: site.conf.erb → /etc/nginx/sites-available/status.cluster.local
   - Creates symbolic link to enable status.cluster.local site
     - Link: /etc/nginx/sites-available/status.cluster.local → /etc/nginx/sites-enabled/status.cluster.local
   - Removes default nginx site configuration

## Dependencies

**External cookbook dependencies**: None (standalone cookbook)
**System package dependencies**: nginx, fail2ban, ufw, openssl, ca-certificates
**Service dependencies**: nginx, fail2ban, ssh, ufw

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
- Ports listening: 80 (HTTP), 443 (HTTPS), 22 (SSH)
- Unix sockets: None
- Network interfaces: All interfaces (0.0.0.0)

**Templates rendered**:
- nginx.conf.erb renders 1 time to /etc/nginx/nginx.conf
- security.conf.erb renders 1 time to /etc/nginx/conf.d/security.conf
- site.conf.erb renders 3 times (once per site) to /etc/nginx/sites-available/{site_name}
- fail2ban.jail.local.erb renders 1 time to /etc/fail2ban/jail.local
- sysctl-security.conf.erb renders 1 time to /etc/sysctl.d/99-security.conf

## Pre-flight checks:
```bash
# Service status
systemctl status nginx
systemctl status fail2ban
systemctl status ssh
ps aux | grep nginx
ps aux | grep fail2ban

# Nginx configuration validation
nginx -t
nginx -T | grep -E 'server_name|listen|ssl_certificate'

# Site-specific checks - test.cluster.local
curl -I http://test.cluster.local
curl -I https://test.cluster.local
curl -s https://test.cluster.local | grep "Test Environment"
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Site-specific checks - ci.cluster.local
curl -I http://ci.cluster.local
curl -I https://ci.cluster.local
curl -s https://ci.cluster.local | grep "CI Environment"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# Site-specific checks - status.cluster.local
curl -I http://status.cluster.local
curl -I https://status.cluster.local
curl -s https://status.cluster.local | grep "Status Environment"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject

# SSL certificate verification - test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN=test.cluster.local'
ls -la /etc/ssl/private/test.cluster.local.key

# SSL certificate verification - ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN=ci.cluster.local'
ls -la /etc/ssl/private/ci.cluster.local.key

# SSL certificate verification - status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN=status.cluster.local'
ls -la /etc/ssl/private/status.cluster.local.key

# Security configuration validation
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
fail2ban-client status nginx-limit-req
fail2ban-client status nginx-botsearch
ufw status verbose
cat /etc/fail2ban/jail.local | grep -E 'enabled|bantime|maxretry'
sysctl -a | grep -f /etc/sysctl.d/99-security.conf

# SSH security validation
grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# File permissions and ownership
ls -la /opt/server/test/index.html
ls -la /opt/server/ci/index.html
ls -la /opt/server/status/index.html
ls -ld /opt/server/test /opt/server/ci /opt/server/status

# Network listening
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :22
ss -tlnp | grep nginx
ss -tlnp | grep sshd

# Security headers validation - test.cluster.local
curl -I https://test.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'

# Security headers validation - ci.cluster.local
curl -I https://ci.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'

# Security headers validation - status.cluster.local
curl -I https://status.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'

# Firewall validation
iptables -L -n | grep -E '80|443|22'
ufw status numbered
```