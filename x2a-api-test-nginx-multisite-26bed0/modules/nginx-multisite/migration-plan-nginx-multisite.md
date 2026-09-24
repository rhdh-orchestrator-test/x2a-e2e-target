---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Multi-site nginx web server cookbook that configures 3 SSL-enabled virtual hosts (test.cluster.local, ci.cluster.local, status.cluster.local) with comprehensive security hardening including fail2ban, UFW firewall, SSH hardening, and kernel security parameters.

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

**IMPORTANT: Use FULL paths from the File Structure section (e.g., `cookbooks/nginx-multisite/recipes/default.rb` not just `recipes/default.rb`)**

1. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs security packages: fail2ban, ufw
   - Configures fail2ban service with custom jail configuration
     - Template: fail2ban.jail.local.erb → /etc/fail2ban/jail.local
   - Sets up UFW firewall rules: deny default, allow SSH/HTTP/HTTPS
   - Deploys kernel security parameters via sysctl
     - Template: sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf
   - Hardens SSH configuration (conditionally):
     - Disables root login if node['security']['ssh']['disable_root'] = true
     - Disables password authentication if node['security']['ssh']['password_auth'] = false
   - Resources: package (1), service (1), template (2), execute (6), service (1)

2. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx package
   - Deploys main nginx configuration
     - Template: nginx.conf.erb → /etc/nginx/nginx.conf
   - Deploys security configuration for nginx
     - Template: security.conf.erb → /etc/nginx/conf.d/security.conf
   - Enables and starts nginx service
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Creates document root directory for each site
     - Deploys static index.html file for each site
       - test.cluster.local: files/default/test/index.html → /opt/server/test/index.html
       - ci.cluster.local: files/default/ci/index.html → /opt/server/ci/index.html
       - status.cluster.local: files/default/status/index.html → /opt/server/status/index.html
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)

3. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group for certificate management
   - Creates SSL certificate and private key directories: /etc/ssl/certs, /etc/ssl/private
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Generates self-signed SSL certificate for each site using OpenSSL
     - Certificate details: RSA 2048-bit, 365 days validity, CN=site_name
     - Sets proper permissions: 640 for private keys, root:ssl-cert ownership
   - Resources: package (1), group (1), directory (2), execute (3)

4. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Deploys nginx virtual host configuration for each site
       - Template: site.conf.erb → /etc/nginx/sites-available/[site_name]
       - Variables: server_name, document_root, ssl_enabled, cert_file, key_file
     - Creates symbolic link to enable each site
       - Link: /etc/nginx/sites-available/[site_name] → /etc/nginx/sites-enabled/[site_name]
   - Removes default nginx site configuration
   - Resources: template (3), link (3), file (1)

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

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. SSL certificates are generated as self-signed certificates with hardcoded organizational details for demonstration purposes.

## Checks for the Migration

**Files to verify**:
- /etc/nginx/nginx.conf (main nginx configuration)
- /etc/nginx/conf.d/security.conf (nginx security settings)
- /etc/nginx/sites-available/test.cluster.local (test site config)
- /etc/nginx/sites-available/ci.cluster.local (CI site config)
- /etc/nginx/sites-available/status.cluster.local (status site config)
- /etc/nginx/sites-enabled/test.cluster.local (test site enabled)
- /etc/nginx/sites-enabled/ci.cluster.local (CI site enabled)
- /etc/nginx/sites-enabled/status.cluster.local (status site enabled)
- /opt/server/test/index.html (test site content)
- /opt/server/ci/index.html (CI site content)
- /opt/server/status/index.html (status site content)
- /etc/ssl/certs/test.cluster.local.crt (test SSL certificate)
- /etc/ssl/certs/ci.cluster.local.crt (CI SSL certificate)
- /etc/ssl/certs/status.cluster.local.crt (status SSL certificate)
- /etc/ssl/private/test.cluster.local.key (test SSL private key)
- /etc/ssl/private/ci.cluster.local.key (CI SSL private key)
- /etc/ssl/private/status.cluster.local.key (status SSL private key)
- /etc/fail2ban/jail.local (fail2ban configuration)
- /etc/sysctl.d/99-security.conf (kernel security parameters)

**Service endpoints to check**:
- Ports listening: 80 (HTTP), 443 (HTTPS), 22 (SSH)
- Unix sockets: None
- Network interfaces: Binds to all interfaces (0.0.0.0)

**Templates rendered**:
- fail2ban.jail.local.erb → /etc/fail2ban/jail.local (1 time)
- nginx.conf.erb → /etc/nginx/nginx.conf (1 time)
- security.conf.erb → /etc/nginx/conf.d/security.conf (1 time)
- sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf (1 time)
- site.conf.erb → /etc/nginx/sites-available/[site_name] (3 times, once per site)

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
curl -k -I https://test.cluster.local
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject -dates
ls -la /opt/server/test/index.html
cat /etc/nginx/sites-available/test.cluster.local | grep -E 'server_name|root|ssl_certificate'

# Site-specific checks - ci.cluster.local
curl -I http://ci.cluster.local
curl -I https://ci.cluster.local
curl -k -I https://ci.cluster.local
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject -dates
ls -la /opt/server/ci/index.html
cat /etc/nginx/sites-available/ci.cluster.local | grep -E 'server_name|root|ssl_certificate'

# Site-specific checks - status.cluster.local
curl -I http://status.cluster.local
curl -I https://status.cluster.local
curl -k -I https://status.cluster.local
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject -dates
ls -la /opt/server/status/index.html
cat /etc/nginx/sites-available/status.cluster.local | grep -E 'server_name|root|ssl_certificate'

# SSL certificate verification
ls -la /etc/ssl/certs/test.cluster.local.crt /etc/ssl/certs/ci.cluster.local.crt /etc/ssl/certs/status.cluster.local.crt
ls -la /etc/ssl/private/test.cluster.local.key /etc/ssl/private/ci.cluster.local.key /etc/ssl/private/status.cluster.local.key
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Not Before:|Not After:'
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Not Before:|Not After:'
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Not Before:|Not After:'

# Security configuration validation
fail2ban-client status
ufw status verbose
cat /etc/fail2ban/jail.local | grep -E 'enabled|bantime|findtime|maxretry'
cat /etc/sysctl.d/99-security.conf
sysctl -a | grep -E 'net.ipv4.ip_forward|net.ipv4.conf.all.accept_redirects'

# SSH hardening verification
grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config
sshd -T | grep -E 'permitrootlogin|passwordauthentication'

# Network listening verification
netstat -tulpn | grep -E ':80|:443|:22'
ss -tlnp | grep nginx
lsof -i :80
lsof -i :443

# Content verification
curl -k https://test.cluster.local | grep "Test Environment"
curl -k https://ci.cluster.local | grep -i "ci\|continuous"
curl -k https://status.cluster.local | grep -i "status\|monitoring"

# Security headers verification
curl -k -I https://test.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options'
curl -k -I https://ci.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options'
curl -k -I https://status.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options'

# HTTP to HTTPS redirect verification
curl -I http://test.cluster.local | grep "301\|Location: https"
curl -I http://ci.cluster.local | grep "301\|Location: https"
curl -I http://status.cluster.local | grep "301\|Location: https"

# File permissions verification
ls -la /etc/ssl/private/ | grep -E 'test.cluster.local.key|ci.cluster.local.key|status.cluster.local.key'
ls -la /etc/ssl/certs/ | grep -E 'test.cluster.local.crt|ci.cluster.local.crt|status.cluster.local.crt'
ls -la /opt/server/test/ /opt/server/ci/ /opt/server/status/
```