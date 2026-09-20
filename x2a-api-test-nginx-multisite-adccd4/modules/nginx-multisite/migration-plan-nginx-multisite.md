---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Web server cookbook that configures nginx with 3 SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local), implements comprehensive security hardening with fail2ban, UFW firewall, SSH restrictions, and deploys self-signed SSL certificates for each site.

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
cookbooks/nginx-multisite/files/default/test/index.html
cookbooks/nginx-multisite/files/default/ci/index.html
cookbooks/nginx-multisite/files/default/status/index.html
```

## Module Explanation

The cookbook performs operations in this order:

1. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs security packages: fail2ban, ufw
   - Configures fail2ban service with custom jail configuration
   - Template: fail2ban.jail.local.erb → /etc/fail2ban/jail.local
   - Sets up UFW firewall rules: deny default, allow SSH/HTTP/HTTPS, enable firewall
   - Deploys kernel security parameters via sysctl
   - Template: sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf
   - Conditionally disables SSH root login (if node['security']['ssh']['disable_root'] = true)
   - Conditionally disables SSH password authentication (if node['security']['ssh']['password_auth'] = false)

2. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration
   - Template: nginx.conf.erb → /etc/nginx/nginx.conf
   - Deploys security configuration for nginx
   - Template: security.conf.erb → /etc/nginx/conf.d/security.conf
   - Enables and starts nginx service
   - Iterations: Creates document root directories and deploys static files for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - test.cluster.local: files/default/test/index.html → /opt/server/test/index.html
     - ci.cluster.local: files/default/ci/index.html → /opt/server/ci/index.html
     - status.cluster.local: files/default/status/index.html → /opt/server/status/index.html

3. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group for certificate management
   - Creates SSL certificate directories: /etc/ssl/certs, /etc/ssl/private
   - Iterations: Generates self-signed SSL certificates for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Certificate paths: /etc/ssl/certs/{site_name}.crt, /etc/ssl/private/{site_name}.key
     - Certificate details: 2048-bit RSA, 365 days validity, US/Example organization

4. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterations: Deploys nginx virtual host configuration for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Template: site.conf.erb → /etc/nginx/sites-available/{site_name}
     - Creates symlinks: /etc/nginx/sites-enabled/{site_name} → /etc/nginx/sites-available/{site_name}
     - Each site configured with: HTTP→HTTPS redirect, SSL/TLS 1.2+, security headers, gzip compression
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
- Ports: 80 (HTTP), 443 (HTTPS), 22 (SSH)
- Network interfaces: Binds to all interfaces (0.0.0.0)

**Templates rendered**:
- fail2ban.jail.local.erb → /etc/fail2ban/jail.local (1 time)
- nginx.conf.erb → /etc/nginx/nginx.conf (1 time)
- security.conf.erb → /etc/nginx/conf.d/security.conf (1 time)
- sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf (1 time)
- site.conf.erb → /etc/nginx/sites-available/{site_name} (3 times: test.cluster.local, ci.cluster.local, status.cluster.local)

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
curl -I https://test.cluster.local
curl -s https://test.cluster.local | grep "Test Environment"
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject -dates

# Site-specific checks - ci.cluster.local
curl -I http://ci.cluster.local
curl -I https://ci.cluster.local
curl -s https://ci.cluster.local | grep -i "ci\|continuous"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject -dates

# Site-specific checks - status.cluster.local
curl -I http://status.cluster.local
curl -I https://status.cluster.local
curl -s https://status.cluster.local | grep -i "status\|monitoring"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject -dates

# SSL certificate validation - test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN=test.cluster.local'
ls -la /etc/ssl/private/test.cluster.local.key

# SSL certificate validation - ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN=ci.cluster.local'
ls -la /etc/ssl/private/ci.cluster.local.key

# SSL certificate validation - status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN=status.cluster.local'
ls -la /etc/ssl/private/status.cluster.local.key

# Security configuration validation
cat /etc/nginx/conf.d/security.conf
cat /etc/fail2ban/jail.local
fail2ban-client status
ufw status verbose

# SSH security validation
grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# Document root validation - test.cluster.local
ls -la /opt/server/test/
cat /opt/server/test/index.html | grep "test.cluster.local"
stat -c "%a %U:%G" /opt/server/test/

# Document root validation - ci.cluster.local
ls -la /opt/server/ci/
cat /opt/server/ci/index.html | grep "ci.cluster.local"
stat -c "%a %U:%G" /opt/server/ci/

# Document root validation - status.cluster.local
ls -la /opt/server/status/
cat /opt/server/status/index.html | grep "status.cluster.local"
stat -c "%a %U:%G" /opt/server/status/

# Network listening
netstat -tulpn | grep :80
netstat -tulpn | grep :443
netstat -tulpn | grep :22
ss -tlnp | grep nginx
```