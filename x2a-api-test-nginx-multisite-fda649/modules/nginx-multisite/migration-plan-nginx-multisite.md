---
source-path: cookbooks/nginx-multisite
---

# Migration Plan: nginx-multisite

**TLDR**: Multi-site nginx web server with SSL-enabled virtual hosts for 3 subdomains (test.cluster.local, ci.cluster.local, status.cluster.local), includes comprehensive security hardening with fail2ban, UFW firewall, SSH hardening, and self-signed SSL certificates.

## Service Type and Instances

**Service Type**: Web Server

**Configured Instances**:
- **test.cluster.local**: Testing and development environment
  - Location/Path: /opt/server/test
  - Port/Socket: 80 (redirects to 443), 443 (SSL)
  - Key Config: SSL enabled, self-signed certificate, security headers, gzip compression

- **ci.cluster.local**: Continuous integration environment  
  - Location/Path: /opt/server/ci
  - Port/Socket: 80 (redirects to 443), 443 (SSL)
  - Key Config: SSL enabled, self-signed certificate, security headers, gzip compression

- **status.cluster.local**: Status monitoring environment
  - Location/Path: /opt/server/status
  - Port/Socket: 80 (redirects to 443), 443 (SSL)
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

1. **default** (`cookbooks/nginx-multisite/recipes/default.rb`):
   - Orchestrates the complete nginx multisite setup
   - Includes recipes in dependency order: security → nginx → ssl → sites
   - Resources: include_recipe (4)

2. **security** (`cookbooks/nginx-multisite/recipes/security.rb`):
   - Installs security packages: fail2ban, ufw
   - Configures fail2ban with custom jail settings for SSH and nginx protection
   - Sets up UFW firewall with default deny policy, allows SSH (22), HTTP (80), HTTPS (443)
   - Deploys kernel security parameters via sysctl
   - Conditionally hardens SSH: disables root login and password authentication
   - Resources: package (1), service (2), template (2), execute (6)
   - Templates:
     - fail2ban.jail.local.erb → /etc/fail2ban/jail.local
     - sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf

3. **nginx** (`cookbooks/nginx-multisite/recipes/nginx.rb`):
   - Installs nginx web server package
   - Deploys main nginx configuration with optimized settings
   - Deploys security configuration with hardened headers and SSL settings
   - Enables and starts nginx service
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Creates document root directory for each site
     - Deploys static index.html file for each site
   - Resources: package (1), template (2), service (1), directory (3), cookbook_file (3)
   - Templates:
     - nginx.conf.erb → /etc/nginx/nginx.conf
     - security.conf.erb → /etc/nginx/conf.d/security.conf

4. **ssl** (`cookbooks/nginx-multisite/recipes/ssl.rb`):
   - Installs SSL packages: openssl, ca-certificates
   - Creates ssl-cert group for certificate management
   - Creates SSL certificate and private key directories
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Generates self-signed SSL certificate for each site (365 days validity)
     - Sets proper permissions: private keys 640 root:ssl-cert
     - Certificate subject: /C=US/ST=Example/L=Example/O=Example Org/OU=IT/CN={site_name}/emailAddress=admin@example.com
   - Resources: package (1), group (1), directory (2), execute (3)

5. **sites** (`cookbooks/nginx-multisite/recipes/sites.rb`):
   - Iterations: Runs 3 times for sites: **test.cluster.local**, **ci.cluster.local**, **status.cluster.local**
     - Deploys nginx virtual host configuration for each site
     - Creates symlink to enable each site
     - Configures HTTP to HTTPS redirect, SSL settings, security headers, gzip compression
   - Removes default nginx site configuration
   - Resources: template (3), link (3), file (1)
   - Templates:
     - site.conf.erb → /etc/nginx/sites-available/{site_name} (renders 3 times)

## Dependencies

