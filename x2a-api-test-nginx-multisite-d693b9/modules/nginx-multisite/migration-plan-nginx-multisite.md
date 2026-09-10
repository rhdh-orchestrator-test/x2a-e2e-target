---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Multi-site nginx web server hosting 3 SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) with comprehensive security hardening including fail2ban, UFW firewall, SSH restrictions, and security headers. Each site serves static content from dedicated document roots with self-signed SSL certificates.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:
- **test.cluster.local**: Testing and development environment
  - Location/Path: /opt/server/test
  - Port/Socket: HTTP 80 → HTTPS 443 (redirect)
  - Key Config: SSL enabled, self-signed certificate, security headers, gzip compression

- **ci.cluster.local**: Continuous integration environment
  - Location/Path: /opt/server/ci
  - Port/Socket: HTTP 80 → HTTPS 443 (redirect)
  - Key Config: SSL enabled, self-signed certificate, security headers, gzip compression

- **status.cluster.local**: Status monitoring environment
  - Location/Path: /opt/server/status
  - Port/Socket: HTTP 80 → HTTPS 443 (redirect)
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

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Orchestrates the complete setup by including all sub-recipes
   - Resources: include_recipe (4)

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs security packages: fail2ban, ufw
   - Configures fail2ban with custom jail settings
   - Sets up UFW firewall rules: deny default, allow SSH/HTTP/HTTPS
   - Applies kernel security parameters via sysctl
   - Conditionally disables SSH root login and password authentication
   - Resources: package (1), service (2), template (2), execute (7)
   - Templates:
     - fail2ban.jail.local.erb → /etc/fail2ban/jail.local
     - sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration and security configuration
   - Creates document root directories for all sites
   - Deploys static index.html files for each site
   - Enables and starts nginx service
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)
   - Templates:
     - nginx.conf.erb → /etc/nginx/nginx.conf
     - security.conf.erb → /etc/nginx/conf.d/security.conf
   - Iterations: Creates directories and deploys files for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Creates /opt/server/test, /opt/server/ci, /opt/server/status directories
     - Deploys corresponding index.html files from files/default/{site}/index.html

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group and SSL directories
   - Generates self-signed certificates for each site
   - Resources: package (1), group (1), directory (2), execute (3)
   - Iterations: Generates certificates for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Generates RSA 2048-bit self-signed certificates valid for 365 days
     - Certificate: /etc/ssl/certs/{site_name}.crt
     - Private key: /etc/ssl/private/{site_name}.key (mode 640, owner root:ssl-cert)

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Creates nginx virtual host configurations for each site
   - Enables sites by creating symlinks in sites-enabled
   - Removes default nginx site
   - Resources: template (3), link (3), file (1)
   - Templates:
     - site.conf.erb → /etc/nginx/sites-available/{site_name} (3 times)
   - Iterations: Configures sites for **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Each site configured with HTTP→HTTPS redirect, SSL/TLS 1.2+, security headers
     - HSTS, CSP, X-Frame-Options, gzip compression enabled
     - Access/error logs: /var/log/nginx/{site_name}_{access|error}.log

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

No credentials or secrets were detected in this cookbook. All SSL certificates are self-signed and generated locally. All configuration values appear to be non-sensitive.

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
- Ports listening: 80 (HTTP), 443 (HTTPS)
- Network interfaces: All interfaces (0.0.0.0:80, 0.0.0.0:443)

**Templates rendered**:
- fail2ban.jail.local.erb → /etc/fail2ban/jail.local (1 time)
- nginx.conf.erb → /etc/nginx/nginx.conf (1 time)
- security.conf.erb → /etc/nginx/conf.d/security.conf (1 time)
- sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf (1 time)
- site.conf.erb → /etc/nginx/sites-available/{site_name} (3 times)

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

# Site checks - verify each site individually
# Site: test.cluster.local
curl -I http://test.cluster.local  # should return 301 redirect to HTTPS
curl -I -k https://test.cluster.local  # should return 200 OK
curl -s -k https://test.cluster.local | grep "Test Environment"
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local </dev/null 2>/dev/null | openssl x509 -noout -subject

# Site: ci.cluster.local
curl -I http://ci.cluster.local  # should return 301 redirect to HTTPS
curl -I -k https://ci.cluster.local  # should return 200 OK
curl -s -k https://ci.cluster.local | grep "CI Environment"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local </dev/null 2>/dev/null | openssl x509 -noout -subject

# Site: status.cluster.local
curl -I http://status.cluster.local  # should return 301 redirect to HTTPS
curl -I -k https://status.cluster.local  # should return 200 OK
curl -s -k https://status.cluster.local | grep "Status Environment"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local </dev/null 2>/dev/null | openssl x509 -noout -subject

# SSL certificate validation - check each certificate
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|Signature Algorithm'
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|Signature Algorithm'
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|Signature Algorithm'

# Private key validation - check permissions and ownership
ls -la /etc/ssl/private/test.cluster.local.key  # should show 640 root:ssl-cert
ls -la /etc/ssl/private/ci.cluster.local.key  # should show 640 root:ssl-cert
ls -la /etc/ssl/private/status.cluster.local.key  # should show 640 root:ssl-cert

# Security configuration validation
fail2ban-client status
fail2ban-client status nginx-http-auth
ufw status verbose  # should show active with SSH, HTTP, HTTPS allowed
cat /etc/fail2ban/jail.local | grep -E 'enabled|bantime|findtime|maxretry'
sysctl -a | grep -E 'net.ipv4.conf.all.accept_redirects|net.ipv4.conf.all.send_redirects|net.ipv4.tcp_syncookies'

# SSH security validation
grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# Document root validation
ls -la /opt/server/test/index.html  # should exist with proper content
ls -la /opt/server/ci/index.html  # should exist with proper content
ls -la /opt/server/status/index.html  # should exist with proper content
cat /opt/server/test/index.html | grep "test.cluster.local"
cat /opt/server/ci/index.html | grep "ci.cluster.local"
cat /opt/server/status/index.html | grep "status.cluster.local"

# Nginx site configuration validation
ls -la /etc/nginx/sites-available/  # should show 3 site configs
ls -la /etc/nginx/sites-enabled/  # should show 3 symlinks, no default
test -L /etc/nginx/sites-enabled/test.cluster.local && echo "test.cluster.local enabled"
test -L /etc/nginx/sites-enabled/ci.cluster.local && echo "ci.cluster.local enabled"
test -L /etc/nginx/sites-enabled/status.cluster.local && echo "status.cluster.local enabled"
test ! -f /etc/nginx/sites-enabled/default && echo "default site removed"

# Security headers validation - check each site
curl -I -k https://test.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'
curl -I -k https://ci.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'
curl -I -k https://status.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'

# Network listening validation
netstat -tulpn | grep :80  # should show nginx listening
netstat -tulpn | grep :443  # should show nginx listening
ss -tlnp | grep nginx
lsof -i :80
lsof -i :443

# Process validation
ps aux | grep "nginx: master"  # should show 1 master process
ps aux | grep "nginx: worker"  # should show worker processes
pgrep nginx | wc -l  # should show multiple nginx processes
```