**External cookbook dependencies**: None
**System package dependencies**: nginx, fail2ban, ufw, openssl, ca-certificates
**Service dependencies**: nginx, fail2ban, ssh

## Credentials

**Detection Summary**: No credentials detected across all files

**Source**:
  - **Provider**: None detected
  - **URL**: N/A
  - **Path**: N/A

No credentials or secrets were detected in this cookbook. All configuration values appear to be non-sensitive. SSL certificates are self-signed and generated locally.

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
- Unix sockets: None

**Templates rendered**:
- fail2ban.jail.local.erb → /etc/fail2ban/jail.local (renders 1 time)
- nginx.conf.erb → /etc/nginx/nginx.conf (renders 1 time)
- security.conf.erb → /etc/nginx/conf.d/security.conf (renders 1 time)
- sysctl-security.conf.erb → /etc/sysctl.d/99-security.conf (renders 1 time)
- site.conf.erb → /etc/nginx/sites-available/{site_name} (renders 3 times)

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
openssl s_client -connect test.cluster.local:443 -servername test.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject
ls -la /opt/server/test/index.html
cat /etc/nginx/sites-available/test.cluster.local | grep -E 'server_name|document_root|ssl_certificate'

# Site-specific checks - ci.cluster.local
curl -I http://ci.cluster.local
curl -I https://ci.cluster.local
curl -s https://ci.cluster.local | grep -i "ci\|continuous"
openssl s_client -connect ci.cluster.local:443 -servername ci.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject
ls -la /opt/server/ci/index.html
cat /etc/nginx/sites-available/ci.cluster.local | grep -E 'server_name|document_root|ssl_certificate'

# Site-specific checks - status.cluster.local
curl -I http://status.cluster.local
curl -I https://status.cluster.local
curl -s https://status.cluster.local | grep -i "status\|monitoring"
openssl s_client -connect status.cluster.local:443 -servername status.cluster.local < /dev/null 2>/dev/null | openssl x509 -noout -subject
ls -la /opt/server/status/index.html
cat /etc/nginx/sites-available/status.cluster.local | grep -E 'server_name|document_root|ssl_certificate'

# SSL certificate validation - test.cluster.local
openssl x509 -in /etc/ssl/certs/test.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN=test.cluster.local'
ls -la /etc/ssl/private/test.cluster.local.key
openssl rsa -in /etc/ssl/private/test.cluster.local.key -check -noout

# SSL certificate validation - ci.cluster.local
openssl x509 -in /etc/ssl/certs/ci.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN=ci.cluster.local'
ls -la /etc/ssl/private/ci.cluster.local.key
openssl rsa -in /etc/ssl/private/ci.cluster.local.key -check -noout

# SSL certificate validation - status.cluster.local
openssl x509 -in /etc/ssl/certs/status.cluster.local.crt -noout -text | grep -E 'Subject:|Not After:|CN=status.cluster.local'
ls -la /etc/ssl/private/status.cluster.local.key
openssl rsa -in /etc/ssl/private/status.cluster.local.key -check -noout

# Security configuration validation
cat /etc/fail2ban/jail.local | grep -E 'enabled = true|bantime|maxretry'
fail2ban-client status
fail2ban-client status sshd
fail2ban-client status nginx-http-auth
ufw status verbose
grep -E 'PermitRootLogin|PasswordAuthentication' /etc/ssh/sshd_config
sysctl -a | grep -f /etc/sysctl.d/99-security.conf

# Network listening
netstat -tulpn | grep -E ':80|:443|:22'
ss -tlnp | grep nginx
lsof -i :80
lsof -i :443

# Security headers validation - test.cluster.local
curl -I https://test.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'

# Security headers validation - ci.cluster.local
curl -I https://ci.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'

# Security headers validation - status.cluster.local
curl -I https://status.cluster.local | grep -E 'Strict-Transport-Security|X-Frame-Options|X-Content-Type-Options|X-XSS-Protection'
```